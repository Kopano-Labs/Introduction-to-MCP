using Kopano.Kpgs.Contracts;

namespace Kopano.Kpgs.Realtime;

public interface IKpgsRealtimeTransport
{
    Task ConnectAsync(string sessionId, CancellationToken cancellationToken = default);
    IAsyncEnumerable<RealtimeEvent> ReadEventsAsync(CancellationToken cancellationToken = default);
    Task DisconnectAsync(CancellationToken cancellationToken = default);
}

public sealed class KpgsRealtimeClient
{
    private readonly IKpgsRealtimeTransport _transport;
    private readonly ICanonicalSessionReader _canonicalReader;

    public KpgsRealtimeClient(IKpgsRealtimeTransport transport, ICanonicalSessionReader canonicalReader)
    {
        _transport = transport;
        _canonicalReader = canonicalReader;
    }

    public Task ConnectAsync(string sessionId, CancellationToken cancellationToken = default) =>
        _transport.ConnectAsync(sessionId, cancellationToken);

    public IAsyncEnumerable<RealtimeEvent> ReadEventsAsync(CancellationToken cancellationToken = default) =>
        _transport.ReadEventsAsync(cancellationToken);

    /// <summary>
    /// Reconnect never treats missed socket events as canonical state. After the
    /// transport reconnects, the client reloads the session from the canonical reader.
    /// </summary>
    public async Task<TaskSnapshot> ReconnectAndRecoverAsync(
        string sessionId,
        KpgsIdentityContext identity,
        CancellationToken cancellationToken = default)
    {
        await _transport.DisconnectAsync(cancellationToken);
        await _transport.ConnectAsync(sessionId, cancellationToken);
        return await _canonicalReader.GetSessionSnapshotAsync(sessionId, identity, cancellationToken);
    }
}
