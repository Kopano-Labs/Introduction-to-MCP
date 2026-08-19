using System.Collections.Concurrent;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;

namespace Kopano.Kpgs.Adapter;

public sealed class KpgsAdapterOptions
{
    public string EstateProperty { get; set; } = "unconfigured";
    public string AdapterVersion { get; set; } = "0.1.0";
    public string ProtocolVersion { get; set; } = KpgsProtocol.Version;
    public TimeSpan RequestTimeout { get; set; } = TimeSpan.FromSeconds(8);
    public int SafeRetryCount { get; set; } = 2;
    public int CircuitFailureThreshold { get; set; } = 3;
    public TimeSpan CircuitBreakDuration { get; set; } = TimeSpan.FromSeconds(20);
}

public sealed record DomainRegistration(
    string EstateProperty,
    string DomainId,
    Uri PublicBaseUri,
    string ProtocolVersion);

public interface IKpgsSecretProvider
{
    ValueTask<string?> GetSecretAsync(string reference, CancellationToken cancellationToken = default);
}

public interface IKpgsIdentityTranslator
{
    ValueTask<KpgsIdentityContext> TranslateAsync(HttpContext context, CancellationToken cancellationToken = default);
}

public interface IKpgsHubClient : ICanonicalSessionReader
{
    Task<bool> IsReadyAsync(CancellationToken cancellationToken = default);
    Task RegisterDomainAsync(DomainRegistration registration, CapabilityDecision decision, CancellationToken cancellationToken = default);
    Task<CapabilityDecision> ResolveCapabilityAsync(KpgsIdentityContext identity, CapabilityRequest request, CancellationToken cancellationToken = default);
    Task<TaskSnapshot> CreateTaskAsync(TaskCreateRequest request, KpgsIdentityContext identity, CapabilityDecision decision, CancellationToken cancellationToken = default);
    Task<TaskSnapshot> SendCommandAsync(string taskId, TaskCommandRequest request, KpgsIdentityContext identity, CapabilityDecision decision, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<EvidenceRecord>> GetEvidenceAsync(string taskId, KpgsIdentityContext identity, CapabilityDecision decision, CancellationToken cancellationToken = default);
}

public sealed class KpgsAuthorizationException(string message) : InvalidOperationException(message);
public sealed class KpgsIdempotencyConflictException(string message) : InvalidOperationException(message);
public sealed class KpgsHubUnavailableException(string message, Exception? inner = null) : Exception(message, inner);
public sealed class KpgsCircuitOpenException(string message) : Exception(message);

public sealed class InMemoryIdempotencyGate
{
    private sealed record Entry(string Fingerprint, Lazy<Task<object?>> Operation);
    private readonly ConcurrentDictionary<string, Entry> _entries = new(StringComparer.Ordinal);

    public async Task<T> ExecuteOnceAsync<T>(
        string operationKey,
        string fingerprint,
        Func<Task<T>> action)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(operationKey);
        ArgumentException.ThrowIfNullOrWhiteSpace(fingerprint);

        while (true)
        {
            if (_entries.TryGetValue(operationKey, out var existing))
            {
                if (!string.Equals(existing.Fingerprint, fingerprint, StringComparison.Ordinal))
                {
                    throw new KpgsIdempotencyConflictException(
                        "Idempotency key is already bound to different governed content.");
                }

                return (T)(await existing.Operation.Value.ConfigureAwait(false))!;
            }

            var candidate = new Entry(
                fingerprint,
                new Lazy<Task<object?>>(
                    async () => await action().ConfigureAwait(false),
                    LazyThreadSafetyMode.ExecutionAndPublication));

            if (_entries.TryAdd(operationKey, candidate))
            {
                try
                {
                    return (T)(await candidate.Operation.Value.ConfigureAwait(false))!;
                }
                catch
                {
                    _entries.TryRemove(new KeyValuePair<string, Entry>(operationKey, candidate));
                    throw;
                }
            }
        }
    }
}

/// <summary>
/// Small dependency-free resilience membrane. Only callers explicitly marked
/// idempotent are retried. A circuit breaker stops repeated transport pressure.
/// </summary>
public sealed class KpgsHubInvoker
{
    private readonly KpgsAdapterOptions _options;
    private readonly object _circuitLock = new();
    private int _consecutiveFailures;
    private DateTimeOffset? _circuitOpenUntil;

    public KpgsHubInvoker(KpgsAdapterOptions options) => _options = options;

