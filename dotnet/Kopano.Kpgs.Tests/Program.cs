using System.Net;
using System.Text.Json;
using Kopano.Kpgs.Adapter;
using Kopano.Kpgs.Contracts;
using Kopano.Kpgs.Evidence;
using Kopano.Kpgs.Realtime;

var proofs = new AdapterProofs();
await proofs.RunAsync();
Console.WriteLine("KPGS .NET domain adapter proof: PASS");

sealed class AdapterProofs
{
    private readonly KpgsIdentityContext _identity = new(
        "subject:test",
        "tenant:test",
        "domain:test",
        "session:test",
        "corr:test");

    public async Task RunAsync()
    {
        await HealthAndVersionAreMachineReadable();
        await AuthorizedCreateIsLeaseBoundAndReplaySafe();
        await SameIdempotencyKeyWithDifferentPayloadRejects();
        await DeniedCapabilityBlocksBeforeMutation();
        await PolicyOutageFailsClosedBeforeMutation();
        await MissingNbBlocksBeforeCapabilityResolution();
        await SafeTransientFailureRetriesOnlyInsideIdempotentBoundary();
        await RealtimeReconnectRecoversFromCanonicalReader();
        await AdapterReplacementRecoversStateFromHubNotLocalMemory();
        RenterEnvelopeIsVersionedContractSurface();
    }

    private async Task HealthAndVersionAreMachineReadable()
    {
        var hub = new FakeHub();
        var (adapter, _) = NewAdapter(hub);
        var health = await adapter.GetHealthAsync();
        var version = adapter.GetVersion();

        Assert(health.Status == "ready" && health.HubReachable, "health must reflect Hub readiness");
        Assert(version.Protocol == KpgsProtocol.Version, "version endpoint must expose canonical protocol version");
        Assert(version.TargetFramework == "net10.0", "adapter target framework must be machine-verifiable");
    }

    private async Task AuthorizedCreateIsLeaseBoundAndReplaySafe()
    {
        var hub = new FakeHub();
        var (adapter, evidence) = NewAdapter(hub);
        var request = CreateRequest("idem-1", "update-1", value: 1);

        var first = await adapter.CreateTaskAsync(request, _identity);
        var replay = await adapter.CreateTaskAsync(request, _identity);

        Assert(first.TaskId == replay.TaskId, "exact replay must return the same governed result");
        Assert(hub.CreateSuccesses == 1, "exact replay must not execute Hub CREATE twice");
        Assert(hub.CapabilityRequests.Count >= 2, "each privileged call must resolve a Hub capability decision");
        Assert(hub.CapabilityRequests.All(r => r.Capability == "task.create"), "CREATE must request task.create capability");

        var emitted = await evidence.QueryAsync(_identity.CorrelationId);
        Assert(emitted.Count >= 2, "executions must emit correlation-bound evidence");
        Assert(emitted.All(record => !record.Canonical && record.AuthorityEffect == "none"), "adapter evidence must never claim canonical authority");
        Assert(emitted.Any(record => record.References.Any(reference => reference.StartsWith("lease:", StringComparison.Ordinal))), "evidence must bind to a Hub lease decision");
    }

    private async Task SameIdempotencyKeyWithDifferentPayloadRejects()
    {
        var hub = new FakeHub();
        var (adapter, _) = NewAdapter(hub);
        await adapter.CreateTaskAsync(CreateRequest("idem-collision", "update-a", value: 1), _identity);

        await ExpectAsync<KpgsIdempotencyConflictException>(
            () => adapter.CreateTaskAsync(CreateRequest("idem-collision", "update-b", value: 2), _identity),
            "same idempotency key with changed governed content must reject");
        Assert(hub.CreateSuccesses == 1, "collision must not reach a second Hub mutation");
    }

    private async Task DeniedCapabilityBlocksBeforeMutation()
    {
        var hub = new FakeHub { DenyCapabilities = true };
        var (adapter, _) = NewAdapter(hub);

        await ExpectAsync<KpgsAuthorizationException>(
            () => adapter.CreateTaskAsync(CreateRequest("idem-denied", "update-denied", value: 1), _identity),
            "denied capability must fail before CREATE");
        Assert(hub.CreateAttempts == 0, "denied capability must not call Hub CREATE");
    }

    private async Task PolicyOutageFailsClosedBeforeMutation()
    {
        var hub = new FakeHub { FailCapabilityTransport = true };
        var (adapter, evidence) = NewAdapter(hub, options: new KpgsAdapterOptions
        {
            EstateProperty = "test.example",
            RequestTimeout = TimeSpan.FromSeconds(1),
            SafeRetryCount = 1,
            CircuitFailureThreshold = 5,
        });

        await ExpectAsync<KpgsAuthorizationException>(
            () => adapter.CreateTaskAsync(CreateRequest("idem-policy", "update-policy", value: 1), _identity),
            "policy outage must HOLD rather than bypass governance");
        Assert(hub.CreateAttempts == 0, "policy outage must not call Hub CREATE");
        var emitted = await evidence.QueryAsync(_identity.CorrelationId);
        Assert(emitted.Any(record => record.Action == "task.create" && record.Outcome == "HOLD"), "policy outage must emit HOLD evidence");
    }

