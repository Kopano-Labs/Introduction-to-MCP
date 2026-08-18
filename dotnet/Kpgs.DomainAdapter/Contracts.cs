using System.Text.Json.Serialization;

namespace Kpgs.DomainAdapter;

public sealed record GitHubIssueReadRequest(
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("correlation_id")] string CorrelationId,
    [property: JsonPropertyName("tenant_id")] string TenantId,
    [property: JsonPropertyName("domain_id")] string DomainId,
    [property: JsonPropertyName("task_id")] string TaskId,
    [property: JsonPropertyName("lease_token")] string LeaseToken,
    [property: JsonPropertyName("operation_nonce")] string OperationNonce,
    [property: JsonPropertyName("owner")] string Owner,
    [property: JsonPropertyName("repository")] string Repository,
    [property: JsonPropertyName("issue_number")] int IssueNumber);

public sealed record GitHubIssueData(
    [property: JsonPropertyName("number")] int Number,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("html_url")] string HtmlUrl);

public sealed record AdapterFailure(
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("retryable")] bool Retryable);

public sealed record AdapterReceipt<T>(
    [property: JsonPropertyName("schema")] string Schema,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("correlation_id")] string CorrelationId,
    [property: JsonPropertyName("outcome")] string Outcome,
    [property: JsonPropertyName("operation")] string Operation,
    [property: JsonPropertyName("resource_scope")] string ResourceScope,
    [property: JsonPropertyName("lease_id")] string? LeaseId,
    [property: JsonPropertyName("data")] T? Data,
    [property: JsonPropertyName("failure")] AdapterFailure? Failure,
    [property: JsonPropertyName("authority_effect")] string AuthorityEffect = "none");

internal sealed record LeaseHeader(
    [property: JsonPropertyName("alg")] string Alg,
    [property: JsonPropertyName("typ")] string Typ,
    [property: JsonPropertyName("kid")] string Kid,
    [property: JsonPropertyName("iss")] string Issuer);

internal sealed record LeaseSubject(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind);

internal sealed record LeaseCapability(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("resource_scope")] string ResourceScope);

internal sealed record LeasePayload(
    [property: JsonPropertyName("lease_id")] string LeaseId,
    [property: JsonPropertyName("subject")] LeaseSubject Subject,
    [property: JsonPropertyName("tenant_id")] string TenantId,
    [property: JsonPropertyName("domain_id")] string DomainId,
    [property: JsonPropertyName("task_id")] string TaskId,
    [property: JsonPropertyName("capabilities")] LeaseCapability[] Capabilities,
    [property: JsonPropertyName("issued_at")] DateTimeOffset IssuedAt,
    [property: JsonPropertyName("expires_at")] DateTimeOffset ExpiresAt,
    [property: JsonPropertyName("nonce")] string Nonce);

public sealed record LeaseDecision(
    string LeaseId,
    string SubjectId,
    string KeyId,
    string Capability,
    string ResourceScope);
