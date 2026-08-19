namespace Kopano.Kpgs.Contracts;

public static class KpgsProtocol
{
    public const string Current = "1.0";
    public const string BoundaryMarker = "#NB";
    public const string ProgressiveUpdate = "APU -> Progressive Update -> #NB -> bounded CRUD -> SWFUS";

    public static bool IsCompatible(string requested, string supported = Current)
    {
        static int Major(string value) => int.TryParse(value.Split('.', 2)[0], out var major) ? major : -1;
        return Major(requested) >= 0 && Major(requested) == Major(supported);
    }
}

public sealed record DomainManifest(
    string EstateProperty,
    string AdapterId,
    string AdapterVersion,
    string ProtocolVersion,
    string GoverningSpecRef);

public sealed record DomainIdentity(
    string SubjectId,
    string SubjectKind,
    string TenantId,
    IReadOnlyDictionary<string, string> Claims);

public sealed record HubContext(
    string EstateProperty,
    string TenantId,
    string DomainId,
    string TaskId,
    string CorrelationId,
    DomainIdentity Identity,
    string GoverningSpecRef);

public sealed record CapabilityRequest(
    string Capability,
    string ResourceScope,
    string IdempotencyKey);

public sealed record CapabilityDecision(
    bool Allowed,
    string DecisionRef,
    string? LeaseToken,
    DateTimeOffset? ExpiresAt,
    string UserSafeReason);

public sealed record GovernedTaskRequest(
    string TaskId,
    string CorrelationId,
    string GoverningSpecRef,
    object Input,
    string IdempotencyKey,
    string BoundaryMarker = KpgsProtocol.BoundaryMarker,
    string CrudIntent = "CREATE");

public sealed record GovernedTaskSnapshot(
    string TaskId,
    string Status,
    long Version,
    IReadOnlyList<string> NextActions,
    string UserSafeExplanation,
    string CorrelationId);

public sealed record GovernedCommand(
    string CommandId,
    string Name,
    object? Payload,
    string IdempotencyKey,
    string CorrelationId,
    string BoundaryMarker = KpgsProtocol.BoundaryMarker);

public sealed record EvidenceSummary(
    string TaskId,
    string CorrelationId,
    IReadOnlyList<string> EvidenceRefs,
    string VerificationStatus);

public sealed record AdapterHealth(
    bool Live,
    bool Ready,
    string HubStatus,
    string ProtocolVersion,
    DateTimeOffset CheckedAt);

public sealed record AdapterVersionInfo(
    string AdapterId,
    string AdapterVersion,
    string ProtocolVersion,
    bool Compatible);

public sealed record RealtimeEvent(
    long Sequence,
    string TaskId,
    string EventType,
    object Payload,
    string CorrelationId,
    DateTimeOffset OccurredAt);

public sealed record RealtimeSnapshot(
    string TaskId,
    long Version,
    IReadOnlyList<RealtimeEvent> Events);
