using System.Collections.Concurrent;
using Kopano.Kpgs.Contracts;

namespace Kopano.Kpgs.Evidence;

public interface IKpgsEvidenceSink
{
    Task EmitAsync(EvidenceRecord record, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<EvidenceRecord>> QueryAsync(string correlationId, CancellationToken cancellationToken = default);
}

/// <summary>
/// Reference-only transient sink. It is observability evidence, never durable canonical business state.
/// Production domains should inject their governed evidence transport.
/// </summary>
public sealed class InMemoryEvidenceSink : IKpgsEvidenceSink
{
    private readonly ConcurrentQueue<EvidenceRecord> _records = new();

    public Task EmitAsync(EvidenceRecord record, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (record.Canonical || !string.Equals(record.AuthorityEffect, "none", StringComparison.Ordinal))
        {
            throw new InvalidOperationException("Adapter evidence cannot claim canonical authority.");
        }
        _records.Enqueue(record);
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<EvidenceRecord>> QueryAsync(string correlationId, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        IReadOnlyList<EvidenceRecord> result = _records
            .Where(record => string.Equals(record.CorrelationId, correlationId, StringComparison.Ordinal))
            .OrderBy(record => record.CreatedAt)
            .ToArray();
        return Task.FromResult(result);
    }
}

public static class EvidenceFactory
{
    public static EvidenceRecord Create(
        string correlationId,
        string source,
        string action,
        string outcome,
        string detail,
        params string[] references) =>
        new(
            EvidenceId: $"evidence_{Guid.NewGuid():N}",
            CorrelationId: correlationId,
            Source: source,
            Action: action,
            Outcome: outcome,
            Detail: detail,
            References: references,
            CreatedAt: DateTimeOffset.UtcNow,
            Canonical: false,
            AuthorityEffect: "none");
}
