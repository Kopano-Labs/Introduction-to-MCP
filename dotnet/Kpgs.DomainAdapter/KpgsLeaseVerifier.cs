using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Kpgs.DomainAdapter;

public sealed class LeaseVerificationException(string code, string message)
    : Exception(message)
{
    public string Code { get; } = code;
}

public sealed class KpgsLeaseVerifier
{
    private const string TokenType = "KPGS-LEASE";
    private const string Algorithm = "HS256";
    private readonly IReadOnlyDictionary<string, byte[]> _keys;
    private readonly string _issuer;
    private readonly TimeSpan _maxTtl;
    private readonly Func<DateTimeOffset> _clock;

    public KpgsLeaseVerifier(
        IReadOnlyDictionary<string, byte[]> keys,
        string issuer = "kpgs-sovereign-hub",
        TimeSpan? maxTtl = null,
        Func<DateTimeOffset>? clock = null)
    {
        if (keys.Count == 0)
        {
            throw new ArgumentException("At least one lease verification key is required.", nameof(keys));
        }

        foreach (var pair in keys)
        {
            if (string.IsNullOrWhiteSpace(pair.Key) || pair.Value.Length < 32)
            {
                throw new ArgumentException("Lease keys require a non-empty kid and at least 32 bytes.", nameof(keys));
            }
        }

        _keys = keys;
        _issuer = issuer;
        _maxTtl = maxTtl ?? TimeSpan.FromMinutes(15);
        _clock = clock ?? (() => DateTimeOffset.UtcNow);
    }

    public static KpgsLeaseVerifier FromConfiguration(IConfiguration configuration)
    {
        var issuer = configuration["KPGS:LeaseIssuer"] ?? "kpgs-sovereign-hub";
        var keySection = configuration.GetSection("KPGS:LeaseKeys");
        var keys = new Dictionary<string, byte[]>(StringComparer.Ordinal);

        foreach (var child in keySection.GetChildren())
        {
            if (string.IsNullOrWhiteSpace(child.Value))
            {
                continue;
            }

            try
            {
                keys[child.Key] = Convert.FromBase64String(child.Value);
            }
            catch (FormatException exception)
            {
                throw new InvalidOperationException(
                    $"KPGS lease key '{child.Key}' must be Base64-encoded key bytes.",
                    exception);
            }
        }

        return new KpgsLeaseVerifier(keys, issuer);
    }

    public LeaseDecision Verify(
        string token,
        string tenantId,
        string domainId,
        string taskId,
        string capability,
        string resourceScope)
    {
        if (string.IsNullOrWhiteSpace(token) || token.Length > 32768)
        {
            throw new LeaseVerificationException("lease_invalid", "Capability lease token is invalid.");
        }

        var parts = token.Split('.');
        if (parts.Length != 3)
        {
            throw new LeaseVerificationException("lease_invalid", "Capability lease token must contain three compact segments.");
        }

        LeaseHeader header;
        LeasePayload payload;
        try
        {
            header = JsonSerializer.Deserialize<LeaseHeader>(Decode(parts[0]))
                ?? throw new JsonException("Missing lease header.");
            payload = JsonSerializer.Deserialize<LeasePayload>(Decode(parts[1]))
                ?? throw new JsonException("Missing lease payload.");
        }
        catch (JsonException exception)
        {
            throw new LeaseVerificationException("lease_invalid", $"Capability lease JSON is invalid: {exception.Message}");
        }

        if (header.Alg != Algorithm || header.Typ != TokenType || header.Issuer != _issuer)
        {
            throw new LeaseVerificationException("lease_invalid", "Capability lease header or issuer is not admitted.");
        }

        if (!_keys.TryGetValue(header.Kid, out var key))
        {
            throw new LeaseVerificationException("lease_unknown_key", "Capability lease signing key is unknown.");
        }

        var signingInput = Encoding.ASCII.GetBytes($"{parts[0]}.{parts[1]}");
        var expected = HMACSHA256.HashData(key, signingInput);
        var signature = Decode(parts[2]);
        if (expected.Length != signature.Length || !CryptographicOperations.FixedTimeEquals(expected, signature))
        {
            throw new LeaseVerificationException("lease_signature_invalid", "Capability lease signature verification failed.");
        }

        var now = _clock();
        var ttl = payload.ExpiresAt - payload.IssuedAt;
        if (ttl <= TimeSpan.Zero || ttl > _maxTtl)
        {
            throw new LeaseVerificationException("lease_ttl_invalid", "Capability lease lifetime violates KPGS policy.");
        }

        if (now < payload.IssuedAt)
        {
            throw new LeaseVerificationException("lease_not_active", "Capability lease is not active yet.");
        }

        if (now >= payload.ExpiresAt)
        {
            throw new LeaseVerificationException("lease_expired", "Capability lease expired.");
        }

        if (string.IsNullOrWhiteSpace(payload.LeaseId) || string.IsNullOrWhiteSpace(payload.Nonce))
        {
            throw new LeaseVerificationException("lease_invalid", "Capability lease identity or nonce is missing.");
        }

        if (payload.TenantId != tenantId || payload.DomainId != domainId || payload.TaskId != taskId)
        {
            throw new LeaseVerificationException("lease_scope_denied", "Capability lease tenant/domain/task scope does not match the request.");
        }

        var admitted = payload.Capabilities.Any(item =>
            item.Name == capability && item.ResourceScope == resourceScope);
        if (!admitted)
        {
            throw new LeaseVerificationException("lease_capability_denied", "Capability or resource scope is not admitted by the lease.");
        }

        return new LeaseDecision(
            payload.LeaseId,
            payload.Subject.Id,
            header.Kid,
            capability,
            resourceScope);
    }

    private static byte[] Decode(string value)
    {
        var padded = value.Replace('-', '+').Replace('_', '/');
        padded += new string('=', (4 - padded.Length % 4) % 4);
        try
        {
            return Convert.FromBase64String(padded);
        }
        catch (FormatException exception)
        {
            throw new LeaseVerificationException("lease_invalid", $"Capability lease compact encoding is invalid: {exception.Message}");
        }
    }
}

public sealed class OperationReplayGuard
{
    private readonly HashSet<string> _consumed = new(StringComparer.Ordinal);
    private readonly object _gate = new();

    public bool TryConsume(string leaseId, string operationNonce)
    {
        if (string.IsNullOrWhiteSpace(operationNonce) || operationNonce.Length < 8)
        {
            return false;
        }

        var key = $"{leaseId}\u001f{operationNonce}";
        lock (_gate)
        {
            return _consumed.Add(key);
        }
    }
}