    public async Task<T> ExecuteAsync<T>(
        Func<CancellationToken, Task<T>> operation,
        bool idempotent,
        CancellationToken cancellationToken = default)
    {
        ThrowIfCircuitOpen();
        var attempts = idempotent ? Math.Max(1, _options.SafeRetryCount + 1) : 1;
        Exception? last = null;

        for (var attempt = 1; attempt <= attempts; attempt++)
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            timeout.CancelAfter(_options.RequestTimeout);
            try
            {
                var result = await operation(timeout.Token).ConfigureAwait(false);
                ResetCircuit();
                return result;
            }
            catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
            {
                last = new TimeoutException("KPGS Hub operation exceeded the bounded request timeout.");
            }
            catch (HttpRequestException ex) when (ex.StatusCode is null || (int)ex.StatusCode >= 500)
            {
                last = ex;
            }

            RegisterFailure();
            if (attempt < attempts)
            {
                var delay = TimeSpan.FromMilliseconds(100 * Math.Pow(2, attempt - 1));
                await Task.Delay(delay, cancellationToken).ConfigureAwait(false);
            }
        }

        throw new KpgsHubUnavailableException("KPGS Hub operation failed after bounded retry policy.", last);
    }

    private void ThrowIfCircuitOpen()
    {
        lock (_circuitLock)
        {
            if (_circuitOpenUntil is { } until)
            {
                if (until > DateTimeOffset.UtcNow)
                {
                    throw new KpgsCircuitOpenException("KPGS Hub circuit is temporarily open.");
                }
                _circuitOpenUntil = null;
                _consecutiveFailures = 0;
            }
        }
    }

    private void RegisterFailure()
    {
        lock (_circuitLock)
        {
            _consecutiveFailures++;
            if (_consecutiveFailures >= Math.Max(1, _options.CircuitFailureThreshold))
            {
                _circuitOpenUntil = DateTimeOffset.UtcNow.Add(_options.CircuitBreakDuration);
            }
        }
    }

    private void ResetCircuit()
    {
        lock (_circuitLock)
        {
            _consecutiveFailures = 0;
            _circuitOpenUntil = null;
        }
    }
}

public sealed class KpgsAdapterService : ICanonicalSessionReader
{
    private readonly IKpgsHubClient _hub;
    private readonly IKpgsEvidenceSink _evidence;
    private readonly InMemoryIdempotencyGate _idempotency;
    private readonly KpgsHubInvoker _invoker;
    private readonly KpgsAdapterOptions _options;

    public KpgsAdapterService(
        IKpgsHubClient hub,
        IKpgsEvidenceSink evidence,
        InMemoryIdempotencyGate idempotency,
        KpgsHubInvoker invoker,
        KpgsAdapterOptions options)
    {
        _hub = hub;
        _evidence = evidence;
        _idempotency = idempotency;
        _invoker = invoker;
        _options = options;
    }

    public AdapterVersion GetVersion() =>
        new(
            Adapter: _options.AdapterVersion,
            Protocol: _options.ProtocolVersion,
            TargetFramework: "net10.0",
            CompatibleProtocols: [KpgsProtocol.Version]);

