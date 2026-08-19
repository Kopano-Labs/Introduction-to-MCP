using System.Collections.Concurrent;
using Kopano.Kpgs.Adapter;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;

var builder = WebApplication.CreateBuilder(args);
var manifest = new DomainManifest(
    builder.Configuration["KPGS_ESTATE_PROPERTY"] ?? "localhost.kpgs",
    "reference-dotnet-adapter",
    "0.1.0-preview.1",
    KpgsProtocol.Current,
    "kpgs://spec/dotnet-domain-adapter-v1");
var options = new KpgsAdapterOptions(manifest, TimeSpan.FromSeconds(5), 2, 3);
var hub = new LocalMockHub();
var evidence = new InMemoryEvidenceSink();
var adapter = new KpgsDomainAdapter(options, hub, evidence);
await adapter.RegisterAsync();

var app = builder.Build();

HubContext Context(HttpContext http)
{
    var taskId = http.Request.RouteValues["id"]?.ToString() ?? http.Request.Headers["X-KPGS-Task"].FirstOrDefault() ?? "new-task";
    var correlation = http.Request.Headers["X-Correlation-ID"].FirstOrDefault() ?? Guid.NewGuid().ToString("n");
    return new HubContext(
        manifest.EstateProperty,
        "reference-tenant",
        "reference-domain",
        taskId,
        correlation,
        new DomainIdentity("reference-user", "human", "reference-tenant", new Dictionary<string, string>()),
        manifest.GoverningSpecRef);
}

app.MapKpgsAdapter(adapter, Context);
app.MapGet("/kpgs/evidence", () => Results.Ok(evidence.Items));
app.Run();

sealed class LocalMockHub : IKpgsHubClient
{
    private readonly ConcurrentDictionary<string, GovernedTaskSnapshot> _tasks = new(StringComparer.Ordinal);

    public Task<bool> RegisterAsync(DomainManifest manifest, CancellationToken cancellationToken) => Task.FromResult(true);
    public Task<bool> IsReadyAsync(CancellationToken cancellationToken) => Task.FromResult(true);

    public Task<CapabilityDecision> RequestCapabilityAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken) =>
        Task.FromResult(new CapabilityDecision(true, $"policy://local/{request.Capability}", "local-short-lived-lease", DateTimeOffset.UtcNow.AddMinutes(5), "Allowed by local development policy."));

    public Task<GovernedTaskSnapshot> CreateTaskAsync(HubContext context, GovernedTaskRequest request, string leaseToken, CancellationToken cancellationToken)
    {
        var snapshot = new GovernedTaskSnapshot(request.TaskId, "created", 1, ["continue", "cancel"], "Task created through the local KPGS mock.", request.CorrelationId);
        _tasks[request.TaskId] = snapshot;
        return Task.FromResult(snapshot);
    }

    public Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, string leaseToken, CancellationToken cancellationToken)
    {
        var prior = _tasks.TryGetValue(context.TaskId, out var found)
            ? found
            : new GovernedTaskSnapshot(context.TaskId, "missing", 0, [], "Task does not exist.", command.CorrelationId);
        var next = prior with { Status = command.Name, Version = prior.Version + 1, CorrelationId = command.CorrelationId };
        _tasks[context.TaskId] = next;
        return Task.FromResult(next);
    }

    public Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken) =>
        Task.FromResult(_tasks.TryGetValue(context.TaskId, out var value) ? value : null);

    public Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken) =>
        Task.FromResult(new EvidenceSummary(context.TaskId, context.CorrelationId, [$"kpgs://task/{context.TaskId}"], "local-development"));
}

public partial class Program;
