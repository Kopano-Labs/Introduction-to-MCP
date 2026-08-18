using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;

namespace Kpgs.DomainAdapter;

public static class UpstreamFailureMapper
{
    public static AdapterFailure Map(HttpStatusCode statusCode) => statusCode switch
    {
        HttpStatusCode.NotFound => new("upstream_not_found", "Requested GitHub issue was not found.", false),
        HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden =>
            new("upstream_denied", "GitHub denied the adapter request.", false),
        HttpStatusCode.TooManyRequests =>
            new("upstream_rate_limited", "GitHub rate limited the adapter request.", true),
        _ when (int)statusCode >= 500 =>
            new("upstream_unavailable", "GitHub is temporarily unavailable.", true),
        _ => new("upstream_failure", $"GitHub returned HTTP {(int)statusCode}.", false)
    };
}

public sealed class GitHubIssueReader(HttpClient httpClient)
{
    private readonly HttpClient _httpClient = httpClient;

    public async Task<(GitHubIssueData? Data, AdapterFailure? Failure)> ReadAsync(
        string owner,
        string repository,
        int issueNumber,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(owner)
            || string.IsNullOrWhiteSpace(repository)
            || issueNumber <= 0)
        {
            return (null, new AdapterFailure(
                "request_invalid",
                "Owner, repository and positive issue number are required.",
                false));
        }

        using var request = new HttpRequestMessage(
            HttpMethod.Get,
            $"repos/{Uri.EscapeDataString(owner)}/{Uri.EscapeDataString(repository)}/issues/{issueNumber}");
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/vnd.github+json"));
        request.Headers.Add("X-GitHub-Api-Version", "2022-11-28");

        using var response = await _httpClient.SendAsync(request, cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            return (null, UpstreamFailureMapper.Map(response.StatusCode));
        }

        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        using var document = await JsonDocument.ParseAsync(stream, cancellationToken: cancellationToken);
        var root = document.RootElement;
        var data = new GitHubIssueData(
            root.GetProperty("number").GetInt32(),
            root.GetProperty("title").GetString() ?? string.Empty,
            root.GetProperty("state").GetString() ?? "unknown",
            root.GetProperty("html_url").GetString() ?? string.Empty);
        return (data, null);
    }
}