    public async Task<AdapterHealth> GetHealthAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var ready = await _invoker.ExecuteAsync(
                ct => _hub.IsReadyAsync(ct),
                idempotent: true,
                cancellationToken).ConfigureAwait(false);
            return new AdapterHealth(
                ready ? "ready" : "degraded",
                ready,
                _options.ProtocolVersion,
                _options.AdapterVersion,
                DateTimeOffset.UtcNow);
        }
        catch (Exception ex) when (ex is KpgsHubUnavailableException or KpgsCircuitOpenException)
        {
            return new AdapterHealth(
                "degraded",
                false,
                _options.ProtocolVersion,
                _options.AdapterVersion,
                DateTimeOffset.UtcNow);
        }
    }

    public async Task RegisterDomainAsync(
        DomainRegistration registration,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        var decision = await RequireCapabilityAsync(
            identity,
            capability: "domain.register",
            resourceScope: $"estate:{registration.EstateProperty}",
            taskId: $"domain:{registration.DomainId}",
            cancellationToken).ConfigureAwait(false);

        await _invoker.ExecuteAsync(
            async ct =>
            {
                await _hub.RegisterDomainAsync(registration, decision, ct).ConfigureAwait(false);
                return true;
            },
            idempotent: true,
            cancellationToken).ConfigureAwait(false);

        await EmitAsync(identity.CorrelationId, "domain.register", "PASS", registration.DomainId, decision.LeaseId!, cancellationToken).ConfigureAwait(false);
    }

    public async Task<TaskSnapshot> GetSessionSnapshotAsync(
        string sessionId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        var decision = await RequireCapabilityAsync(
            identity,
            "session.read",
            $"session:{sessionId}",
            sessionId,
            cancellationToken).ConfigureAwait(false);

        var snapshot = await _invoker.ExecuteAsync(
            ct => _hub.GetSessionSnapshotAsync(sessionId, identity, ct),
            idempotent: true,
            cancellationToken).ConfigureAwait(false);
        await EmitAsync(identity.CorrelationId, "session.read", "PASS", snapshot.TaskId, decision.LeaseId!, cancellationToken).ConfigureAwait(false);
        return snapshot;
    }

    public async Task<TaskSnapshot> CreateTaskAsync(
        TaskCreateRequest request,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        ValidateProgressiveCreate(request.BoundaryMarker, request.CrudIntent);
        var decision = await RequireCapabilityAsync(
            identity,
            "task.create",
            $"domain:{identity.DomainId}",
            request.UpdateId,
            cancellationToken).ConfigureAwait(false);

        var fingerprint = Fingerprint(new { identity.TenantId, identity.DomainId, request });
        var snapshot = await _idempotency.ExecuteOnceAsync(
            $"task.create:{identity.TenantId}:{request.IdempotencyKey}",
            fingerprint,
            () => _invoker.ExecuteAsync(
                ct => _hub.CreateTaskAsync(request, identity, decision, ct),
                idempotent: true,
                cancellationToken)).ConfigureAwait(false);

        await EmitAsync(identity.CorrelationId, "task.create", "PASS", snapshot.TaskId, decision.LeaseId!, cancellationToken).ConfigureAwait(false);
        return snapshot;
    }

    public async Task<TaskSnapshot> SendCommandAsync(
        string taskId,
        TaskCommandRequest request,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        if (!string.Equals(request.BoundaryMarker, "#NB", StringComparison.Ordinal))
        {
            throw new InvalidOperationException("Literal #NB boundary is required before task command mutation.");
        }

        var decision = await RequireCapabilityAsync(
            identity,
            "task.command",
            $"task:{taskId}",
            taskId,
            cancellationToken).ConfigureAwait(false);

        var fingerprint = Fingerprint(new { identity.TenantId, taskId, request });
        var snapshot = await _idempotency.ExecuteOnceAsync(
            $"task.command:{identity.TenantId}:{taskId}:{request.IdempotencyKey}",
            fingerprint,
            () => _invoker.ExecuteAsync(
                ct => _hub.SendCommandAsync(taskId, request, identity, decision, ct),
                idempotent: true,
                cancellationToken)).ConfigureAwait(false);

        await EmitAsync(identity.CorrelationId, "task.command", "PASS", taskId, decision.LeaseId!, cancellationToken).ConfigureAwait(false);
        return snapshot;
    }

    public async Task<IReadOnlyList<EvidenceRecord>> GetEvidenceAsync(
        string taskId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        var decision = await RequireCapabilityAsync(
            identity,
            "evidence.read",
            $"task:{taskId}",
            taskId,
            cancellationToken).ConfigureAwait(false);

        return await _invoker.ExecuteAsync(
            ct => _hub.GetEvidenceAsync(taskId, identity, decision, ct),
            idempotent: true,
            cancellationToken).ConfigureAwait(false);
    }

    private async Task<CapabilityDecision> RequireCapabilityAsync(
        KpgsIdentityContext identity,
        string capability,
        string resourceScope,
        string taskId,
        CancellationToken cancellationToken)
    {
        CapabilityDecision decision;
        try
        {
            decision = await _invoker.ExecuteAsync(
                ct => _hub.ResolveCapabilityAsync(
                    identity,
                    new CapabilityRequest(capability, resourceScope, taskId, identity.CorrelationId),
                    ct),
                idempotent: true,
                cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is KpgsHubUnavailableException or KpgsCircuitOpenException)
        {
            await EmitAsync(identity.CorrelationId, capability, "HOLD", "policy-unavailable", "no-lease", cancellationToken).ConfigureAwait(false);
            throw new KpgsAuthorizationException("Privileged action held because Hub capability/policy verification is unavailable.");
        }

        if (!decision.IsUsable(DateTimeOffset.UtcNow))
        {
            await EmitAsync(identity.CorrelationId, capability, "REJECT", decision.Reason, decision.LeaseId ?? "no-lease", cancellationToken).ConfigureAwait(false);
            throw new KpgsAuthorizationException($"Capability denied: {capability}.");
        }

        return decision;
    }

    private async Task EmitAsync(
        string correlationId,
        string action,
        string outcome,
        string detail,
        string leaseId,
        CancellationToken cancellationToken) =>
        await _evidence.EmitAsync(
            EvidenceFactory.Create(
                correlationId,
                source: "Kopano.Kpgs.Adapter",
                action,
                outcome,
                detail,
                $"lease:{leaseId}",
                $"estate:{_options.EstateProperty}",
                $"protocol:{_options.ProtocolVersion}"),
            cancellationToken).ConfigureAwait(false);

    private static void ValidateProgressiveCreate(string boundaryMarker, string crudIntent)
    {
        if (!string.Equals(boundaryMarker, "#NB", StringComparison.Ordinal))
        {
            throw new InvalidOperationException("Literal #NB boundary is required before task mutation.");
        }
        if (!string.Equals(crudIntent, "CREATE", StringComparison.Ordinal))
        {
            throw new InvalidOperationException("Reference task pilot is bounded to CREATE.");
        }
    }

    private static string Fingerprint(object value)
    {
        var json = JsonSerializer.Serialize(value);
        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json))).ToLowerInvariant();
    }
}

