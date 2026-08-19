using System.Text.Json;

namespace Kopano.Kpgs.Contracts;

public static class KpgsProtocol
{
    public const string Name = "kpgs.domain-adapter.v1";
    public const string Version = "1.0.0";
    public const string ProgressiveUpdate = "APU -> Progressive Update -> #NB -> bounded CRUD -> SWFUS";
}

public sealed record KpgsIdentityContext(
    string SubjectId,
    string TenantId,
    string DomainId,
    string SessionId,
    string CorrelationId);

public sealed record CapabilityRequest(
    string Capability,
    string ResourceScope,
    string TaskId,
    string CorrelationId);

public sealed record CapabilityDecision(
    bool Allowed,
    string? LeaseId,
    DateTimeOffset? ExpiresAt,
    string PolicyDecisionRef,
    string Reason)
{
    public bool IsUsable(DateTimeOffset now) =>
        Allowed &&
        !string.IsNullOrWhiteSpace(LeaseId) &&
        ExpiresAt is not null &&
        ExpiresAt > now;
}

public sealed record TaskCreateRequest(
    string GoverningSpecRef,
    JsonElement Input,
    string IdempotencyKey,
    string UpdateId,
    string BoundaryMarker = "#NB",
    string CrudIntent = "CREATE");

public sealed record TaskCommandRequest(
    string Command,
    JsonElement Input,
    string IdempotencyKey,
    string UpdateId,
    string BoundaryMarker = "#NB");

public sealed record TaskSnapshot(
    string TaskId,
    string Status,
    string GoverningSpecRef,
    string CorrelationId,
    IReadOnlyList<string> NextActions,
    string UserSafeExplanation,
    bool ApprovalRequired,
    DateTimeOffset UpdatedAt);

public sealed record RenterRequestEnvelope(
    string TaskId,
    string SkillName,
    string SkillVersion,
    string CorrelationId,
    string CapabilityLeaseId,
    JsonElement Input);

public sealed record RenterResponseEnvelope(
    string TaskId,
    string CorrelationId,
    string Outcome,
    JsonElement Output,
    string EvidenceRef,
    bool Canonical = false,
    string AuthorityEffect = "none");

public sealed record EvidenceRecord(
    string EvidenceId,
    string CorrelationId,
    string Source,
    string Action,
    string Outcome,
    string Detail,
    IReadOnlyList<string> References,
    DateTimeOffset CreatedAt,
    bool Canonical = false,
    string AuthorityEffect = "none");

public sealed record AdapterHealth(
    string Status,
    bool HubReachable,
    string Protocol,
    string AdapterVersion,
    DateTimeOffset CheckedAt);

public sealed record AdapterVersion(
    string Adapter,
    string Protocol,
    string TargetFramework,
    IReadOnlyList<string> CompatibleProtocols);

public sealed record RealtimeEvent(
    string SessionId,
    string EventId,
    string CorrelationId,
    string Kind,
    JsonElement Payload,
    DateTimeOffset OccurredAt);

public interface ICanonicalSessionReader
{
    Task<TaskSnapshot> GetSessionSnapshotAsync(
        string sessionId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default);
}
