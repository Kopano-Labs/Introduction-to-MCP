using Kopano.Kpgs.Adapter;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;
using Kopano.Kpgs.Realtime;

static void Assert(bool condition, string message)
{
    if (!condition) throw new InvalidOperationException(message);
}

static async Task ExpectAsync<TException>(Func<Task> action, string message)
    where TException : Exception
{
    try
    {
        await action();
    }
    catch (TException)
    {
        return;
    }
    throw new InvalidOperationException(message);
}

var manifest = new DomainManifest("example.kopanolabs.com", "proof-adapter", "0.1.0-preview.1", "1.0", "kpgs://spec/domain-proof");
var options = new KpgsAdapterOptions(manifest, TimeSpan.FromMilliseconds(100), 1, 2);
var evidence = new InMemoryEvidenceSink();
var hub = new ProofHub();
var adapter = new KpgsDomainAdapter(options, hub, evidence);
await adapter.RegisterAsync();
Assert(hub.Registered, "domain registration did not execute");
Assert((await adapter.HealthAsync()).Ready, "adapter is not ready");
Assert(adapter.Version("1.9").Compatible, "same protocol major should be compatible");
Assert(!adapter.Version("2.0").Compatible, "different protocol major must be incompatible");
Assert(KpgsProtocol.ProgressiveUpdate.Contains("#NB", StringComparison.Ordinal), "progressive-update contract lost #NB");

var identity = new DomainIdentity("human:1", "human", "tenant:1", new Dictionary<string, string>());
var context = new HubContext(manifest.EstateProperty, "tenant:1", "domain:1", "task:1", "corr:1", identity, manifest.GoverningSpecRef);
var request = new GovernedTaskRequest("task:1", "corr:1", manifest.GoverningSpecRef, new { goal = "proof" }, "idem:create:1");
var created = await adapter.CreateTaskAsync(context, request);
var replay = await adapter.CreateTaskAsync(context, request);
Assert(created == replay, "idempotent task replay changed the result");
Assert(hub.CreateCalls == 1, "idempotent task replay executed twice");
Assert(hub.CapabilityCalls == 2, "exact replay bypassed a fresh capability decision");
Assert(evidence.Items.Count == 1 && evidence.Items[0].AuthorityEffect == "none", "execution evidence missing or promoted authority");

await ExpectAsync<KpgsIdempotencyConflictException>(
    () => adapter.CreateTaskAsync(
        context,
        request with { Input = new { goal = "different governed content" } }),
    "changed content reused the same idempotency identity without conflict");
Assert(hub.CreateCalls == 1, "idempotency collision reached a second CREATE mutation");

var concurrentRequest = new GovernedTaskRequest("task:1", "corr:concurrent", manifest.GoverningSpecRef, new { goal = "concurrent" }, "idem:create:concurrent");
var concurrent = await Task.WhenAll(
    adapter.CreateTaskAsync(context, concurrentRequest),
    adapter.CreateTaskAsync(context, concurrentRequest));
Assert(concurrent[0] == concurrent[1], "concurrent exact replay returned divergent snapshots");
Assert(hub.CreateCalls == 2, "concurrent exact replay executed duplicate Hub CREATE work");

var beforeNbCapabilityCalls = hub.CapabilityCalls;
await ExpectAsync<InvalidOperationException>(
    () => adapter.CreateTaskAsync(context, request with { IdempotencyKey = "idem:bad-nb", BoundaryMarker = "NB" }),
    "mutation without literal #NB was admitted");
Assert(hub.CapabilityCalls == beforeNbCapabilityCalls, "invalid #NB boundary reached capability resolution");

hub.Allow = false;
await ExpectAsync<CapabilityDeniedException>(
    () => adapter.ExecuteCommandAsync(context, new GovernedCommand("cmd:deny", "approve", null, "idem:deny:1", "corr:deny")),
    "denied capability executed");
Assert(hub.CommandCalls == 0, "denied command reached the privileged hub operation");
hub.Allow = true;

hub.ExpireLeases = true;
await ExpectAsync<CapabilityDeniedException>(
    () => adapter.ExecuteCommandAsync(context, new GovernedCommand("cmd:expired", "approve", null, "idem:expired:1", "corr:expired")),
    "expired capability lease executed");
Assert(hub.CommandCalls == 0, "expired lease reached the privileged hub operation");
hub.ExpireLeases = false;

await ExpectAsync<InvalidOperationException>(
    () => adapter.ExecuteCommandAsync(
        context,
        new GovernedCommand("cmd:bad-nb", "approve", null, "idem:bad-nb-command", "corr:bad-nb", "NB")),
    "command without literal #NB was admitted");
Assert(hub.CommandCalls == 0, "invalid command #NB reached the privileged hub operation");

var fallbackLog = new List<RealtimeTransportKind>();
var realtime = new KpgsRealtimeClient(
    new ProofSnapshotSource(),
    [
        new ProofTransport(RealtimeTransportKind.Polling, true, fallbackLog),
        new ProofTransport(RealtimeTransportKind.ServerSentEvents, true, fallbackLog),
        new ProofTransport(RealtimeTransportKind.WebSocket, false, fallbackLog),
    ]);