public static class KpgsAdapterServiceCollectionExtensions
{
    public static IServiceCollection AddKpgsAdapter(
        this IServiceCollection services,
        KpgsAdapterOptions options)
    {
        services.AddSingleton(options);
        services.AddSingleton<InMemoryIdempotencyGate>();
        services.AddSingleton<KpgsHubInvoker>();
        services.AddScoped<KpgsAdapterService>();
        return services;
    }
}

public static class KpgsAdapterEndpointExtensions
{
    public static IEndpointRouteBuilder MapKpgsAdapterEndpoints(this IEndpointRouteBuilder endpoints)
    {
        endpoints.MapGet("/kpgs/health", async (KpgsAdapterService adapter, CancellationToken ct) =>
            Results.Ok(await adapter.GetHealthAsync(ct)));

        endpoints.MapGet("/kpgs/version", (KpgsAdapterService adapter) =>
            Results.Ok(adapter.GetVersion()));

        endpoints.MapGet("/kpgs/session/{id}", async (
            string id,
            HttpContext context,
            IKpgsIdentityTranslator identityTranslator,
            KpgsAdapterService adapter,
            CancellationToken ct) =>
            await ExecuteAsync(async () =>
            {
                var identity = await identityTranslator.TranslateAsync(context, ct);
                return Results.Ok(await adapter.GetSessionSnapshotAsync(id, identity, ct));
            }));

        endpoints.MapPost("/kpgs/tasks", async (
            TaskCreateRequest request,
            HttpContext context,
            IKpgsIdentityTranslator identityTranslator,
            KpgsAdapterService adapter,
            CancellationToken ct) =>
            await ExecuteAsync(async () =>
            {
                var identity = await identityTranslator.TranslateAsync(context, ct);
                return Results.Ok(await adapter.CreateTaskAsync(request, identity, ct));
            }));

        endpoints.MapPost("/kpgs/tasks/{id}/commands", async (
            string id,
            TaskCommandRequest request,
            HttpContext context,
            IKpgsIdentityTranslator identityTranslator,
            KpgsAdapterService adapter,
            CancellationToken ct) =>
            await ExecuteAsync(async () =>
            {
                var identity = await identityTranslator.TranslateAsync(context, ct);
                return Results.Ok(await adapter.SendCommandAsync(id, request, identity, ct));
            }));

        endpoints.MapGet("/kpgs/tasks/{id}/evidence", async (
            string id,
            HttpContext context,
            IKpgsIdentityTranslator identityTranslator,
            KpgsAdapterService adapter,
            CancellationToken ct) =>
            await ExecuteAsync(async () =>
            {
                var identity = await identityTranslator.TranslateAsync(context, ct);
                return Results.Ok(await adapter.GetEvidenceAsync(id, identity, ct));
            }));

        return endpoints;
    }

    private static async Task<IResult> ExecuteAsync(Func<Task<IResult>> action)
    {
        try
        {
            return await action().ConfigureAwait(false);
        }
        catch (KpgsAuthorizationException ex)
        {
            return Results.Problem(ex.Message, statusCode: StatusCodes.Status403Forbidden);
        }
        catch (KpgsIdempotencyConflictException ex)
        {
            return Results.Problem(ex.Message, statusCode: StatusCodes.Status409Conflict);
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(ex.Message, statusCode: StatusCodes.Status422UnprocessableEntity);
        }
        catch (KpgsHubUnavailableException ex)
        {
            return Results.Problem(ex.Message, statusCode: StatusCodes.Status503ServiceUnavailable);
        }
    }
}
