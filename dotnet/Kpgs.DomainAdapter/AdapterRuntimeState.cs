namespace Kpgs.DomainAdapter;

public sealed record AdapterRuntimeState(
    KpgsLeaseVerifier? LeaseVerifier,
    bool GitHubTokenConfigured,
    string Version = "1.0.0",
    string Contract = "kpgs.domain-adapter.v1")
{
    public bool Ready => LeaseVerifier is not null;
}