    private async Task MissingNbBlocksBeforeCapabilityResolution()
    {
        var hub = new FakeHub();
        var (adapter, _) = NewAdapter(hub);
        var before = hub.CapabilityRequests.Count;
        var request = CreateRequest("idem-nb", "update-nb", value: 1) with { BoundaryMarker = "NB" };

        await ExpectAsync<InvalidOperationException>(
            () => adapter.CreateTaskAsync(request, _identity),
            "literal #NB is required before mutation");
        Assert(hub.CapabilityRequests.Count == before, "invalid boundary must stop before capability/mutation work");
    }

    private async Task SafeTransientFailureRetriesOnlyInsideIdempotentBoundary()
    {
        var hub = new FakeHub { TransientCreateFailures = 1 };
        var (adapter, _) = NewAdapter(hub, options: new KpgsAdapterOptions
        {
            EstateProperty = "test.example",
            RequestTimeout = TimeSpan.FromSeconds(2),
            SafeRetryCount = 2,
            CircuitFailureThreshold = 5,
        });

        var result = await adapter.CreateTaskAsync(CreateRequest("idem-retry", "update-retry", value: 7), _identity);
        Assert(result.Status == "created", "bounded retry must recover an idempotent transient failure");
        Assert(hub.CreateAttempts == 2 && hub.CreateSuccesses == 1, "retry must execute one transient failure plus one successful CREATE");
    }

    private async Task RealtimeReconnectRecoversFromCanonicalReader()
    {
        var hub = new FakeHub();
        var (adapter, _) = NewAdapter(hub);
        var transport = new FakeRealtimeTransport();
        var realtime = new KpgsRealtimeClient(transport, adapter);

        await realtime.ConnectAsync(_identity.SessionId);
        var recovered = await realtime.ReconnectAndRecoverAsync(_identity.SessionId, _identity);

        Assert(transport.ConnectCalls == 2 && transport.DisconnectCalls == 1, "realtime recovery must reconnect transport");
        Assert(hub.SessionReads == 1, "realtime recovery must reload canonical session state");
        Assert(recovered.Status == "canonical-recovery", "recovered state must come from canonical session reader");
    }

    private async Task AdapterReplacementRecoversStateFromHubNotLocalMemory()
    {
        var hub = new FakeHub();
        var (firstAdapter, _) = NewAdapter(hub);
        var created = await firstAdapter.CreateTaskAsync(CreateRequest("idem-removal", "update-removal", value: 3), _identity);

        // Simulate rollback/removal/restart: discard the entire adapter instance,
        // including its transient idempotency gate, then rebuild from the same Hub.
        var (replacementAdapter, _) = NewAdapter(hub);
        hub.SessionSnapshot = created with { Status = "canonical-after-restart" };
        var recovered = await replacementAdapter.GetSessionSnapshotAsync(_identity.SessionId, _identity);

        Assert(recovered.Status == "canonical-after-restart", "replacement adapter must recover from Hub rather than local durable business state");
        Assert(hub.SessionReads == 1, "rollback/restart recovery must perform canonical read");
    }

    private static void RenterEnvelopeIsVersionedContractSurface()
    {
        var input = JsonSerializer.SerializeToElement(new { prompt = "bounded" });
        var envelope = new RenterRequestEnvelope(
            "task-1",
            "demo-skill",
            "1.0.0",
            "corr-1",
            "lease-1",
            input);
        Assert(envelope.SkillVersion == "1.0.0" && KpgsProtocol.Name == "kpgs.domain-adapter.v1", "renter envelope and adapter protocol must be explicitly versioned");
    }

    private (KpgsAdapterService Adapter, InMemoryEvidenceSink Evidence) NewAdapter(
        FakeHub hub,
        KpgsAdapterOptions? options = null)
    {
        options ??= new KpgsAdapterOptions
        {
            EstateProperty = "test.example",
            AdapterVersion = "0.1.0",
            ProtocolVersion = KpgsProtocol.Version,
            RequestTimeout = TimeSpan.FromSeconds(2),
            SafeRetryCount = 0,
            CircuitFailureThreshold = 3,
        };
        var evidence = new InMemoryEvidenceSink();
        return (
            new KpgsAdapterService(
                hub,
                evidence,
                new InMemoryIdempotencyGate(),
                new KpgsHubInvoker(options),
                options),
            evidence);
    }

    private static TaskCreateRequest CreateRequest(string idempotencyKey, string updateId, int value) =>
        new(
            GoverningSpecRef: "spec:test",
            Input: JsonSerializer.SerializeToElement(new { value }),
            IdempotencyKey: idempotencyKey,
            UpdateId: updateId,
            BoundaryMarker: "#NB",
            CrudIntent: "CREATE");

