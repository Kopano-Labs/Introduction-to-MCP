using System.Collections.Concurrent;
using System.Text.Json;
using Kopano.Kpgs.Adapter;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<IKpgsEvidenceSink, InMemoryEvidenceSink>();
builder.Services.AddSingleton<IKpgsHubClient, DevelopmentMockHubClient>();
builder.Services.AddSingleton<IKpgsIdentityTranslator, HeaderIdentityTranslator>();
builder.Services.AddSingleton<IKpgsSecretProvider, EnvironmentSecretProvider>();
builder.Services.AddKpgsAdapter(new KpgsAdapterOptions
{
    EstateProperty = builder.Configuration["KPGS_ESTATE_PROPERTY"] ?? "local.reference",
    AdapterVersion = "0.1.0",
    ProtocolVersion = KpgsProtocol.Version,
});

var app = builder.Build();
app.MapGet("/", () => Results.Ok(new
{
    service = "Kopano.Kpgs.Reference",
    authority = "adapter-only",
    canonical_business_state = false,
    protocol = KpgsProtocol.Name,
}));
app.MapKpgsAdapterEndpoints();
app.Run();

/// <summary>
/// Reference identity translation only. Real domains replace this with their
/// authenticated server-side identity integration; browser headers never grant authority.
/// </summary>
sealed class HeaderIdentityTranslator : IKpgsIdentityTranslator
{
    public ValueTask<KpgsIdentityContext> TranslateAsync(
        HttpContext context,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var subject = context.User.Identity?.Name ?? context.Request.Headers["X-KPGS-Subject"].FirstOrDefault();
        if (string.IsNullOrWhiteSpace(subject))
        {
            throw new KpgsAuthorizationException("Authenticated domain identity is required.");
        }

        string RequiredHeader(string name)
        {
            var value = context.Request.Headers[name].FirstOrDefault();
            if (string.IsNullOrWhiteSpace(value))
            {
                throw new KpgsAuthorizationException($"Missing server-resolved identity context header: {name}.");
            }
            return value;
        }

        return ValueTask.FromResult(new KpgsIdentityContext(
            SubjectId: subject,
            TenantId: RequiredHeader("X-KPGS-Tenant"),
            DomainId: RequiredHeader("X-KPGS-Domain"),
            SessionId: RequiredHeader("X-KPGS-Session"),
            CorrelationId: context.Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString("N")));
    }
}

sealed class EnvironmentSecretProvider : IKpgsSecretProvider
{
    public ValueTask<string?> GetSecretAsync(string reference, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (!reference.StartsWith("env:", StringComparison.Ordinal))
        {
            throw new InvalidOperationException("Reference service accepts only env: secret references.");
        }
        return ValueTask.FromResult(Environment.GetEnvironmentVariable(reference[4..]));
    }
}

/// <summary>
/// Local-development mock only. It demonstrates the adapter contract and is not
/// Sovereign Hub, not a production policy engine, and not a canonical state store.
/// </summary>
sealed class DevelopmentMockHubClient : IKpgsHubClient
{
    private readonly ConcurrentDictionary<string, TaskSnapshot> _tasks = new(StringComparer.Ordinal);

    public Task<bool> IsReadyAsync(CancellationToken cancellationToken = default) => Task.FromResult(true);

    public Task<CapabilityDecision> ResolveCapabilityAsync(
        KpgsIdentityContext identity,
        CapabilityRequest request,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(new CapabilityDecision(
            Allowed: true,
            LeaseId: $"dev-lease-{Guid.NewGuid():N}",
            ExpiresAt: DateTimeOffset.UtcNow.AddMinutes(2),
            PolicyDecisionRef: "development-mock-only",
            Reason: "Local reference mock admitted the declared capability."));

    public Task RegisterDomainAsync(
        DomainRegistration registration,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task<TaskSnapshot> CreateTaskAsync(
        TaskCreateRequest request,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        var taskId = $"dev-task-{Guid.NewGuid():N}";
        var snapshot = new TaskSnapshot(
            taskId,
            "created",
            request.GoverningSpecRef,
            identity.CorrelationId,
            ["inspect", "approve"],
            "Development mock created a non-production task snapshot.",
            ApprovalRequired: true,
            UpdatedAt: DateTimeOffset.UtcNow);
        _tasks[taskId] = snapshot;
        return Task.FromResult(snapshot);
    }

    public Task<TaskSnapshot> SendCommandAsync(
        string taskId,
        TaskCommandRequest request,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        if (!_tasks.TryGetValue(taskId, out var previous))
        {
            throw new KeyNotFoundException(taskId);
        }
        var updated = previous with
        {
            Status = $"command:{request.Command}",
            UserSafeExplanation = "Development mock accepted the command under a short-lived mock lease.",
            UpdatedAt = DateTimeOffset.UtcNow,
        };
        _tasks[taskId] = updated;
        return Task.FromResult(updated);
    }

    public Task<TaskSnapshot> GetSessionSnapshotAsync(
        string sessionId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        var snapshot = _tasks.Values.OrderByDescending(task => task.UpdatedAt).FirstOrDefault()
            ?? new TaskSnapshot(
                $"session:{sessionId}",
                "idle",
                "none",
                identity.CorrelationId,
                ["create-task"],
                "No development task exists yet.",
                ApprovalRequired: false,
                UpdatedAt: DateTimeOffset.UtcNow);
        return Task.FromResult(snapshot);
    }

    public Task<IReadOnlyList<EvidenceRecord>> GetEvidenceAsync(
        string taskId,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        IReadOnlyList<EvidenceRecord> evidence =
        [
            EvidenceFactory.Create(
                identity.CorrelationId,
                "DevelopmentMockHubClient",
                "evidence.read",
                "PASS",
                $"Reference-only evidence for {taskId}.",
                decision.PolicyDecisionRef)
        ];
        return Task.FromResult(evidence);
    }
}
