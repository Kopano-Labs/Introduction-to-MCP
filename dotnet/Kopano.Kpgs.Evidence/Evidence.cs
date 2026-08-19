using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Kopano.Kpgs.Contracts;

namespace Kopano.Kpgs.Evidence;

public sealed record AdapterEvidence(
    string Schema,
    string EstateProperty,
    string TaskId,
    string CorrelationId,
    string Kind,
    string EvidenceRef,
    string PayloadDigest,
    DateTimeOffset CreatedAt,
    string AuthorityEffect = "none");

public interface IKpgsEvidenceSink
{
    ValueTask EmitAsync(AdapterEvidence evidence, CancellationToken cancellationToken = default);
}

public sealed class InMemoryEvidenceSink : IKpgsEvidenceSink
{
    private readonly List<AdapterEvidence> _items = [];
    public IReadOnlyList<AdapterEvidence> Items => _items;

    public ValueTask EmitAsync(AdapterEvidence evidence, CancellationToken cancellationToken = default)
    {
        _items.Add(evidence);
        return ValueTask.CompletedTask;
    }
}

public static class EvidenceFactory
{
    public static AdapterEvidence Create(HubContext context, string kind, string evidenceRef, object payload)
    {
        if (string.IsNullOrWhiteSpace(evidenceRef) || !evidenceRef.Contains("://", StringComparison.Ordinal))
            throw new ArgumentException("Evidence references must be governed URIs.", nameof(evidenceRef));

        var json = JsonSerializer.Serialize(payload);
        var digest = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json))).ToLowerInvariant();
        return new AdapterEvidence(
            "kpgs.dotnet-adapter-evidence.v1",
            context.EstateProperty,
            context.TaskId,
            context.CorrelationId,
            kind,
            evidenceRef,
            digest,
            DateTimeOffset.UtcNow);
    }
}