    private static async Task ExpectAsync<TException>(Func<Task> action, string message)
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
        throw new InvalidOperationException($"PROOF FAILED: {message}");
    }

    private static void Assert(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException($"PROOF FAILED: {message}");
        }
    }
}

sealed class FakeHub : IKpgsHubClient
{
    public bool DenyCapabilities { get; set; }
    public bool FailCapabilityTransport { get; set; }
    public int TransientCreateFailures { get; set; }
    public int CreateAttempts { get; private set; }
    public int CreateSuccesses { get; private set; }
    public int CommandCalls { get; private set; }
    public int SessionReads { get; private set; }
    public List<CapabilityRequest> CapabilityRequests { get; } = [];
    public TaskSnapshot? SessionSnapshot { get; set; }

    public Task<bool> IsReadyAsync(CancellationToken cancellationToken = default) => Task.FromResult(true);

    public Task RegisterDomainAsync(DomainRegistration registration, CapabilityDecision decision, CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task<CapabilityDecision> ResolveCapabilityAsync(
        KpgsIdentityContext identity,
        CapabilityRequest request,
        CancellationToken cancellationToken = default)
    {
        CapabilityRequests.Add(request);
        if (FailCapabilityTransport)
        {
            throw new HttpRequestException("policy unavailable", null, HttpStatusCode.ServiceUnavailable);
        }
        return Task.FromResult(new CapabilityDecision(
            Allowed: !DenyCapabilities,
            LeaseId: DenyCapabilities ? null : $"lease-{CapabilityRequests.Count}",
            ExpiresAt: DenyCapabilities ? null : DateTimeOffset.UtcNow.AddMinutes(1),
            PolicyDecisionRef: "policy:test",
            Reason: DenyCapabilities ? "denied by test policy" : "allowed by test policy"));
    }

    public Task<TaskSnapshot> CreateTaskAsync(
        TaskCreateRequest request,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        CreateAttempts++;
        if (TransientCreateFailures > 0)
        {
            TransientCreateFailures--;
            throw new HttpRequestException("transient", null, HttpStatusCode.ServiceUnavailable);
        }
        CreateSuccesses++;
        var snapshot = new TaskSnapshot(
            $"task-{CreateSuccesses}",
            "created",
            request.GoverningSpecRef,
            identity.CorrelationId,
            ["inspect"],
            "Created by fake Hub under a valid test lease.",
            ApprovalRequired: false,
            UpdatedAt: DateTimeOffset.UtcNow);
        SessionSnapshot = snapshot;
        return Task.FromResult(snapshot);
    }

    public Task<TaskSnapshot> SendCommandAsync(
        string taskId,
        TaskCommandRequest request,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        CommandCalls++;
        var snapshot = (SessionSnapshot ?? new TaskSnapshot(taskId, "unknown", "spec:test", identity.CorrelationId, [], "", false, DateTimeOffset.UtcNow)) with
        {
            Status = $"command:{request.Command}",
            UpdatedAt = DateTimeOffset.UtcNow,
        };
        SessionSnapshot = snapshot;
        return Task.FromResult(snapshot);
    }

    public Task<TaskSnapshot> GetSessionSnapshotAsync(
        string sessionId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        SessionReads++;
        return Task.FromResult(SessionSnapshot ?? new TaskSnapshot(
            $"session:{sessionId}",
            "canonical-recovery",
            "spec:test",
            identity.CorrelationId,
            ["continue"],
            "Recovered from canonical fake Hub snapshot.",
            ApprovalRequired: false,
            UpdatedAt: DateTimeOffset.UtcNow));
    }

    public Task<IReadOnlyList<EvidenceRecord>> GetEvidenceAsync(
        string taskId,
        KpgsIdentityContext identity,
        CapabilityDecision decision,
        CancellationToken cancellationToken = default)
    {
        IReadOnlyList<EvidenceRecord> result =
        [EvidenceFactory.Create(identity.CorrelationId, "FakeHub", "evidence.read", "PASS", taskId, decision.LeaseId ?? "no-lease")];
        return Task.FromResult(result);
    }
}

sealed class FakeRealtimeTransport : IKpgsRealtimeTransport
{
    public int ConnectCalls { get; private set; }
    public int DisconnectCalls { get; private set; }

    public Task ConnectAsync(string sessionId, CancellationToken cancellationToken = default)
    {
        ConnectCalls++;
        return Task.CompletedTask;
    }

    public async IAsyncEnumerable<RealtimeEvent> ReadEventsAsync(
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await Task.CompletedTask;
        yield break;
    }

    public Task DisconnectAsync(CancellationToken cancellationToken = default)
    {
        DisconnectCalls++;
        return Task.CompletedTask;
    }
}
