import { AnimatePresence, motion } from 'framer-motion';
import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import './App.css';
import { appendStreamChunk } from './labsUi';
import type { EditableArtifact, EditableTask } from './labsUi';
import { clientTelemetryConfigured, trackClientEvent } from './telemetry';
import { AnimatedBackdrop } from './components/AnimatedBackdrop';
import { AppTopNav } from './components/AppTopNav';
import type {
  ConnectionState,
  CoworkRoom,
  CoworkRoomSummary,
  FeedLogEntry,
  GuiUser,
  LabsAnalytics,
  LabsOverview,
  Lesson,
  LiveMessage,
  McpConsoleReply,
  MicrosoftReadiness,
  PageId,
} from './types';

const CouncilPage = lazy(async () => ({ default: (await import('./pages/CouncilPage')).CouncilPage }));
const LabsPage = lazy(async () => ({ default: (await import('./pages/LabsPage')).LabsPage }));
const ForgePage = lazy(async () => ({ default: (await import('./pages/ForgePage')).ForgePage }));
const ConsolePage = lazy(async () => ({ default: (await import('./pages/ConsolePage')).ConsolePage }));
const AdminPage = lazy(async () => ({ default: (await import('./pages/AdminPage')).AdminPage }));

const apiBase = 'http://127.0.0.1:8000';
const agentList = ['kopano', 'claude', 'grok', 'gemini', 'copilot'];
const laneOrder = ['research', 'build', 'review'];
const ownerOptions = ['Lead', 'DEV_1', 'DEV_2', 'DEV_3 (Background)', 'kopano'];

const pageHeadlines: Record<PageId, string> = {
  council: 'Council',
  labs: 'Labs',
  forge: 'Forge',
  console: 'Console',
  admin: 'Admin',
};

const hasCoworkRoomDetail = (room: CoworkRoomSummary | null | undefined): room is CoworkRoom => (
  Boolean(room?.tasks && room?.artifacts && room?.lanes && room?.dispatch_summary && room?.artifact_summary)
);

