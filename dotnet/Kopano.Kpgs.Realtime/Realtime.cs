using Kopano.Kpgs.Contracts;

namespace Kopano.Kpgs.Realtime;

public enum RealtimeTransportKind
{
    WebSocket,
    ServerSentEvents,
    Polling,
}

public interface IKpgsRealtimeTransport
{
    RealtimeTransportKind Kind { get; }
    Task<bool> ConnectAsync(string taskId, CancellationToken cancellationToken);
    IAsyncEnumerable<RealtimeEvent> ReadAsync(string taskId, long afterSequence, CancellationToken cancellationToken);
}

public interface IKpgsSnapshotSource
{
    Task<RealtimeSnapshot> GetSnapshotAsync(string taskId, CancellationToken cancellationToken);
}

public sealed record RealtimeConnection(
    RealtimeTransportKind Transport,
    RealtimeSnapshot Snapshot,
    IAsyncEnumerable<RealtimeEvent> Events);

public sealed class KpgsRealtimeClient(
    IKpgsSnapshotSource snapshotSource,
    IEnumerable<IKpgsRealtimeTransport> transports)
{
    private readonly IReadOnlyList<IKpgsRealtimeTransport> _transports = transports
        .OrderBy(t => t.Kind switch
        {
            RealtimeTransportKind.WebSocket => 0,
            RealtimeTransportKind.ServerSentEvents => 1,
            _ => 2,
        })
        .ToArray();

    public async Task<RealtimeConnection> ConnectAsync(string taskId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(taskId)) throw new ArgumentException("taskId is required", nameof(taskId));

        // Recovery is source-first: snapshot canonical state before accepting deltas.
        var snapshot = await snapshotSource.GetSnapshotAsync(taskId, cancellationToken);
        foreach (var transport in _transports)
        {
            if (!await transport.ConnectAsync(taskId, cancellationToken)) continue;
            return new RealtimeConnection(
                transport.Kind,
                snapshot,
                Deduplicate(transport.ReadAsync(taskId, snapshot.Version, cancellationToken), snapshot.Version, cancellationToken));
        }

        throw new InvalidOperationException("No governed realtime transport is available.");
    }

    private static async IAsyncEnumerable<RealtimeEvent> Deduplicate(
        IAsyncEnumerable<RealtimeEvent> source,
        long floor,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken)
    {
        var last = floor;
        await foreach (var item in source.WithCancellation(cancellationToken))
        {
            if (item.Sequence <= last) continue;
            last = item.Sequence;
            yield return item;
        }
    }
}