var connection = await realtime.ConnectAsync("task:1");
Assert(connection.Transport == RealtimeTransportKind.ServerSentEvents, "realtime fallback did not prefer WS then SSE");
Assert(fallbackLog.SequenceEqual([RealtimeTransportKind.WebSocket, RealtimeTransportKind.ServerSentEvents]), "fallback order drifted");
Assert(connection.Snapshot.Version == 4, "reconnect did not restore snapshot first");
var sequences = new List<long>();
await foreach (var evt in connection.Events) sequences.Add(evt.Sequence);
Assert(sequences.SequenceEqual([5L, 6L]), "duplicate/old realtime events were not filtered");

var removal = new KpgsDomainAdapter(options, new UnreadyHub(), new InMemoryEvidenceSink());
try
{
    await removal.RegisterAsync();
    throw new InvalidOperationException("rejected registration was promoted");
}
catch (InvalidOperationException)
{
    // Adapter removal/rollback leaves the domain app independent; failure is explicit.
}

Console.WriteLine("KPGS .NET DOMAIN ADAPTER PROOF PASS");

sealed class ProofHub : IKpgsHubClient
{
    public bool Registered { get; private set; }
    public bool Allow { get; set; } = true;
    public bool ExpireLeases { get; set; }
    public int CapabilityCalls { get; private set; }
    public int CreateCalls { get; private set; }
    public int CommandCalls { get; private set; }

    public Task<bool> RegisterAsync(DomainManifest manifest, CancellationToken cancellationToken)
    {
        Registered = true;
        return Task.FromResult(true);
    }

    public Task<bool> IsReadyAsync(CancellationToken cancellationToken) => Task.FromResult(true);

    public Task<CapabilityDecision> RequestCapabilityAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken)
    {
        CapabilityCalls++;
        var expiry = ExpireLeases
            ? DateTimeOffset.UtcNow.AddSeconds(-1)
            : DateTimeOffset.UtcNow.AddMinutes(1);
        return Task.FromResult(new CapabilityDecision(
            Allow,
            "policy://proof",
            Allow ? "lease:proof" : null,
            Allow ? expiry : null,
            !Allow ? "not permitted for this task" : ExpireLeases ? "lease expired" : "allowed"));
    }

    public Task<GovernedTaskSnapshot> CreateTaskAsync(HubContext context, GovernedTaskRequest request, string leaseToken, CancellationToken cancellationToken)
    {
        CreateCalls++;
        return Task.FromResult(new GovernedTaskSnapshot(request.TaskId, "created", CreateCalls, ["continue"], "created", request.CorrelationId));
    }

    public Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, string leaseToken, CancellationToken cancellationToken)
    {
        CommandCalls++;
        return Task.FromResult(new GovernedTaskSnapshot(context.TaskId, command.Name, 2, [], command.Name, command.CorrelationId));
    }

    public Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken) => Task.FromResult<GovernedTaskSnapshot?>(null);
    public Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken) => Task.FromResult(new EvidenceSummary(context.TaskId, context.CorrelationId, [], "proof"));
}

sealed class UnreadyHub : IKpgsHubClient
{
    public Task<bool> RegisterAsync(DomainManifest manifest, CancellationToken cancellationToken) => Task.FromResult(false);
    public Task<bool> IsReadyAsync(CancellationToken cancellationToken) => Task.FromResult(false);
    public Task<CapabilityDecision> RequestCapabilityAsync(HubContext context, CapabilityRequest request, CancellationToken cancellationToken) => throw new InvalidOperationException();
    public Task<GovernedTaskSnapshot> CreateTaskAsync(HubContext context, GovernedTaskRequest request, string leaseToken, CancellationToken cancellationToken) => throw new InvalidOperationException();
    public Task<GovernedTaskSnapshot> ExecuteCommandAsync(HubContext context, GovernedCommand command, string leaseToken, CancellationToken cancellationToken) => throw new InvalidOperationException();
    public Task<GovernedTaskSnapshot?> GetSessionAsync(HubContext context, CancellationToken cancellationToken) => throw new InvalidOperationException();
    public Task<EvidenceSummary> GetEvidenceAsync(HubContext context, CancellationToken cancellationToken) => throw new InvalidOperationException();
}

sealed class ProofSnapshotSource : IKpgsSnapshotSource
{
    public Task<RealtimeSnapshot> GetSnapshotAsync(string taskId, CancellationToken cancellationToken) =>
        Task.FromResult(new RealtimeSnapshot(taskId, 4, []));
}

sealed class ProofTransport(RealtimeTransportKind kind, bool available, List<RealtimeTransportKind> log) : IKpgsRealtimeTransport
{
    public RealtimeTransportKind Kind => kind;

    public Task<bool> ConnectAsync(string taskId, CancellationToken cancellationToken)
    {
        log.Add(kind);
        return Task.FromResult(available);
    }

    public async IAsyncEnumerable<RealtimeEvent> ReadAsync(string taskId, long afterSequence, [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken)
    {
        foreach (var sequence in new long[] { 4, 5, 5, 6 })
        {
            await Task.Yield();
            yield return new RealtimeEvent(sequence, taskId, "proof", new { sequence }, "corr:realtime", DateTimeOffset.UtcNow);
        }
    }
}