const readPageFromHash = (): PageId => {
  if (typeof window === 'undefined') {
    return 'council';
  }

  const raw = window.location.hash.replace(/^#\/?/, '').trim().toLowerCase();
  if (raw === 'labs' || raw === 'forge' || raw === 'console' || raw === 'admin' || raw === 'council') {
    return raw;
  }
  return 'council';
};

const pageTransition = {
  initial: { opacity: 0, y: 30, scale: 0.99 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -24, scale: 1.01 },
};

const App = () => {
  const [page, setPage] = useState<PageId>(readPageFromHash);
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting');
  const [feedLog, setFeedLog] = useState<FeedLogEntry[]>([
    {
      id: 'system-ready',
      type: 'system',
      content: 'Council room booted. Waiting for websocket or polled updates.',
      received_at: new Date().toISOString(),
      source: 'system',
    },
  ]);
  const [sessions, setSessions] = useState<Lesson[]>([]);
  const [selectedSession, setSelectedSession] = useState<Lesson | null>(null);
  const [labsOverview, setLabsOverview] = useState<LabsOverview | null>(null);
  const [labsAnalytics, setLabsAnalytics] = useState<LabsAnalytics | null>(null);
  const [microsoftReadiness, setMicrosoftReadiness] = useState<MicrosoftReadiness | null>(null);
  const [coworkRooms, setCoworkRooms] = useState<CoworkRoomSummary[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [roomName, setRoomName] = useState('Kopano Context Premiere');
  const [roomMission, setRoomMission] = useState('Launch the first creator-grade cowork flow inside Kopano Labs.');
  const [artifactTitle, setArtifactTitle] = useState('Azure Demo Day Connector Pack');
  const [artifactSummary, setArtifactSummary] = useState('Installer guidance and connector workflow notes for IDE, CLI, Azure, and MCP parity.');
  const [artifactType, setArtifactType] = useState('api');
  const [taskTitle, setTaskTitle] = useState('Implement connector execution cards');
  const [taskDescription, setTaskDescription] = useState('Ship click-to-run install and connector playbooks in Kopano Labs.');
  const [taskOwner, setTaskOwner] = useState('DEV_1');
  const [taskPriority, setTaskPriority] = useState('high');
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editingArtifactId, setEditingArtifactId] = useState<number | null>(null);
  const [consoleMessage, setConsoleMessage] = useState('How should Kopano support MCP chat across IDEs, CLI, operating systems, skills, Azure, and connectors?');
  const [consoleReply, setConsoleReply] = useState<McpConsoleReply | null>(null);
  const [consoleStream, setConsoleStream] = useState('');
  const [selectedModel, setSelectedModel] = useState('deterministic');
  const [connectorResult, setConnectorResult] = useState('');
  const [adminUser, setAdminUser] = useState<GuiUser | null>(null);
  const [adminEmail, setAdminEmail] = useState('admin@kopano.local');
  const [adminPassword, setAdminPassword] = useState('demo-admin');
  const [adminError, setAdminError] = useState<string | null>(null);
  const [adminLoading, setAdminLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const seenFeedIds = useRef<Set<string>>(new Set(['system-ready']));

  const activeRoomCandidate = coworkRooms.find((room) => room.id === activeRoomId) ?? coworkRooms[0] ?? null;
  const activeRoom = hasCoworkRoomDetail(activeRoomCandidate)
    ? activeRoomCandidate
    : coworkRooms.find((room) => hasCoworkRoomDetail(room)) ?? null;
  const isAdminLoggedIn = adminUser?.role === 'admin';
  const featuredAgentId = activeAgent ?? thinkingAgent ?? 'kopano';
  const latestTransmission = messages[messages.length - 1] ?? null;
  const councilCards = agentList.map((id) => {
    const lastMsg = messages.filter((message) => message.agent === id).slice(-1)[0];
    return {
      id,
      lastMsg,
      isStudent: id === 'kopano',
      isThinking: thinkingAgent === id,
      isResponding: activeAgent === id,
    };
  });
  const featuredCouncilCard = councilCards.find((card) => card.id === featuredAgentId) ?? councilCards[0];
  const supportCouncilCards = councilCards.filter((card) => card.id !== featuredCouncilCard.id);
  const latestFeedEntries = feedLog.slice(-10).reverse();
  const consoleFeedPreview = latestFeedEntries.filter((entry) => entry.source !== 'system').slice(0, 4);
  const adminFeedPreview = latestFeedEntries.slice(0, 8);

  const pushFeedLog = useCallback((entry: FeedLogEntry) => {
    if (seenFeedIds.current.has(entry.id)) {
      return;
    }
    seenFeedIds.current.add(entry.id);
    setFeedLog((prev) => [...prev, entry].slice(-60));
  }, []);

  const logSystemEvent = useCallback((type: string, content: string) => {
    const stamp = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    pushFeedLog({
      id: `system:${type}:${stamp}`,
      type,
      content,
      received_at: new Date().toISOString(),
      source: 'system',
    });
  }, [pushFeedLog]);

  const navigate = (nextPage: PageId) => {
    const nextHash = `#/${nextPage}`;
    if (window.location.hash !== nextHash) {
      window.location.hash = nextHash;
    }
    setPage(nextPage);
  };

  const postJson = async (url: string, body: object) => fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const fetchLabsAnalytics = async () => setLabsAnalytics(await (await fetch(`${apiBase}/api/labs/analytics`)).json());
  const fetchMicrosoftReadiness = async () => setMicrosoftReadiness(await (await fetch(`${apiBase}/api/labs/microsoft-readiness`)).json());

  const fetchCoworkRoomDetail = async (roomId: number) => {
    const data = await (await fetch(`${apiBase}/api/labs/cowork/rooms/${roomId}`)).json();
    const room: CoworkRoom = data.room;
    setCoworkRooms((prev) => [room, ...prev.filter((entry) => entry.id !== roomId)].sort((a, b) => b.id - a.id));
    setActiveRoomId(roomId);
  };

  const fetchCoworkRooms = async () => {
    const data = await (await fetch(`${apiBase}/api/labs/cowork/rooms`)).json();
    setCoworkRooms((prev) => {
      const detailedRooms = prev.filter((room) => hasCoworkRoomDetail(room));
      return data.rooms.map((room: CoworkRoomSummary) => detailedRooms.find((candidate) => candidate.id === room.id) ?? room);
    });
    if (!activeRoomId && data.rooms.length > 0) {
      await fetchCoworkRoomDetail(data.rooms[0].id);
    }
  };

  const refreshLabs = async (roomId?: number) => {
    await fetchCoworkRooms();
    if (roomId) {
      await fetchCoworkRoomDetail(roomId);
    }
    await fetchLabsAnalytics();
    await fetchMicrosoftReadiness();
  };

  const handleLiveEvent = useCallback((data: Partial<LiveMessage> & { type?: string }, source: 'ws' | 'poll') => {
    const entryId = `${data.type ?? 'unknown'}:${data.agent ?? 'system'}:${data.block_id ?? 'no-block'}:${data.round ?? '0'}:${data.content ?? ''}`;

    if (data.type === 'thinking') {
      setThinkingAgent(data.agent ?? null);
      setActiveAgent(null);
    }

    if (data.type === 'response' && data.agent && data.block_id && data.content && data.reasoning && typeof data.round === 'number') {
      setThinkingAgent(null);
      setActiveAgent(data.agent);
      const nextMessage: LiveMessage = {
        type: 'response',
        agent: data.agent,
        block_id: data.block_id,
        content: data.content,
        reasoning: data.reasoning,
        round: data.round,
        value_score: data.value_score,
        override_score: data.override_score,
        improvement_hint: data.improvement_hint,
      };
      setMessages((prev) => {
        if (prev.some((message) => message.block_id === data.block_id)) {
          return prev;
        }
        return [...prev, nextMessage];
      });
      window.setTimeout(() => {
        setActiveAgent((current) => (current === data.agent ? null : current));
      }, 5000);
    }

    if (data.type === 'override') {
      setSelectedSession((prev) => prev ? ({
        ...prev,
        rounds: prev.rounds?.map((round) => ({
          ...round,
          blocks: round.blocks.map((block) => block.block_id === data.block_id
            ? { ...block, override_score: data.override_score ?? null, improvement_hint: data.improvement_hint ?? null }
            : block),
        })),
      }) : null);
    }

    pushFeedLog({
      id: entryId,
      type: data.type ?? 'unknown',
      agent: data.agent,
      content: data.content,
      reasoning: data.reasoning,
      round: data.round,
      received_at: new Date().toISOString(),
      source,
    });
  }, [pushFeedLog]);

  useEffect(() => {
    const handleHashChange = () => {
      setPage(readPageFromHash());
    };

    if (!window.location.hash) {
      window.location.hash = '#/council';
    }
    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  useEffect(() => {
    trackClientEvent('orch_page_view', { page });
  }, [page]);

  useEffect(() => {
    let isMounted = true;
    const savedAdmin = window.localStorage.getItem('kopano-admin-user');
    if (savedAdmin) {
      try {
        setAdminUser(JSON.parse(savedAdmin) as GuiUser);
      } catch {
        window.localStorage.removeItem('kopano-admin-user');
      }
    }

    ws.current = new WebSocket(`${apiBase.replace('http', 'ws')}/ws/live`);
    ws.current.onopen = () => {
      setConnectionState('live');
      logSystemEvent('connection', 'WebSocket feed connected to the live council.');
    };
    ws.current.onerror = () => {
      setConnectionState('error');
      logSystemEvent('connection-error', 'WebSocket feed reported an error.');
    };
    ws.current.onclose = () => {
      setConnectionState('error');
      logSystemEvent('connection-closed', 'WebSocket feed closed. Polling fallback remains active.');
    };
    ws.current.onmessage = (event) => handleLiveEvent(JSON.parse(event.data), 'ws');

    const pollUpdates = window.setInterval(async () => {
      try {
        const response = await fetch(`${apiBase}/updates`);
        const updates = await response.json();
        if (!Array.isArray(updates)) {
          return;
        }
        updates.forEach((update) => handleLiveEvent(update, 'poll'));
        if (updates.length > 0) {
          setConnectionState('live');
        }
      } catch {
        setConnectionState((current) => (current === 'live' ? current : 'error'));
      }
    }, 4000);

    const loadInitialData = async () => {
      const [sessionsData, overviewData, analyticsData, roomsPayload, microsoftReadinessData] = await Promise.all([
        fetch(`${apiBase}/sessions`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/overview`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/analytics`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/cowork/rooms`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/microsoft-readiness`).then((response) => response.json()),
      ]);

      if (!isMounted) {
        return;
      }

      setSessions(sessionsData);
      setLabsOverview(overviewData);
      setLabsAnalytics(analyticsData);
      setCoworkRooms(roomsPayload.rooms);
      setMicrosoftReadiness(microsoftReadinessData);
      logSystemEvent('bootstrap', 'Council, labs, forge, and vault data loaded.');

      if (roomsPayload.rooms.length > 0) {
        const detailPayload = await fetch(`${apiBase}/api/labs/cowork/rooms/${roomsPayload.rooms[0].id}`).then((response) => response.json());
        if (!isMounted) {
          return;
        }
        const room: CoworkRoom = detailPayload.room;
        setCoworkRooms((prev) => [room, ...prev.filter((entry) => entry.id !== room.id)].sort((a, b) => b.id - a.id));
        setActiveRoomId(room.id);
      }
    };

    window.setTimeout(() => {
      void loadInitialData();
    }, 0);

    return () => {
      isMounted = false;
      window.clearInterval(pollUpdates);
      ws.current?.close();
    };
  }, [handleLiveEvent, logSystemEvent]);

  const createCoworkRoom = async () => {
    const data = await (await postJson(`${apiBase}/api/labs/cowork/rooms`, { name: roomName, mission: roomMission, lead: 'Lead' })).json();
    await refreshLabs(data.room.id);
    logSystemEvent('forge', `Forge room "${data.room.name}" launched for demo execution.`);
  };

  const createArtifact = async () => {
    if (!activeRoom) {
      return;
    }

    if (editingArtifactId) {
      await postJson(`${apiBase}/api/labs/cowork/artifacts/${editingArtifactId}/edit`, {
        artifact_type: artifactType,
        title: artifactTitle,
        summary: artifactSummary,
        status: 'draft',
        link: 'Kopano Context',
      });
      setEditingArtifactId(null);
    } else {
      await postJson(`${apiBase}/api/labs/cowork/rooms/${activeRoom.id}/artifacts`, {
        artifact_type: artifactType,
        title: artifactTitle,
        summary: artifactSummary,
        status: 'draft',
        link: 'Kopano Context',
      });
    }

    await refreshLabs(activeRoom.id);
    logSystemEvent('artifact', `Artifact "${artifactTitle}" saved in ${activeRoom.name}.`);
  };

  const createOrUpdateTask = async () => {
    if (!activeRoom) {
      return;
    }

    if (editingTaskId) {
      await postJson(`${apiBase}/api/labs/cowork/tasks/${editingTaskId}/edit`, {
        title: taskTitle,
        description: taskDescription,
        owner: taskOwner,
        priority: taskPriority,
      });
      setEditingTaskId(null);
    } else {
      await postJson(`${apiBase}/api/labs/cowork/rooms/${activeRoom.id}/tasks`, {
        title: taskTitle,
        description: taskDescription,
        owner: taskOwner,
        priority: taskPriority,
        lane: 'build',
      });
    }

    await refreshLabs(activeRoom.id);
    logSystemEvent('task', `Task "${taskTitle}" routed to ${taskOwner} in ${activeRoom.name}.`);
  };

  const updateTaskStatus = async (taskId: number, status: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/status`, { status });
    if (activeRoom) {
      await refreshLabs(activeRoom.id);
    }
    logSystemEvent('task-status', `Task ${taskId} moved to ${status}.`);
  };

  const updateTaskOwner = async (taskId: number, owner: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/owner`, { owner });
    if (activeRoom) {
      await refreshLabs(activeRoom.id);
    }
    logSystemEvent('task-owner', `Task ${taskId} reassigned to ${owner}.`);
  };

  const moveTaskToLane = async (taskId: number, lane: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/lane`, { lane });
    if (activeRoom) {
      await refreshLabs(activeRoom.id);
    }
    logSystemEvent('task-lane', `Task ${taskId} moved into ${lane}.`);
  };

  const runConnectorAction = async (actionId: string) => {
    const data = await (await postJson(`${apiBase}/api/labs/connectors/actions/execute`, { action_id: actionId })).json();
    const readinessLines = data.readiness
      ? [
        `Required checks: ${data.readiness.summary.required_ready}/${data.readiness.summary.required_total}`,
        `Azure CLI: ${data.readiness.tooling.az.healthy ? data.readiness.tooling.az.version : 'missing or broken'}`,
        `Azure Developer CLI: ${data.readiness.tooling.azd.healthy ? data.readiness.tooling.azd.version : 'missing or broken'}`,
        `Azure login: ${data.readiness.azure_account.logged_in ? data.readiness.azure_account.subscription_name : 'not signed in'}`,
        `Server telemetry: ${data.readiness.tooling.telemetry.configured ? 'configured' : data.readiness.tooling.telemetry.reason}`,
      ]
      : [];

    setConnectorResult([data.title, data.summary, ...readinessLines, ...(data.commands ?? []), ...(data.next_steps ?? [])].join('\n'));
    if (data.readiness) {
      setMicrosoftReadiness(data.readiness as MicrosoftReadiness);
    }
    trackClientEvent('orch_connector_action', { action_id: actionId });
    logSystemEvent('connector', `${data.title} executed from Kopano Labs.`);
  };

  const sendConsoleMessage = async () => {
    const data = await (await postJson(`${apiBase}/api/labs/mcp-console/chat`, {
      message: consoleMessage,
      session_id: consoleReply?.session_id ?? null,
      model_preference: selectedModel === 'deterministic' ? null : selectedModel,
    })).json();

    setConsoleReply(data);
    setConsoleStream(data.response);
    await fetchLabsAnalytics();
    logSystemEvent('console', `Console reply generated on topic "${data.topic}".`);
  };

  const streamConsoleMessage = async () => {
    setConsoleStream('');
    const response = await fetch(`${apiBase}/api/labs/mcp-console/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: consoleMessage,
        session_id: consoleReply?.session_id ?? null,
        model_preference: selectedModel === 'deterministic' ? null : selectedModel,
      }),
    });
    const text = await response.text();
    const chunks = text.split('\n\n').filter(Boolean);
    let aggregated = '';
    let finalPayload: McpConsoleReply | null = null;

    for (const entry of chunks) {
      const raw = entry.replace(/^data:\s*/, '');
      const payload = JSON.parse(raw) as { type: string; content?: string } & Partial<McpConsoleReply>;
      if (payload.type === 'chunk') {
        aggregated = appendStreamChunk(aggregated, payload);
        setConsoleStream(aggregated);
      }
      if (payload.type === 'final') {
        finalPayload = payload as McpConsoleReply;
      }
    }

    if (finalPayload) {
      setConsoleReply(finalPayload);
      setConsoleStream(finalPayload.response);
      logSystemEvent('console-stream', `Streaming console reply completed on topic "${finalPayload.topic}".`);
    }

    await fetchLabsAnalytics();
  };

  const loadSession = async (id: string) => {
    const session = await (await fetch(`${apiBase}/sessions/${id}`)).json();
    setSelectedSession(session);
    navigate('admin');
  };

  const overrideScore = async (blockId: string, score: number) => {
    if (!selectedSession) {
      return;
    }
    await postJson(`${apiBase}/sessions/${selectedSession.id}/override`, { block_id: blockId, override_score: score });
  };

  const loginAdmin = async () => {
    setAdminLoading(true);
    setAdminError(null);
    try {
      const response = await postJson(`${apiBase}/auth/login`, { email: adminEmail, password: adminPassword });
      const data = await response.json();
      if (!response.ok) {
        setAdminError(data.detail ?? 'Admin login failed.');
        return;
      }
      if (data.user?.role !== 'admin') {
        setAdminError('This account is not an admin.');
        return;
      }
      setAdminUser(data.user);
      window.localStorage.setItem('kopano-admin-user', JSON.stringify(data.user));
      navigate('admin');
      logSystemEvent('admin-login', `Admin session opened for ${data.user.email}.`);
    } catch {
      setAdminError('Unable to reach the Kopano auth service.');
    } finally {
      setAdminLoading(false);
    }
  };

  const logoutAdmin = () => {
    setAdminUser(null);
    setSelectedSession(null);
    setAdminError(null);
    window.localStorage.removeItem('kopano-admin-user');
    navigate('labs');
    logSystemEvent('admin-logout', 'Admin session closed. Returned to public Labs.');
  };

  const editTask = (task: EditableTask) => {
    setEditingTaskId(task.id);
    setTaskTitle(task.title);
    setTaskDescription(task.description);
    setTaskOwner(task.owner);
    setTaskPriority(task.priority);
  };

  const editArtifact = (artifact: EditableArtifact) => {
    setEditingArtifactId(artifact.id);
    setArtifactType(artifact.artifact_type);
    setArtifactTitle(artifact.title);
    setArtifactSummary(artifact.summary);
  };

  return (
    <div className={`orch-app page-${page}`}>
      <AnimatedBackdrop page={page} connectionState={connectionState} />
      <div className="shell-frame">
        <AppTopNav
          page={page}
          connectionState={connectionState}
          sessionCount={sessions.length}
          isAdminLoggedIn={isAdminLoggedIn}
          onNavigate={navigate}
        />

        <div className="page-caption-row">
          <span className="eyebrow">Now showing</span>
          <h1>{pageHeadlines[page]}</h1>
          <div className="badge-cluster">
            <span className="status-badge neutral">{clientTelemetryConfigured ? 'Browser telemetry armed' : 'Browser telemetry pending'}</span>
            <span className="status-badge neutral">{microsoftReadiness ? `${microsoftReadiness.summary.required_ready}/${microsoftReadiness.summary.required_total} Microsoft checks ready` : 'Loading Microsoft checks'}</span>
          </div>
        </div>

        <main className="page-stage">
          <Suspense fallback={<div className="glass-card loading-card">Loading surface...</div>}>
            <AnimatePresence mode="wait">
              <motion.div
                key={page}
                className="page-surface"
                variants={pageTransition}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={{ duration: 0.62, ease: [0.16, 1, 0.3, 1] }}
              >
                {page === 'council' && (
                  <CouncilPage
                    connectionState={connectionState}
                    featuredCard={featuredCouncilCard}
                    supportCards={supportCouncilCards}
                    latestTransmission={latestTransmission}
                    feedPreview={latestFeedEntries.slice(0, 6)}
                    sessionCount={sessions.length}
                    onNavigate={navigate}
                  />
                )}

                {page === 'labs' && (
                  <LabsPage
                    labsOverview={labsOverview}
                    labsAnalytics={labsAnalytics}
                    microsoftReadiness={microsoftReadiness}
                    connectorResult={connectorResult}
                    isAdminLoggedIn={isAdminLoggedIn}
                    onNavigate={navigate}
                    onRunConnectorAction={(actionId) => { void runConnectorAction(actionId); }}
                  />
                )}

                {page === 'forge' && (
                  <ForgePage
                    coworkRooms={coworkRooms}
                    activeRoom={activeRoom}
                    roomName={roomName}
                    roomMission={roomMission}
                    taskTitle={taskTitle}
                    taskDescription={taskDescription}
                    taskOwner={taskOwner}
                    taskPriority={taskPriority}
                    artifactTitle={artifactTitle}
                    artifactSummary={artifactSummary}
                    artifactType={artifactType}
                    editingTaskId={editingTaskId}
                    editingArtifactId={editingArtifactId}
                    laneOrder={laneOrder}
                    ownerOptions={ownerOptions}
                    onRoomNameChange={setRoomName}
                    onRoomMissionChange={setRoomMission}
                    onTaskTitleChange={setTaskTitle}
                    onTaskDescriptionChange={setTaskDescription}
                    onTaskOwnerChange={setTaskOwner}
                    onTaskPriorityChange={setTaskPriority}
                    onArtifactTitleChange={setArtifactTitle}
                    onArtifactSummaryChange={setArtifactSummary}
                    onArtifactTypeChange={setArtifactType}
                    onCreateRoom={() => { void createCoworkRoom(); }}
                    onSelectRoom={(roomId) => { void fetchCoworkRoomDetail(roomId); }}
                    onCreateOrUpdateTask={() => { void createOrUpdateTask(); }}
                    onCreateArtifact={() => { void createArtifact(); }}
                    onUpdateTaskStatus={(taskId, status) => { void updateTaskStatus(taskId, status); }}
                    onUpdateTaskOwner={(taskId, owner) => { void updateTaskOwner(taskId, owner); }}
                    onMoveTaskToLane={(taskId, lane) => { void moveTaskToLane(taskId, lane); }}
                    onEditTask={editTask}
                    onEditArtifact={editArtifact}
                  />
                )}

                {page === 'console' && (
                  <ConsolePage
                    consoleMessage={consoleMessage}
                    consoleReply={consoleReply}
                    consoleStream={consoleStream}
                    selectedModel={selectedModel}
                    feedPreview={consoleFeedPreview}
                    labsAnalytics={labsAnalytics}
                    onConsoleMessageChange={setConsoleMessage}
                    onModelChange={setSelectedModel}
                    onSend={() => { void sendConsoleMessage(); }}
                    onStream={() => { void streamConsoleMessage(); }}
                  />
                )}

                {page === 'admin' && (
                  <AdminPage
                    isAdminLoggedIn={isAdminLoggedIn}
                    adminUser={adminUser}
                    adminEmail={adminEmail}
                    adminPassword={adminPassword}
                    adminError={adminError}
                    adminLoading={adminLoading}
                    sessions={sessions}
                    selectedSession={selectedSession}
                    adminFeedPreview={adminFeedPreview}
                    labsAnalytics={labsAnalytics}
                    microsoftReadiness={microsoftReadiness}
                    onAdminEmailChange={setAdminEmail}
                    onAdminPasswordChange={setAdminPassword}
                    onLogin={() => { void loginAdmin(); }}
                    onLogout={logoutAdmin}
                    onLoadSession={(id) => { void loadSession(id); }}
                    onOverrideScore={(blockId, score) => { void overrideScore(blockId, score); }}
                  />
                )}
              </motion.div>
            </AnimatePresence>
          </Suspense>
        </main>
      </div>
    </div>
  );
};

export default App;
