using System.Collections.Concurrent;
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
    private readonly ConcurrentDictionary<string, GovernedTaskSnapshot> _idempotentResults = new(StringComparer.Ordinal);
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
        if (_idempotentResults.TryGetValue(request.IdempotencyKey, out var replay)) return replay;
        var lease = await RequireLeaseAsync(context, new CapabilityRequest("task.create", $"task:{request.TaskId}", request.IdempotencyKey), cancellationToken);
        // Non-idempotent business execution is never transparently retried here. The
        // caller-supplied key and Hub remain the durable replay authority.
        var result = await hub.CreateTaskAsync(context, request, lease, cancellationToken);
        _idempotentResults.TryAdd(request.IdempotencyKey, result);
        await evidence.EmitAsync(EvidenceFactory.Create(context, "task-created", $"kpgs://task/{request.TaskId}", result), cancellationToken);
        return result;
    }

    public async Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, CancellationToken cancellationToken = default)
    {
        if (_idempotentResults.TryGetValue(command.IdempotencyKey, out var replay)) return replay;
        var lease = await RequireLeaseAsync(context, new CapabilityRequest($"task.command.{command.Name}", $"task:{context.TaskId}", command.IdempotencyKey), cancellationToken);
        var result = await hub.ExecuteCommandAsync(context, command, lease, cancellationToken);
        _idempotentResults.TryAdd(command.IdempotencyKey, result);
        await evidence.EmitAsync(EvidenceFactory.Create(context, "task-command", $"kpgs://command/{command.CommandId}", result), cancellationToken);
        return result;
    }

    public Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken = default) =>
        _resilience.ExecuteSafeAsync(ct => hub.GetSessionAsync(context, ct), cancellationToken);

    public Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken = default) =>
        _resilience.ExecuteSafeAsync(ct => hub.GetEvidenceAsync(context, ct), cancellationToken);

    private async Task<string> RequireLeaseAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken)
    {
        var decision = await _resilience.ExecuteSafeAsync(ct => hub.RequestCapabilityAsync(context, request, ct), cancellationToken);
        if (!decision.Allowed || string.IsNullOrWhiteSpace(decision.LeaseToken))
            throw new CapabilityDeniedException(decision.UserSafeReason);
        return decision.LeaseToken;
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
        });
        endpoints.MapPost("/kpgs/tasks/{id}/commands", async (HttpContext http, GovernedCommand command, CancellationToken ct) =>
        {
            try { return Results.Ok(await adapter.ExecuteCommandAsync(contextFactory(http), command, ct)); }
            catch (CapabilityDeniedException ex) { return Results.Json(new { error = ex.Message }, statusCode: StatusCodes.Status403Forbidden); }
        });
        return endpoints;
    }
}
