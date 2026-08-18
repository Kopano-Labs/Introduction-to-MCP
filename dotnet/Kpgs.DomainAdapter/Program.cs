using System.Diagnostics;
using System.Net.Http.Headers;
using Kpgs.DomainAdapter;
using Microsoft.AspNetCore.RateLimiting;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("adapter", limiter =>
    {
        limiter.PermitLimit = 30;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
    });
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});

KpgsLeaseVerifier? leaseVerifier = null;
try
{
    leaseVerifier = KpgsLeaseVerifier.FromConfiguration(builder.Configuration);
}
catch (ArgumentException)
{
    // Contract-only mode: health remains observable, privileged execution is denied.
}

var githubToken = builder.Configuration["GITHUB_TOKEN"];
builder.Services.AddSingleton(new AdapterRuntimeState(
    leaseVerifier,
    !string.IsNullOrWhiteSpace(githubToken)));
builder.Services.AddSingleton<OperationReplayGuard>();
builder.Services.AddHttpClient<GitHubIssueReader>(client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("KPGS-DomainAdapter/1.0");
    if (!string.IsNullOrWhiteSpace(githubToken))
    {
        client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", githubToken);
    }
});

var app = builder.Build();
app.UseRateLimiter();

app.MapGet("/kpgs/health", (AdapterRuntimeState state) => Results.Ok(new
{
    status = state.Ready ? "ready" : "contract-only",
    contract = state.Contract,
    version = state.Version,
    lease_verification = state.Ready,
    github_token_configured = state.GitHubTokenConfigured,
    canonical_state_owner = false,
    authority_effect = "none",
}));

app.MapGet("/kpgs/version", (AdapterRuntimeState state) => Results.Ok(new
{
    contract = state.Contract,
    version = state.Version,
    runtime = ".NET 10",
    authority_effect = "none",
}));

app.MapPost(
        "/kpgs/execute/github-issue-read",
        async (
            GitHubIssueReadRequest request,
            AdapterRuntimeState state,
            OperationReplayGuard replayGuard,
            GitHubIssueReader reader,
            ILogger<Program> logger,
            CancellationToken cancellationToken) =>
        {
            const string operation = "github.issue.read";
            var resourceScope =
                $"github:{request.Owner}/{request.Repository}/issues/{request.IssueNumber}";

            if (string.IsNullOrWhiteSpace(request.RequestId)
                || string.IsNullOrWhiteSpace(request.CorrelationId)
                || request.IssueNumber <= 0)
            {
                return Results.Json(
                    Failure<object>(
                        request,
                        operation,
                        resourceScope,
                        "request_invalid",
                        "Request identity and a positive issue number are required.",
                        false),
                    statusCode: StatusCodes.Status400BadRequest);
            }

            if (state.LeaseVerifier is null)
            {
                return Results.Json(
                    Failure<object>(
                        request,
                        operation,
                        resourceScope,
                        "adapter_not_configured",
                        "Lease verification keys are not configured.",
                        true),
                    statusCode: StatusCodes.Status503ServiceUnavailable);
            }

            LeaseDecision lease;
            try
            {
                lease = state.LeaseVerifier.Verify(
                    request.LeaseToken,
                    request.TenantId,
                    request.DomainId,
                    request.TaskId,
                    operation,
                    resourceScope);
            }
            catch (LeaseVerificationException exception)
            {
                logger.LogWarning(
                    "KPGS adapter lease denied code={Code} correlation={CorrelationId} resource={ResourceScope}",
                    exception.Code,
                    request.CorrelationId,
                    resourceScope);
                return Results.Json(
                    Failure<object>(
                        request,
                        operation,
                        resourceScope,
                        exception.Code,
                        exception.Message,
                        false),
                    statusCode: StatusCodes.Status403Forbidden);
            }

            if (!replayGuard.TryConsume(lease.LeaseId, request.OperationNonce))
            {
                return Results.Json(
                    new AdapterReceipt<object>(
                        "kpgs.domain-adapter.receipt.v1",
                        request.RequestId,
                        request.CorrelationId,
                        "hold",
                        operation,
                        resourceScope,
                        lease.LeaseId,
                        null,
                        new AdapterFailure(
                            "operation_replay",
                            "Operation nonce has already been consumed or is invalid.",
                            false)),
                    statusCode: StatusCodes.Status409Conflict);
            }

            var stopwatch = Stopwatch.StartNew();
            var (data, failure) = await reader.ReadAsync(
                request.Owner,
                request.Repository,
                request.IssueNumber,
                cancellationToken);
            stopwatch.Stop();

            if (failure is not null)
            {
                logger.LogWarning(
                    "KPGS adapter upstream failure code={Code} correlation={CorrelationId} elapsed_ms={ElapsedMs} resource={ResourceScope}",
                    failure.Code,
                    request.CorrelationId,
                    stopwatch.ElapsedMilliseconds,
                    resourceScope);
                var statusCode = failure.Code switch
                {
                    "upstream_not_found" => StatusCodes.Status404NotFound,
                    "upstream_rate_limited" => StatusCodes.Status429TooManyRequests,
                    "upstream_unavailable" => StatusCodes.Status503ServiceUnavailable,
                    "upstream_denied" => StatusCodes.Status502BadGateway,
                    _ => StatusCodes.Status502BadGateway,
                };
                return Results.Json(
                    new AdapterReceipt<GitHubIssueData>(
                        "kpgs.domain-adapter.receipt.v1",
                        request.RequestId,
                        request.CorrelationId,
                        "hold",
                        operation,
                        resourceScope,
                        lease.LeaseId,
                        null,
                        failure),
                    statusCode: statusCode);
            }

            logger.LogInformation(
                "KPGS adapter success correlation={CorrelationId} elapsed_ms={ElapsedMs} resource={ResourceScope}",
                request.CorrelationId,
                stopwatch.ElapsedMilliseconds,
                resourceScope);
            return Results.Ok(new AdapterReceipt<GitHubIssueData>(
                "kpgs.domain-adapter.receipt.v1",
                request.RequestId,
                request.CorrelationId,
                "allow",
                operation,
                resourceScope,
                lease.LeaseId,
                data,
                null));
        })
    .RequireRateLimiting("adapter");

app.Run();

static AdapterReceipt<T> Failure<T>(
    GitHubIssueReadRequest request,
    string operation,
    string resourceScope,
    string code,
    string message,
    bool retryable) =>
    new(
        "kpgs.domain-adapter.receipt.v1",
        request.RequestId,
        request.CorrelationId,
        "hold",
        operation,
        resourceScope,
        null,
        default,
        new AdapterFailure(code, message, retryable));

public partial class Program;
