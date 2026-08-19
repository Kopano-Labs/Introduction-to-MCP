using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace Kopano.Kpgs.Adapter;

public sealed record KpgsAdapterOptions(
    DomainManifest Manifest,
    TimeSpan RequestTimeout,
    int SafeRetryCount,
    int CircuitFailureThreshold);

public interface IKpgsSecretProvider
{
    ValueTask<string?> ResolveReferenceAsync(string reference, CancellationToken cancellationToken = default);
}

public interface IKpgsHubClient
{
    Task<bool> RegisterAsync(DomainManifest manifest, CancellationToken cancellationToken);
    Task<bool> IsReadyAsync(CancellationToken cancellationToken);
    Task<CapabilityDecision> RequestCapabilityAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken);
    Task<GovernedTaskSnapshot> CreateTaskAsync(HubContext context, GovernedTaskRequest request, string leaseToken, CancellationToken cancellationToken);
    Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, string leaseToken, CancellationToken cancellationToken);
    Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken);
    Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken);
}

public sealed class CapabilityDeniedException(string message) : InvalidOperationException(message);
public sealed class KpgsIdempotencyConflictException(string message) : InvalidOperationException(message);

public sealed class KpgsResiliencePolicy(KpgsAdapterOptions options)
{
    private int _failures;
    private DateTimeOffset? _openedAt;

    public async Task<T> ExecuteSafeAsync<T>(Func<CancellationToken, Task<T>> action, CancellationToken cancellationToken)
    {
        if (_openedAt is not null && DateTimeOffset.UtcNow - _openedAt < options.RequestTimeout)
            throw new InvalidOperationException("KPGS adapter circuit is open.");

        Exception? last = null;
        for (var attempt = 0; attempt <= options.SafeRetryCount; attempt++)
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            timeout.CancelAfter(options.RequestTimeout);
            try
            {
                var result = await action(timeout.Token);
                _failures = 0;
                _openedAt = null;
                return result;
            }
            catch (Exception ex) when (ex is not OperationCanceledException || !cancellationToken.IsCancellationRequested)
            {
                last = ex;
                _failures++;
                if (_failures >= options.CircuitFailureThreshold) _openedAt = DateTimeOffset.UtcNow;
                if (attempt == options.SafeRetryCount) break;
            }
        }
        throw last ?? new InvalidOperationException("KPGS safe operation failed.");
    }
}

