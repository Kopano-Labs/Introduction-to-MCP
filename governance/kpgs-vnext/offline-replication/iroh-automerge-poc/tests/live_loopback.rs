use kpgs_automerge_iroh_sync_poc::{
    accept_and_sync, bind_loopback_endpoint, connect_and_sync, verify_remote_binding, BoxError,
    PeerBinding, ReplicaStateClass, SyncReplica, ALPN, AUTHORITY_EFFECT,
};
use std::io::ErrorKind;

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn two_offline_documents_converge_over_real_iroh_quic() -> Result<(), BoxError> {
    let server_endpoint = bind_loopback_endpoint(true).await?;
    let client_endpoint = bind_loopback_endpoint(false).await?;

    let mut client = SyncReplica::new(
        "doc:kasilink-neighbourhood-view",
        "principal:alice",
        ReplicaStateClass::NonAuthoritative,
        PeerBinding::new(server_endpoint.id(), "principal:bob")?,
    )?;
    let mut server = SyncReplica::new(
        "doc:kasilink-neighbourhood-view",
        "principal:bob",
        ReplicaStateClass::NonAuthoritative,
        PeerBinding::new(client_endpoint.id(), "principal:alice")?,
    )?;

    // Both peers mutate useful local state before any network exists between them.
    client.put("nearby_gig", "electrician")?;
    server.put("network_hint", "offline-first")?;

    let server_for_task = server_endpoint.clone();
    let server_task = tokio::spawn(async move { accept_and_sync(&server_for_task, server).await });

    connect_and_sync(&client_endpoint, server_endpoint.addr(), &mut client).await?;
    server = server_task.await??;

    assert_eq!(client.get_string("nearby_gig")?.as_deref(), Some("electrician"));
    assert_eq!(server.get_string("nearby_gig")?.as_deref(), Some("electrician"));
    assert_eq!(client.get_string("network_hint")?.as_deref(), Some("offline-first"));
    assert_eq!(server.get_string("network_hint")?.as_deref(), Some("offline-first"));
    assert_eq!(client.heads(), server.heads());
    assert_eq!(client.authority_effect(), AUTHORITY_EFFECT);
    assert_eq!(server.authority_effect(), AUTHORITY_EFFECT);

    let proposal = client.request_authority_promotion("kpgs-receipt://task/abc/r0002")?;
    assert_eq!(proposal.authority_effect, "proposal_only");
    assert_eq!(proposal.state_class, ReplicaStateClass::NonAuthoritative);

    client_endpoint.close().await;
    server_endpoint.close().await;
    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn automerge_document_and_peer_sync_state_survive_recreation() -> Result<(), BoxError> {
    let server_endpoint = bind_loopback_endpoint(true).await?;
    let client_endpoint = bind_loopback_endpoint(false).await?;

    let server_binding = PeerBinding::new(server_endpoint.id(), "principal:bob")?;
    let client_binding = PeerBinding::new(client_endpoint.id(), "principal:alice")?;

    let mut client = SyncReplica::new(
        "doc:continuity",
        "principal:alice",
        ReplicaStateClass::DerivedProjection,
        server_binding.clone(),
    )?;
    let mut server = SyncReplica::new(
        "doc:continuity",
        "principal:bob",
        ReplicaStateClass::DerivedProjection,
        client_binding,
    )?;

    client.put("first", "before-restart")?;
    let server_for_task = server_endpoint.clone();
    let first_server = tokio::spawn(async move { accept_and_sync(&server_for_task, server).await });
    connect_and_sync(&client_endpoint, server_endpoint.addr(), &mut client).await?;
    server = first_server.await??;

    let persisted = client.persist();
    drop(client);
    let mut restored = SyncReplica::restore(persisted, server_binding)?;

    server.put("second", "after-client-restart")?;
    let server_for_task = server_endpoint.clone();
    let second_server = tokio::spawn(async move { accept_and_sync(&server_for_task, server).await });
    connect_and_sync(&client_endpoint, server_endpoint.addr(), &mut restored).await?;
    server = second_server.await??;

    assert_eq!(restored.get_string("first")?.as_deref(), Some("before-restart"));
    assert_eq!(restored.get_string("second")?.as_deref(), Some("after-client-restart"));
    assert_eq!(restored.heads(), server.heads());
    assert_eq!(restored.state_class(), ReplicaStateClass::DerivedProjection);

    client_endpoint.close().await;
    server_endpoint.close().await;
    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn authenticated_iroh_endpoint_does_not_bypass_kpgs_peer_binding() -> Result<(), BoxError> {
    let server_endpoint = bind_loopback_endpoint(true).await?;
    let client_endpoint = bind_loopback_endpoint(false).await?;
    let unrelated_endpoint = bind_loopback_endpoint(false).await?;

    let accepting_endpoint = server_endpoint.clone();
    let server_task = tokio::spawn(async move {
        let incoming = accepting_endpoint
            .accept()
            .await
            .ok_or_else(|| std::io::Error::new(ErrorKind::ConnectionAborted, "endpoint closed"))?;
        let connection = incoming.await?;
        Ok::<_, BoxError>(connection.remote_id())
    });

    let connection = client_endpoint.connect(server_endpoint.addr(), ALPN).await?;
    let wrong_binding = PeerBinding::new(unrelated_endpoint.id(), "principal:not-the-server")?;
    let error = verify_remote_binding(&connection, &wrong_binding).unwrap_err();
    assert!(error.to_string().contains("identity mismatch"));

    // QUIC/TLS authenticated the actual peer, but application governance rejected
    // the endpoint-to-principal binding we supplied. Transport identity != authority.
    assert_eq!(server_task.await??, client_endpoint.id());

    client_endpoint.close().await;
    unrelated_endpoint.close().await;
    server_endpoint.close().await;
    Ok(())
}
