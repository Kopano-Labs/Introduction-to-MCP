use std::{
    io::{Error as IoError, ErrorKind},
    time::Duration,
};

use automerge::{
    sync::{self, Message, SyncDoc},
    transaction::Transactable,
    AutoCommit, ReadDoc, ROOT,
};
use iroh::{
    endpoint::{presets, Connection, RecvStream, SendStream},
    Endpoint, EndpointAddr, EndpointId,
};

pub type BoxError = Box<dyn std::error::Error + Send + Sync + 'static>;

pub const ALPN: &[u8] = b"kpgs/automerge-iroh/0.1";
pub const MAX_FRAME_BYTES: usize = 4 * 1024 * 1024;
pub const MAX_SYNC_ROUNDS: usize = 128;
pub const SYNC_TIMEOUT: Duration = Duration::from_secs(10);
pub const AUTHORITY_EFFECT: &str = "none";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ReplicaStateClass {
    NonAuthoritative,
    DerivedProjection,
    PendingProposal,
}

impl ReplicaStateClass {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::NonAuthoritative => "non_authoritative",
            Self::DerivedProjection => "derived_projection",
            Self::PendingProposal => "pending_proposal",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PeerBinding {
    pub endpoint_id: EndpointId,
    pub principal_id: String,
}

impl PeerBinding {
    pub fn new(endpoint_id: EndpointId, principal_id: impl Into<String>) -> Result<Self, BoxError> {
        let principal_id = principal_id.into();
        if principal_id.trim().is_empty() {
            return Err(IoError::new(ErrorKind::InvalidInput, "principal_id is required").into());
        }
        Ok(Self {
            endpoint_id,
            principal_id,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PromotionProposal {
    pub document_id: String,
    pub state_class: ReplicaStateClass,
    pub governing_task_receipt_ref: String,
    pub authority_effect: &'static str,
}

#[derive(Clone, Debug)]
pub struct PersistedReplica {
    document_id: String,
    local_principal_id: String,
    state_class: ReplicaStateClass,
    expected_peer_endpoint_id: String,
    expected_peer_principal_id: String,
    document_bytes: Vec<u8>,
    sync_state_bytes: Vec<u8>,
}

#[derive(Debug)]
pub struct SyncReplica {
    document_id: String,
    local_principal_id: String,
    state_class: ReplicaStateClass,
    peer: PeerBinding,
    document: AutoCommit,
    sync_state: sync::State,
}

impl SyncReplica {
    pub fn new(
        document_id: impl Into<String>,
        local_principal_id: impl Into<String>,
        state_class: ReplicaStateClass,
        peer: PeerBinding,
    ) -> Result<Self, BoxError> {
        let document_id = document_id.into();
        let local_principal_id = local_principal_id.into();
        if document_id.trim().is_empty() || local_principal_id.trim().is_empty() {
            return Err(IoError::new(
                ErrorKind::InvalidInput,
                "document_id and local_principal_id are required",
            )
            .into());
        }
        Ok(Self {
            document_id,
            local_principal_id,
            state_class,
            peer,
            document: AutoCommit::new(),
            sync_state: sync::State::new(),
        })
    }

    pub fn document_id(&self) -> &str {
        &self.document_id
    }

    pub fn local_principal_id(&self) -> &str {
        &self.local_principal_id
    }

    pub const fn state_class(&self) -> ReplicaStateClass {
        self.state_class
    }

    pub const fn authority_effect(&self) -> &'static str {
        AUTHORITY_EFFECT
    }

    pub fn peer_binding(&self) -> &PeerBinding {
        &self.peer
    }

    pub fn put(
        &mut self,
        key: &str,
        value: impl Into<automerge::ScalarValue>,
    ) -> Result<(), BoxError> {
        if key.trim().is_empty() {
            return Err(IoError::new(ErrorKind::InvalidInput, "key is required").into());
        }
        self.document.put(ROOT, key, value)?;
        Ok(())
    }

    pub fn get_string(&self, key: &str) -> Result<Option<String>, BoxError> {
        let value = self.document.get(ROOT, key)?;
        Ok(value.and_then(|(value, _)| value.to_str().map(ToOwned::to_owned)))
    }

    pub fn heads(&mut self) -> Vec<automerge::ChangeHash> {
        self.document.get_heads()
    }

    pub fn persist(&mut self) -> PersistedReplica {
        PersistedReplica {
            document_id: self.document_id.clone(),
            local_principal_id: self.local_principal_id.clone(),
            state_class: self.state_class,
            expected_peer_endpoint_id: self.peer.endpoint_id.to_string(),
            expected_peer_principal_id: self.peer.principal_id.clone(),
            document_bytes: self.document.save(),
            sync_state_bytes: self.sync_state.encode(),
        }
    }

    pub fn restore(persisted: PersistedReplica, peer: PeerBinding) -> Result<Self, BoxError> {
        if persisted.expected_peer_endpoint_id != peer.endpoint_id.to_string()
            || persisted.expected_peer_principal_id != peer.principal_id
        {
            return Err(IoError::new(
                ErrorKind::PermissionDenied,
                "persisted sync state is bound to a different peer identity",
            )
            .into());
        }
        Ok(Self {
            document_id: persisted.document_id,
            local_principal_id: persisted.local_principal_id,
            state_class: persisted.state_class,
            peer,
            document: AutoCommit::load(&persisted.document_bytes)?,
            sync_state: sync::State::decode(&persisted.sync_state_bytes)?,
        })
    }

    pub fn request_authority_promotion(
        &self,
        governing_task_receipt_ref: impl Into<String>,
    ) -> Result<PromotionProposal, BoxError> {
        let governing_task_receipt_ref = governing_task_receipt_ref.into();
        if governing_task_receipt_ref.trim().is_empty() {
            return Err(IoError::new(
                ErrorKind::PermissionDenied,
                "a governing KPGS task receipt is required before promotion",
            )
            .into());
        }
        Ok(PromotionProposal {
            document_id: self.document_id.clone(),
            state_class: self.state_class,
            governing_task_receipt_ref,
            authority_effect: "proposal_only",
        })
    }

    fn generate_sync_message(&mut self) -> Option<Message> {
        let Self {
            document,
            sync_state,
            ..
        } = self;
        document.sync().generate_sync_message(sync_state)
    }

    fn receive_sync_message(&mut self, message: Message) -> Result<(), BoxError> {
        let Self {
            document,
            sync_state,
            ..
        } = self;
        document.sync().receive_sync_message(sync_state, message)?;
        Ok(())
    }
}

pub fn verify_remote_binding(
    connection: &Connection,
    expected: &PeerBinding,
) -> Result<(), BoxError> {
    let remote_id = connection.remote_id();
    if remote_id != expected.endpoint_id {
        return Err(IoError::new(
            ErrorKind::PermissionDenied,
            format!(
                "iroh endpoint identity mismatch: expected {}, received {}",
                expected.endpoint_id, remote_id
            ),
        )
        .into());
    }
    // TLS authenticates the iroh endpoint. KPGS still decides whether that
    // endpoint-to-principal binding has any capability for a consequential act.
    if expected.principal_id.trim().is_empty() {
        return Err(IoError::new(ErrorKind::PermissionDenied, "peer principal is empty").into());
    }
    Ok(())
}

pub async fn bind_loopback_endpoint(accept_connections: bool) -> Result<Endpoint, BoxError> {
    let mut builder = Endpoint::builder(presets::Minimal)
        .clear_address_lookup()
        .clear_relay_transports()
        .clear_ip_transports()
        .bind_addr("127.0.0.1:0")?;
    if accept_connections {
        builder = builder.alpns(vec![ALPN.to_vec()]);
    }
    Ok(builder.bind().await?)
}

async fn write_frame(send: &mut SendStream, message: Option<Message>) -> Result<bool, BoxError> {
    let Some(message) = message else {
        send.write_all(&0_u32.to_be_bytes()).await?;
        return Ok(false);
    };
    let payload = message.encode();
    if payload.len() > MAX_FRAME_BYTES {
        return Err(IoError::new(
            ErrorKind::InvalidData,
            "automerge sync frame exceeds limit",
        )
        .into());
    }
    let length = u32::try_from(payload.len())?;
    send.write_all(&length.to_be_bytes()).await?;
    send.write_all(&payload).await?;
    Ok(true)
}

async fn read_frame(recv: &mut RecvStream) -> Result<Option<Message>, BoxError> {
    let mut length_bytes = [0_u8; 4];
    recv.read_exact(&mut length_bytes).await?;
    let length = u32::from_be_bytes(length_bytes) as usize;
    if length == 0 {
        return Ok(None);
    }
    if length > MAX_FRAME_BYTES {
        return Err(IoError::new(
            ErrorKind::InvalidData,
            "received sync frame exceeds limit",
        )
        .into());
    }
    let mut payload = vec![0_u8; length];
    recv.read_exact(&mut payload).await?;
    Ok(Some(Message::decode(&payload)?))
}

async fn client_turns(
    mut send: SendStream,
    mut recv: RecvStream,
    replica: &mut SyncReplica,
) -> Result<usize, BoxError> {
    for round in 1..=MAX_SYNC_ROUNDS {
        let outbound = replica.generate_sync_message();
        let sent = write_frame(&mut send, outbound).await?;
        let inbound = read_frame(&mut recv).await?;
        let received = inbound.is_some();
        if let Some(message) = inbound {
            replica.receive_sync_message(message)?;
        }
        if !sent && !received {
            send.finish()?;
            return Ok(round);
        }
    }
    Err(IoError::new(ErrorKind::TimedOut, "sync exceeded maximum rounds").into())
}

async fn server_turns(
    mut send: SendStream,
    mut recv: RecvStream,
    replica: &mut SyncReplica,
) -> Result<usize, BoxError> {
    for round in 1..=MAX_SYNC_ROUNDS {
        let inbound = read_frame(&mut recv).await?;
        let received = inbound.is_some();
        if let Some(message) = inbound {
            replica.receive_sync_message(message)?;
        }
        let outbound = replica.generate_sync_message();
        let sent = write_frame(&mut send, outbound).await?;
        if !received && !sent {
            send.finish()?;
            return Ok(round);
        }
    }
    Err(IoError::new(ErrorKind::TimedOut, "sync exceeded maximum rounds").into())
}

pub async fn connect_and_sync(
    endpoint: &Endpoint,
    remote: EndpointAddr,
    replica: &mut SyncReplica,
) -> Result<usize, BoxError> {
    let future = async {
        let connection = endpoint.connect(remote, ALPN).await?;
        verify_remote_binding(&connection, replica.peer_binding())?;
        let (send, recv) = connection.open_bi().await?;
        let rounds = client_turns(send, recv, replica).await?;
        Ok::<usize, BoxError>(rounds)
    };
    tokio::time::timeout(SYNC_TIMEOUT, future)
        .await
        .map_err(|_| IoError::new(ErrorKind::TimedOut, "client sync timed out"))?
}

pub async fn accept_and_sync(
    endpoint: &Endpoint,
    mut replica: SyncReplica,
) -> Result<SyncReplica, BoxError> {
    let future = async {
        let incoming = endpoint.accept().await.ok_or_else(|| {
            IoError::new(
                ErrorKind::ConnectionAborted,
                "endpoint closed before accept",
            )
        })?;
        let connection = incoming.await?;
        verify_remote_binding(&connection, replica.peer_binding())?;
        let (send, recv) = connection.accept_bi().await?;
        server_turns(send, recv, &mut replica).await?;
        Ok::<SyncReplica, BoxError>(replica)
    };
    tokio::time::timeout(SYNC_TIMEOUT, future)
        .await
        .map_err(|_| IoError::new(ErrorKind::TimedOut, "server sync timed out"))?
}