public sealed class KpgsDomainAdapter(
    KpgsAdapterOptions options,
    IKpgsHubClient hub,
    IKpgsEvidenceSink evidence)
{
    private sealed record IdempotencyEntry(
        string Fingerprint,
        Lazy<Task<GovernedTaskSnapshot>> Operation);

    private readonly ConcurrentDictionary<string, IdempotencyEntry> _idempotentResults = new(StringComparer.Ordinal);
    private readonly KpgsResiliencePolicy _resilience = new(options);

    public DomainManifest Manifest => options.Manifest;

    public async Task<AdapterHealth> HealthAsync(CancellationToken cancellationToken = default)
    {
        var ready = await _resilience.ExecuteSafeAsync(hub.IsReadyAsync, cancellationToken);
        return new AdapterHealth(true, ready, ready ? "ready" : "unavailable", KpgsProtocol.Current, DateTimeOffset.UtcNow);
    }

    public AdapterVersionInfo Version(string requestedProtocol = KpgsProtocol.Current) =>
        new(options.Manifest.AdapterId, options.Manifest.AdapterVersion, KpgsProtocol.Current, KpgsProtocol.IsCompatible(requestedProtocol));

    public async Task RegisterAsync(CancellationToken cancellationToken = default)
    {
        if (!KpgsProtocol.IsCompatible(options.Manifest.ProtocolVersion))
            throw new InvalidOperationException("Domain manifest protocol is incompatible with this adapter.");
        var registered = await _resilience.ExecuteSafeAsync(ct => hub.RegisterAsync(options.Manifest, ct), cancellationToken);
        if (!registered) throw new InvalidOperationException("Sovereign Hub rejected domain registration.");
    }

    public async Task<GovernedTaskSnapshot> CreateTaskAsync(HubContext context, GovernedTaskRequest request, CancellationToken cancellationToken = default)
    {
        ValidateCreateBoundary(request);

        // Replays do not bypass authorization: every privileged invocation resolves
        // a current Hub decision before it may reuse or execute governed work.
        var lease = await RequireLeaseAsync(
            context,
            new CapabilityRequest("task.create", $"task:{request.TaskId}", request.IdempotencyKey),
            cancellationToken);

        var scopedKey = $"create:{context.TenantId}:{context.DomainId}:{request.TaskId}:{request.IdempotencyKey}";
        var fingerprint = Fingerprint(new
        {
            context.TenantId,
            context.DomainId,
            request.TaskId,
            request.CorrelationId,
            request.GoverningSpecRef,
            request.Input,
            request.BoundaryMarker,
            request.CrudIntent,
        });

        return await ExecuteOnceAsync(
            scopedKey,
            fingerprint,
            async () =>
            {
                // Non-idempotent business execution is never transparently retried here.
                // The caller key + this collision membrane + Hub/domain state form the replay boundary.
                var result = await hub.CreateTaskAsync(context, request, lease, cancellationToken);
                await evidence.EmitAsync(
                    EvidenceFactory.Create(context, "task-created", $"kpgs://task/{request.TaskId}", result),
                    cancellationToken);
                return result;
            });
    }

    public async Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, CancellationToken cancellationToken = default)
    {
        ValidateCommandBoundary(command);

        var lease = await RequireLeaseAsync(
            context,
            new CapabilityRequest($"task.command.{command.Name}", $"task:{context.TaskId}", command.IdempotencyKey),
            cancellationToken);

        var scopedKey = $"command:{context.TenantId}:{context.DomainId}:{context.TaskId}:{command.IdempotencyKey}";
        var fingerprint = Fingerprint(new
        {
            context.TenantId,
            context.DomainId,
            context.TaskId,
            command.CommandId,
            command.Name,
            command.Payload,
            command.CorrelationId,
            command.BoundaryMarker,
        });

        return await ExecuteOnceAsync(
            scopedKey,
            fingerprint,
            async () =>
            {
                var result = await hub.ExecuteCommandAsync(context, command, lease, cancellationToken);
                await evidence.EmitAsync(
                    EvidenceFactory.Create(context, "task-command", $"kpgs://command/{command.CommandId}", result),
                    cancellationToken);
                return result;
            });
    }

    public Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken = default) =>
        _resilience.ExecuteSafeAsync(ct => hub.GetSessionAsync(context, ct), cancellationToken);

    public Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken = default) =>
        _resilience.ExecuteSafeAsync(ct => hub.GetEvidenceAsync(context, ct), cancellationToken);

    private async Task<string> RequireLeaseAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken)
    {
        var decision = await _resilience.ExecuteSafeAsync(ct => hub.RequestCapabilityAsync(context, request, ct), cancellationToken);
        if (!decision.Allowed ||
            string.IsNullOrWhiteSpace(decision.LeaseToken) ||
            decision.ExpiresAt is null ||
            decision.ExpiresAt <= DateTimeOffset.UtcNow)
        {
            throw new CapabilityDeniedException(
                string.IsNullOrWhiteSpace(decision.UserSafeReason)
                    ? "Capability lease is missing, denied, or expired."
                    : decision.UserSafeReason);
        }
        return decision.LeaseToken;
    }

    private async Task<GovernedTaskSnapshot> ExecuteOnceAsync(
        string scopedKey,
        string fingerprint,
        Func<Task<GovernedTaskSnapshot>> action)
    {
        while (true)
        {
            if (_idempotentResults.TryGetValue(scopedKey, out var existing))
            {
                if (!string.Equals(existing.Fingerprint, fingerprint, StringComparison.Ordinal))
                {
                    throw new KpgsIdempotencyConflictException(
                        "Idempotency key is already bound to different governed content.");
                }
                return await existing.Operation.Value;
            }

            var candidate = new IdempotencyEntry(
                fingerprint,
                new Lazy<Task<GovernedTaskSnapshot>>(
                    action,
                    LazyThreadSafetyMode.ExecutionAndPublication));

            if (!_idempotentResults.TryAdd(scopedKey, candidate)) continue;

            try
            {
                return await candidate.Operation.Value;
            }
            catch
            {
                _idempotentResults.TryRemove(scopedKey, out _);
                throw;
            }
        }
    }

    private static void ValidateCreateBoundary(GovernedTaskRequest request)
    {
        if (!string.Equals(request.BoundaryMarker, KpgsProtocol.BoundaryMarker, StringComparison.Ordinal))
            throw new InvalidOperationException("Literal #NB boundary is required before governed task CREATE.");
        if (!string.Equals(request.CrudIntent, "CREATE", StringComparison.Ordinal))
            throw new InvalidOperationException("The reference task mutation is bounded to CRUD CREATE.");
    }

    private static void ValidateCommandBoundary(GovernedCommand command)
    {
        if (!string.Equals(command.BoundaryMarker, KpgsProtocol.BoundaryMarker, StringComparison.Ordinal))
            throw new InvalidOperationException("Literal #NB boundary is required before governed task command mutation.");
    }

    private static string Fingerprint(object value)
    {
        var json = JsonSerializer.Serialize(value);
        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json))).ToLowerInvariant();
    }
}

public static class KpgsAdapterEndpointExtensions
{
    public static IEndpointRouteBuilder MapKpgsAdapter(this IEndpointRouteBuilder endpoints, KpgsDomainAdapter adapter, Func<HttpContext, HubContext> contextFactory)
    {
        endpoints.MapGet("/kpgs/health", async (CancellationToken ct) => Results.Ok(await adapter.HealthAsync(ct)));
        endpoints.MapGet("/kpgs/version", (string? protocol) => Results.Ok(adapter.Version(protocol ?? KpgsProtocol.Current)));
        endpoints.MapGet("/kpgs/session/{id}", async (HttpContext http, CancellationToken ct) =>
            Results.Ok(await adapter.GetSessionAsync(contextFactory(http), ct)));
        endpoints.MapGet("/kpgs/tasks/{id}/evidence", async (HttpContext http, CancellationToken ct) =>
            Results.Ok(await adapter.GetEvidenceAsync(contextFactory(http), ct)));
        endpoints.MapPost("/kpgs/tasks", async (HttpContext http, GovernedTaskRequest request, CancellationToken ct) =>
        {
            try { return Results.Ok(await adapter.CreateTaskAsync(contextFactory(http), request, ct)); }
            catch (CapabilityDeniedException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status403Forbidden); }
            catch (KpgsIdempotencyConflictException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status409Conflict); }
            catch (InvalidOperationException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status422UnprocessableEntity); }
        });
        endpoints.MapPost("/kpgs/tasks/{id}/commands", async (HttpContext http, GovernedCommand command, CancellationToken ct) =>
        {
            try { return Results.Ok(await adapter.ExecuteCommandAsync(contextFactory(http), command, ct)); }
            catch (CapabilityDeniedException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status403Forbidden); }
            catch (KpgsIdempotencyConflictException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status409Conflict); }
            catch (InvalidOperationException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status422UnprocessableEntity); }
        });
        return endpoints;
    }
}
