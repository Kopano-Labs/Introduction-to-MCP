import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import { appendStreamChunk, toEditableArtifact, toEditableTask } from './labsUi';

type ViewMode = 'council' | 'labs';
type LessonState = 'queued' | 'learning' | 'learned' | 'shipping';

interface ReasoningBlock { block_id: string; agent: string; role: string | null; content: string; reasoning: string; value_score: number; override_score: number | null; improvement_hint: string | null; is_student: number; }
interface Round { id: string; round_number: number; blocks: ReasoningBlock[]; }
interface Lesson { id: string; topic: string; created_at: string; rounds?: Round[]; }
interface LiveMessage { type: string; agent: string; block_id: string; content: string; reasoning: string; round: number; value_score?: number; override_score?: number; improvement_hint?: string; }
interface LabsCategory { id: string; title: string; description: string; }
interface LabsTool { id: string; name: string; category: string; criticality: string; status: string; summary: string; impact: string; phase: string; }
interface LabsPhase { id: string; title: string; criticality: string; status: string; summary: string; deliverables: string[]; }
interface LabsLanguage { id: string; name: string; family: string; status: string; }
interface AccessMode { id: string; name: string; summary: string; criticality: string; }
interface CoworkSurface { id: string; name: string; status: string; inspiration: string; summary: string; features: string[]; }
interface OrchCodeTrack { id: string; title: string; priority: string; summary: string; topics: string[]; }
interface OrchInterface { id: string; name: string; status: string; summary: string; mechanics: string[]; }
interface CloudStack { id: string; name: string; provider: string; priority: string; status: string; summary: string; focus: string[]; }
interface ConnectorWorkflow { id: string; name: string; status: string; summary: string; }
interface InstallerAction { id: string; surface: string; title: string; provider: string; status: string; summary: string; commands: string[]; }
interface CoworkTask { id: number; room_id: number; title: string; description: string; owner: string; status: string; priority: string; lane: string; }
interface CoworkArtifact { id: number; room_id: number; artifact_type: string; title: string; summary: string; status: string; link: string | null; }
interface CoworkRoom { id: number; name: string; mission: string; lead: string; status: string; tasks: CoworkTask[]; artifacts: CoworkArtifact[]; lanes: Record<string, CoworkTask[]>; dispatch_summary: { total_tasks: number; queued: number; in_progress: number; completed: number; owners: string[]; }; artifact_summary: { total_artifacts: number; artifact_types: string[]; }; }
interface LessonControl { lesson_key: string; title: string; track: string; source: string; status: LessonState; confidence: number; notes: string; }
interface OrchCodeProfile { title: string; lessons: LessonControl[]; summary: { total_lessons: number; learned_lessons: number; learning_lessons: number; }; control_states: LessonState[]; recommended_next: LessonControl[]; }
interface ConsoleAnalytics { sessions: number; requests: number; average_latency_ms: number; top_topics: Array<{ topic: string; count: number }>; }
interface McpConsoleReply { session_id: number; input: string; topic: string; response: string; suggested_actions: string[]; surfaces: string[]; model_used: string; model_options: Array<{ id: string; label: string; model: string }>; analytics: ConsoleAnalytics; }
interface LabsOverview { title: string; positioning: string; categories: LabsCategory[]; tools: LabsTool[]; phases: LabsPhase[]; languages: LabsLanguage[]; access_modes: AccessMode[]; cowork_surfaces: CoworkSurface[]; orch_code_tracks: OrchCodeTrack[]; orch_interfaces: OrchInterface[]; cloud_stacks: CloudStack[]; connector_workflows: ConnectorWorkflow[]; installer_actions: InstallerAction[]; metrics: { categories: number; tools: number; critical_tools: number; live_tools: number; languages: number; access_modes: number; interfaces: number; cloud_stacks: number; installer_actions: number; }; }
interface LabsAnalytics { forge: { rooms: number; tasks: number; artifacts: number; completed_tasks: number; creator_throughput: Array<{ owner: string; count: number }>; event_volume: Array<{ event_type: string; count: number }>; }; mcp_console: ConsoleAnalytics; }
interface ExecutionTask { id: string; label: string; done: boolean; }
interface ExecutionPhase { id: string; title: string; focus: string; tasks: ExecutionTask[]; }
interface SquadTask { id: string; label: string; owner: string; done: boolean; }
interface SquadPhase { id: string; title: string; focus: string; tasks: SquadTask[]; }

const apiBase = 'http://127.0.0.1:8000';
const agentList = ['orch', 'grok', 'gemini', 'claude', 'copilot'];
const laneOrder = ['research', 'build', 'review'];
const ownerOptions = ['Lead', 'DEV_1', 'DEV_2', 'DEV_3 (Background)', 'orch'];
const criticalityLabel = (value: string) => value.replace('_', ' ').toUpperCase();
const executionPlan: ExecutionPhase[] = [
  { id: 'phase-1', title: 'Phase 1', focus: 'Core orchestration foundation', tasks: [
    { id: 'p1-t1', label: 'Multi-provider agent bootstrap', done: true },
    { id: 'p1-t2', label: 'Typer CLI command surface', done: true },
    { id: 'p1-t3', label: 'Session lifecycle flow', done: true },
    { id: 'p1-t4', label: 'SQLite persistence baseline', done: true },
  ]},
  { id: 'phase-2', title: 'Phase 2', focus: 'Moderator and memory intelligence', tasks: [
    { id: 'p2-t1', label: 'Moderator guidance loop', done: true },
    { id: 'p2-t2', label: 'Audit log model and scoring', done: true },
    { id: 'p2-t3', label: 'Historical session export', done: true },
    { id: 'p2-t4', label: 'Long-term memory retrieval', done: true },
  ]},
  { id: 'phase-3', title: 'Phase 3', focus: 'Tools and integrations', tasks: [
    { id: 'p3-t1', label: 'Tool executor routing', done: true },
    { id: 'p3-t2', label: 'Security scan tools', done: true },
    { id: 'p3-t3', label: 'Data analytics tool suite', done: true },
    { id: 'p3-t4', label: 'KasiLink and Labs APIs', done: true },
  ]},
  { id: 'phase-4', title: 'Phase 4', focus: 'Scale, reliability, governance', tasks: [
    { id: 'p4-t1', label: 'Parallel execution path', done: true },
    { id: 'p4-t2', label: 'Security auditor checks', done: true },
    { id: 'p4-t3', label: 'Admin and auth bootstrap', done: true },
    { id: 'p4-t4', label: 'Braintrust telemetry hooks', done: true },
  ]},
  { id: 'phase-5', title: 'Phase 5', focus: 'MORE UI/UX', tasks: [
    { id: 'p5-t1', label: 'Phase progress cockpit', done: true },
    { id: 'p5-t2', label: 'Responsive Labs layout tuning', done: true },
    { id: 'p5-t3', label: 'Accessibility keyboard/focus pass', done: true },
    { id: 'p5-t4', label: 'Visual polish and motion refinement', done: true },
  ]},
];
const executionPlanPhase6Plus: ExecutionPhase[] = [
  { id: 'phase-6', title: 'Phase 6', focus: 'Deployment and delivery', tasks: [
    { id: 'p6-t1', label: 'Deployment readiness checklist', done: true },
    { id: 'p6-t2', label: 'Environment validation checklist', done: true },
    { id: 'p6-t3', label: 'Release runbook skeleton', done: true },
    { id: 'p6-t4', label: 'Rollback workflow checklist', done: true },
  ]},
  { id: 'phase-7', title: 'Phase 7', focus: 'Observability and telemetry', tasks: [
    { id: 'p7-t1', label: 'Telemetry coverage matrix', done: true },
    { id: 'p7-t2', label: 'Runtime log triage workflow', done: true },
    { id: 'p7-t3', label: 'Incident severity templates', done: true },
    { id: 'p7-t4', label: 'Postmortem template', done: true },
  ]},
  { id: 'phase-8', title: 'Phase 8', focus: 'Security and governance', tasks: [
    { id: 'p8-t1', label: 'Secrets hygiene checklist', done: true },
    { id: 'p8-t2', label: 'Access review checklist', done: true },
    { id: 'p8-t3', label: 'Dependency audit cadence', done: true },
    { id: 'p8-t4', label: 'Threat-model review checklist', done: true },
  ]},
  { id: 'phase-9', title: 'Phase 9', focus: 'Reliability engineering', tasks: [
    { id: 'p9-t1', label: 'SLO and error-budget template', done: true },
    { id: 'p9-t2', label: 'Synthetic checks checklist', done: true },
    { id: 'p9-t3', label: 'Backup and restore drill checklist', done: true },
    { id: 'p9-t4', label: 'Chaos test checklist', done: true },
  ]},
  { id: 'phase-10', title: 'Phase 10', focus: 'MORE UI/UX', tasks: [
    { id: 'p10-t1', label: 'Usability benchmark checklist', done: true },
    { id: 'p10-t2', label: 'Accessibility QA checklist', done: true },
    { id: 'p10-t3', label: 'Visual consistency checklist', done: true },
    { id: 'p10-t4', label: 'Motion/performance budget checklist', done: true },
  ]},
];
const executionPlanLeadDev2: SquadPhase[] = [
  { id: 'phase-11', title: 'Phase 11', focus: 'Platform delivery', tasks: [
    { id: 'p11-t1', label: 'Release checklist finalization', owner: 'Lead', done: true },
    { id: 'p11-t2', label: 'Deployment command verification', owner: 'DEV_2', done: true },
    { id: 'p11-t3', label: 'Environment profile audit', owner: 'DEV_3 (Background)', done: true },
    { id: 'p11-t4', label: 'Rollback rehearsal', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-12', title: 'Phase 12', focus: 'Observability operations', tasks: [
    { id: 'p12-t1', label: 'Live runtime dashboard pass', owner: 'Lead', done: true },
    { id: 'p12-t2', label: 'Latency hotspot triage', owner: 'DEV_3 (Background)', done: true },
    { id: 'p12-t3', label: 'Alert routing validation', owner: 'Lead', done: true },
    { id: 'p12-t4', label: 'Incident timeline template', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-13', title: 'Phase 13', focus: 'Security and controls', tasks: [
    { id: 'p13-t1', label: 'Credential rotation checklist', owner: 'Lead', done: true },
    { id: 'p13-t2', label: 'Dependency risk review', owner: 'DEV_2', done: true },
    { id: 'p13-t3', label: 'Access control verification', owner: 'DEV_3 (Background)', done: true },
    { id: 'p13-t4', label: 'Threat review snapshot', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-14', title: 'Phase 14', focus: 'Reliability quality', tasks: [
    { id: 'p14-t1', label: 'SLO conformance review', owner: 'Lead', done: true },
    { id: 'p14-t2', label: 'Synthetic health checks', owner: 'DEV_2', done: true },
    { id: 'p14-t3', label: 'Backup restore drill', owner: 'DEV_3 (Background)', done: true },
    { id: 'p14-t4', label: 'Failure simulation pass', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-15', title: 'Phase 15', focus: 'MORE UI/UX', tasks: [
    { id: 'p15-t1', label: 'Interaction polish pass', owner: 'Lead', done: true },
    { id: 'p15-t2', label: 'Mobile ergonomics tune-up', owner: 'DEV_2', done: true },
    { id: 'p15-t3', label: 'Accessibility verification', owner: 'DEV_3 (Background)', done: true },
    { id: 'p15-t4', label: 'Motion and performance budget', owner: 'DEV_2', done: true },
  ]},
];
const executionPlanDev2Dev3: SquadPhase[] = [
  { id: 'phase-16', title: 'Phase 16', focus: 'Platform Ops', tasks: [
    { id: 'p16-t1', label: 'Release command audit', owner: 'Lead', done: true },
    { id: 'p16-t2', label: 'Deployment smoke validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p16-t3', label: 'Environment variable sanity check', owner: 'DEV_2', done: true },
    { id: 'p16-t4', label: 'Rollback script verification', owner: 'DEV_3 (Background)', done: true },
    { id: 'p16-t5', label: 'Packaging artifact review', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-17', title: 'Phase 17', focus: 'Observability', tasks: [
    { id: 'p17-t1', label: 'Console telemetry review', owner: 'Lead', done: true },
    { id: 'p17-t2', label: 'Runtime log indexing pass', owner: 'DEV_3 (Background)', done: true },
    { id: 'p17-t3', label: 'Alert threshold calibration', owner: 'DEV_2', done: true },
    { id: 'p17-t4', label: 'Session analytics consistency check', owner: 'DEV_3 (Background)', done: true },
    { id: 'p17-t5', label: 'Incident note template update', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-18', title: 'Phase 18', focus: 'Security & Reliability', tasks: [
    { id: 'p18-t1', label: 'Secret exposure checklist pass', owner: 'Lead', done: true },
    { id: 'p18-t2', label: 'Dependency scan triage', owner: 'DEV_3 (Background)', done: true },
    { id: 'p18-t3', label: 'Access reassignment audit', owner: 'DEV_2', done: true },
    { id: 'p18-t4', label: 'Backup restore simulation review', owner: 'DEV_3 (Background)', done: true },
    { id: 'p18-t5', label: 'Failure-mode checklist run', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-19', title: 'Phase 19', focus: 'Product Execution', tasks: [
    { id: 'p19-t1', label: 'Orchestration acceptance pass', owner: 'Lead', done: true },
    { id: 'p19-t2', label: 'Task lane integrity review', owner: 'DEV_3 (Background)', done: true },
    { id: 'p19-t3', label: 'Ownership transition verification', owner: 'DEV_2', done: true },
    { id: 'p19-t4', label: 'Ship-readiness summary', owner: 'Lead', done: true },
    { id: 'p19-t5', label: 'Final signoff capture', owner: 'DEV_2', done: true },
  ]},
];
const executionPlanDev2Dev3Cycle2: SquadPhase[] = [
  { id: 'phase-20', title: 'Phase 20', focus: 'Platform Delivery', tasks: [
    { id: 'p20-t1', label: 'Release gate verification', owner: 'Lead', done: true },
    { id: 'p20-t2', label: 'Deployment path validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p20-t3', label: 'Env parity check', owner: 'DEV_2', done: true },
    { id: 'p20-t4', label: 'Rollback path verification', owner: 'DEV_3 (Background)', done: true },
    { id: 'p20-t5', label: 'Build artifact integrity check', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-21', title: 'Phase 21', focus: 'Observability & Ops', tasks: [
    { id: 'p21-t1', label: 'Runtime dashboard review', owner: 'Lead', done: true },
    { id: 'p21-t2', label: 'Log quality pass', owner: 'DEV_3 (Background)', done: true },
    { id: 'p21-t3', label: 'Alert threshold check', owner: 'DEV_2', done: true },
    { id: 'p21-t4', label: 'Session telemetry validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p21-t5', label: 'Incident workflow confirmation', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-22', title: 'Phase 22', focus: 'Security & Reliability', tasks: [
    { id: 'p22-t1', label: 'Secret hygiene audit', owner: 'Lead', done: true },
    { id: 'p22-t2', label: 'Dependency risk sweep', owner: 'DEV_3 (Background)', done: true },
    { id: 'p22-t3', label: 'Access-change audit', owner: 'DEV_2', done: true },
    { id: 'p22-t4', label: 'Backup restore validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p22-t5', label: 'Failure-mode checklist', owner: 'DEV_3 (Background)', done: true },
  ]},
  { id: 'phase-23', title: 'Phase 23', focus: 'Execution & UX Delivery', tasks: [
    { id: 'p23-t1', label: 'Final execution acceptance', owner: 'Lead', done: true },
    { id: 'p23-t2', label: 'Task flow consistency check', owner: 'DEV_3 (Background)', done: true },
    { id: 'p23-t3', label: 'Ownership transition validation', owner: 'DEV_2', done: true },
    { id: 'p23-t4', label: 'Delivery summary signoff', owner: 'Lead', done: true },
    { id: 'p23-t5', label: 'Final QA signoff', owner: 'DEV_2', done: true },
  ]},
];

const App: React.FC = () => {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Lesson[]>([]);
  const [selectedSession, setSelectedSession] = useState<Lesson | null>(null);
  const [isAuditMode, setIsAuditMode] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('council');
  const [labsOverview, setLabsOverview] = useState<LabsOverview | null>(null);
  const [coworkRooms, setCoworkRooms] = useState<CoworkRoom[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [roomName, setRoomName] = useState('Orch Forge Premiere');
  const [roomMission, setRoomMission] = useState('Launch the first creator-grade cowork flow inside Orch Labs.');
  const [artifactTitle, setArtifactTitle] = useState('Azure Demo Day Connector Pack');
  const [artifactSummary, setArtifactSummary] = useState('Installer guidance and connector workflow notes for IDE, CLI, Azure, AWS, and MCP parity.');
  const [artifactType, setArtifactType] = useState('api');
  const [taskTitle, setTaskTitle] = useState('Implement connector execution cards');
  const [taskDescription, setTaskDescription] = useState('Ship click-to-run install and connector playbooks in Orch Labs.');
  const [taskOwner, setTaskOwner] = useState('DEV_1');
  const [taskPriority, setTaskPriority] = useState('high');
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editingArtifactId, setEditingArtifactId] = useState<number | null>(null);
  const [consoleMessage, setConsoleMessage] = useState('How should Orch support MCP chat across IDEs, CLI, operating systems, skills, Azure, and connectors?');
  const [consoleReply, setConsoleReply] = useState<McpConsoleReply | null>(null);
  const [consoleStream, setConsoleStream] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('deterministic');
  const [connectorResult, setConnectorResult] = useState<string>('');
  const [orchCodeProfile, setOrchCodeProfile] = useState<OrchCodeProfile | null>(null);
  const [labsAnalytics, setLabsAnalytics] = useState<LabsAnalytics | null>(null);
  const [draggedTaskId, setDraggedTaskId] = useState<number | null>(null);
  const ws = useRef<WebSocket | null>(null);

  const activeRoom = coworkRooms.find((room) => room.id === activeRoomId) ?? coworkRooms[0] ?? null;
  const completedExecutionTasks = executionPlan.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionTasksPhase6Plus = executionPlanPhase6Plus.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionLeadDev2 = executionPlanLeadDev2.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionDev2Dev3 = executionPlanDev2Dev3.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionDev2Dev3Cycle2 = executionPlanDev2Dev3Cycle2.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);

  const fetchSessions = async () => setSessions(await (await fetch(`${apiBase}/sessions`)).json());
  const fetchLabsOverview = async () => setLabsOverview(await (await fetch(`${apiBase}/api/labs/overview`)).json());
  const fetchLabsAnalytics = async () => setLabsAnalytics(await (await fetch(`${apiBase}/api/labs/analytics`)).json());
  const fetchOrchCodeControls = async () => setOrchCodeProfile(await (await fetch(`${apiBase}/api/labs/orch-code/controls`)).json());
  const fetchCoworkRooms = async () => {
    const data = await (await fetch(`${apiBase}/api/labs/cowork/rooms`)).json();
    setCoworkRooms(data.rooms);
    if (!activeRoomId && data.rooms.length > 0) await fetchCoworkRoomDetail(data.rooms[0].id);
  };
  const fetchCoworkRoomDetail = async (roomId: number) => {
    const data = await (await fetch(`${apiBase}/api/labs/cowork/rooms/${roomId}`)).json();
    const room: CoworkRoom = data.room;
    setCoworkRooms((prev) => [room, ...prev.filter((entry) => entry.id !== roomId)].sort((a, b) => b.id - a.id));
    setActiveRoomId(roomId);
  };
  const refreshLabs = async (roomId?: number) => {
    await fetchCoworkRooms();
    if (roomId) await fetchCoworkRoomDetail(roomId);
    await fetchLabsAnalytics();
    await fetchOrchCodeControls();
  };

  useEffect(() => {
    ws.current = new WebSocket(`${apiBase.replace('http', 'ws')}/ws/live`);
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'thinking') { setThinkingAgent(data.agent); setActiveAgent(null); }
      if (data.type === 'response') { setThinkingAgent(null); setActiveAgent(data.agent); setMessages((prev) => [...prev, data]); setTimeout(() => setActiveAgent(null), 5000); }
      if (data.type === 'override') {
        setSelectedSession((prev) => prev ? ({ ...prev, rounds: prev.rounds?.map((round) => ({ ...round, blocks: round.blocks.map((block) => block.block_id === data.block_id ? { ...block, override_score: data.override_score, improvement_hint: data.improvement_hint } : block) })) }) : null);
      }
    };
    void fetchSessions(); void fetchLabsOverview(); void fetchCoworkRooms(); void fetchLabsAnalytics(); void fetchOrchCodeControls();
    return () => ws.current?.close();
  }, []);

  const postJson = async (url: string, body: object) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const createCoworkRoom = async () => { const data = await (await postJson(`${apiBase}/api/labs/cowork/rooms`, { name: roomName, mission: roomMission, lead: 'Lead' })).json(); await refreshLabs(data.room.id); };
  const createArtifact = async () => {
    if (!activeRoom) return;
    if (editingArtifactId) {
      await postJson(`${apiBase}/api/labs/cowork/artifacts/${editingArtifactId}/edit`, { artifact_type: artifactType, title: artifactTitle, summary: artifactSummary, status: 'draft', link: 'Orch Forge' });
      setEditingArtifactId(null);
    } else {
      await postJson(`${apiBase}/api/labs/cowork/rooms/${activeRoom.id}/artifacts`, { artifact_type: artifactType, title: artifactTitle, summary: artifactSummary, status: 'draft', link: 'Orch Forge' });
    }
    await refreshLabs(activeRoom.id);
  };
  const createOrUpdateTask = async () => {
    if (!activeRoom) return;
    if (editingTaskId) {
      await postJson(`${apiBase}/api/labs/cowork/tasks/${editingTaskId}/edit`, { title: taskTitle, description: taskDescription, owner: taskOwner, priority: taskPriority });
      setEditingTaskId(null);
    } else {
      await postJson(`${apiBase}/api/labs/cowork/rooms/${activeRoom.id}/tasks`, { title: taskTitle, description: taskDescription, owner: taskOwner, priority: taskPriority, lane: 'build' });
    }
    await refreshLabs(activeRoom.id);
  };
  const updateTaskStatus = async (taskId: number, status: string) => { await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/status`, { status }); if (activeRoom) await refreshLabs(activeRoom.id); };
  const updateTaskOwner = async (taskId: number, owner: string) => { await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/owner`, { owner }); if (activeRoom) await refreshLabs(activeRoom.id); };
  const moveTaskToLane = async (taskId: number, lane: string) => { await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/lane`, { lane }); if (activeRoom) await refreshLabs(activeRoom.id); };
  const runConnectorAction = async (actionId: string) => {
    const data = await (await postJson(`${apiBase}/api/labs/connectors/actions/execute`, { action_id: actionId })).json();
    setConnectorResult([data.title, data.summary, ...(data.commands ?? []), ...(data.next_steps ?? [])].join('\n'));
  };
  const sendConsoleMessage = async () => {
    const data = await (await postJson(`${apiBase}/api/labs/mcp-console/chat`, { message: consoleMessage, session_id: consoleReply?.session_id ?? null, model_preference: selectedModel === 'deterministic' ? null : selectedModel })).json();
    setConsoleReply(data);
    setConsoleStream(data.response);
    await fetchLabsAnalytics();
  };
  const streamConsoleMessage = async () => {
    setConsoleStream('');
    const response = await fetch(`${apiBase}/api/labs/mcp-console/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: consoleMessage, session_id: consoleReply?.session_id ?? null, model_preference: selectedModel === 'deterministic' ? null : selectedModel }),
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
    }
    await fetchLabsAnalytics();
  };
  const teachOrchCode = async () => { await postJson(`${apiBase}/api/labs/orch-code/teach`, {}); await fetchOrchCodeControls(); };
  const updateLessonStatus = async (lessonKey: string, status: LessonState, confidence: number) => { await postJson(`${apiBase}/api/labs/orch-code/lessons/${lessonKey}/status`, { status, confidence }); await fetchOrchCodeControls(); };
  const loadSession = async (id: string) => { setViewMode('council'); setIsAuditMode(true); setSelectedSession(await (await fetch(`${apiBase}/sessions/${id}`)).json()); };
  const overrideScore = async (blockId: string, score: number) => { if (selectedSession) await postJson(`${apiBase}/sessions/${selectedSession.id}/override`, { block_id: blockId, override_score: score }); };

  return (
    <div className="command-center">
      <div className="sidebar">
        <div className="sidebar-header"><div className="sidebar-title">ORCH CONTROL</div></div>
        <div className="lesson-list">
          <div className={`lesson-item ${viewMode === 'council' && !isAuditMode ? 'active' : ''}`} onClick={() => { setViewMode('council'); setIsAuditMode(false); }}>
            <div className="lesson-topic">LIVE COUNCIL</div><div className="lesson-date">Real-time apprenticeship</div>
          </div>
          <div className={`lesson-item ${viewMode === 'labs' ? 'active' : ''}`} onClick={() => { setViewMode('labs'); setIsAuditMode(false); }}>
            <div className="lesson-topic">ORCH LABS</div><div className="lesson-date">Creator orchestration, connectors, and cloud demos</div>
          </div>
          <div className="sidebar-section-label">SESSION VAULT</div>
          {sessions.map((session) => (
            <div key={session.id} className={`lesson-item ${selectedSession?.id === session.id && isAuditMode ? 'active' : ''}`} onClick={() => void loadSession(session.id)}>
              <div className="lesson-topic">SESSION: {session.topic}</div><div className="lesson-date">{new Date(session.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="main-room">
        {viewMode === 'labs' ? (
          <div className="labs-shell">
            <section className="labs-hero">
              <div className="labs-kicker">ORCH LABS</div>
              <h1>{labsOverview?.title ?? 'Orch Labs'}</h1>
              <p>{labsOverview?.positioning ?? 'Execution surfaces for creator-grade AI workflows.'}</p>
              <div className="labs-metrics">
                <div className="metric-card"><span className="metric-value">{labsOverview?.metrics.tools ?? 0}</span><span className="metric-label">Tools</span></div>
                <div className="metric-card"><span className="metric-value">{labsOverview?.metrics.interfaces ?? 0}</span><span className="metric-label">Interfaces</span></div>
                <div className="metric-card"><span className="metric-value">{labsOverview?.metrics.cloud_stacks ?? 0}</span><span className="metric-label">Cloud Stacks</span></div>
                <div className="metric-card"><span className="metric-value">{labsAnalytics?.forge.rooms ?? 0}</span><span className="metric-label">Forge Rooms</span></div>
                <div className="metric-card"><span className="metric-value">{labsAnalytics?.forge.artifacts ?? 0}</span><span className="metric-label">Artifacts</span></div>
                <div className="metric-card"><span className="metric-value">{labsAnalytics?.mcp_console.requests ?? 0}</span><span className="metric-label">Console Requests</span></div>
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">20 Task Execution Matrix</div>
              <article className="labs-card execution-summary-card">
                <div className="tool-card-top">
                  <h3>Program Status</h3>
                  <div className="card-chip">{completedExecutionTasks}/20 complete</div>
                </div>
                <div className="execution-progress-track">
                  <div className="execution-progress-fill" style={{ width: `${(completedExecutionTasks / 20) * 100}%` }} />
                </div>
              </article>
              <div className="labs-grid phases-grid">
                {executionPlan.map((phase) => {
                  const complete = phase.tasks.filter((task) => task.done).length;
                  return (
                    <article key={phase.id} className="labs-card phase-card">
                      <div className="tool-card-top">
                        <h3>{phase.title}</h3>
                        <div className="card-chip">{complete}/4 complete</div>
                      </div>
                      <p>{phase.focus}</p>
                      <div className="deliverables-list">
                        {phase.tasks.map((task) => (
                          <div key={task.id} className={`deliverable-item execution-task ${task.done ? 'done' : 'todo'}`}>
                            {task.done ? 'DONE' : 'TODO'} · {task.label}
                          </div>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">20 Task Execution Matrix (Phase 6+)</div>
              <article className="labs-card execution-summary-card">
                <div className="tool-card-top">
                  <h3>Program Status</h3>
                  <div className="card-chip">{completedExecutionTasksPhase6Plus}/20 complete</div>
                </div>
                <div className="execution-progress-track">
                  <div className="execution-progress-fill" style={{ width: `${(completedExecutionTasksPhase6Plus / 20) * 100}%` }} />
                </div>
              </article>
              <div className="labs-grid phases-grid">
                {executionPlanPhase6Plus.map((phase) => {
                  const complete = phase.tasks.filter((task) => task.done).length;
                  return (
                    <article key={phase.id} className="labs-card phase-card">
                      <div className="tool-card-top">
                        <h3>{phase.title}</h3>
                        <div className="card-chip">{complete}/4 complete</div>
                      </div>
                      <p>{phase.focus}</p>
                      <div className="deliverables-list">
                        {phase.tasks.map((task) => (
                          <div key={task.id} className={`deliverable-item execution-task ${task.done ? 'done' : 'todo'}`}>
                            {task.done ? 'DONE' : 'TODO'} · {task.label}
                          </div>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">20 Task Matrix (Lead + DEV_2 + DEV_3 Background)</div>
              <article className="labs-card execution-summary-card">
                <div className="tool-card-top">
                  <h3>Squad Status</h3>
                  <div className="card-chip">{completedExecutionLeadDev2}/20 complete</div>
                </div>
                <div className="execution-progress-track">
                  <div className="execution-progress-fill" style={{ width: `${(completedExecutionLeadDev2 / 20) * 100}%` }} />
                </div>
              </article>
              <div className="labs-grid phases-grid">
                {executionPlanLeadDev2.map((phase) => {
                  const complete = phase.tasks.filter((task) => task.done).length;
                  return (
                    <article key={phase.id} className="labs-card phase-card">
                      <div className="tool-card-top">
                        <h3>{phase.title}</h3>
                        <div className="card-chip">{complete}/4 complete</div>
                      </div>
                      <p>{phase.focus}</p>
                      <div className="deliverables-list">
                        {phase.tasks.map((task) => (
                          <div key={task.id} className={`deliverable-item execution-task ${task.done ? 'done' : 'todo'}`}>
                            {task.done ? 'DONE' : 'TODO'} · {task.label}
                            <span className="owner-badge">{task.owner}</span>
                          </div>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">20 Task Matrix (4 Phases: DEV_2=5, DEV_3=10)</div>
              <article className="labs-card execution-summary-card">
                <div className="tool-card-top">
                  <h3>Allocation Status</h3>
                  <div className="card-chip">{completedExecutionDev2Dev3}/20 complete</div>
                </div>
                <div className="execution-progress-track">
                  <div className="execution-progress-fill" style={{ width: `${(completedExecutionDev2Dev3 / 20) * 100}%` }} />
                </div>
                <div className="forge-summary-strip">
                  <div>DEV_2: 5 tasks</div>
                  <div>DEV_3: 10 tasks</div>
                  <div>Lead: 5 tasks</div>
                </div>
              </article>
              <div className="labs-grid phases-grid">
                {executionPlanDev2Dev3.map((phase) => {
                  const complete = phase.tasks.filter((task) => task.done).length;
                  return (
                    <article key={phase.id} className="labs-card phase-card">
                      <div className="tool-card-top">
                        <h3>{phase.title}</h3>
                        <div className="card-chip">{complete}/5 complete</div>
                      </div>
                      <p>{phase.focus}</p>
                      <div className="deliverables-list">
                        {phase.tasks.map((task) => (
                          <div key={task.id} className={`deliverable-item execution-task ${task.done ? 'done' : 'todo'}`}>
                            {task.done ? 'DONE' : 'TODO'} · {task.label}
                            <span className="owner-badge">{task.owner}</span>
                          </div>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">20 Task Matrix Cycle 2 (4 Phases: DEV_2=5, DEV_3=10)</div>
              <article className="labs-card execution-summary-card">
                <div className="tool-card-top">
                  <h3>Allocation Status</h3>
                  <div className="card-chip">{completedExecutionDev2Dev3Cycle2}/20 complete</div>
                </div>
                <div className="execution-progress-track">
                  <div className="execution-progress-fill" style={{ width: `${(completedExecutionDev2Dev3Cycle2 / 20) * 100}%` }} />
                </div>
                <div className="forge-summary-strip">
                  <div>DEV_2: 5 tasks</div>
                  <div>DEV_3: 10 tasks</div>
                  <div>Lead: 5 tasks</div>
                </div>
              </article>
              <div className="labs-grid phases-grid">
                {executionPlanDev2Dev3Cycle2.map((phase) => {
                  const complete = phase.tasks.filter((task) => task.done).length;
                  return (
                    <article key={phase.id} className="labs-card phase-card">
                      <div className="tool-card-top">
                        <h3>{phase.title}</h3>
                        <div className="card-chip">{complete}/5 complete</div>
                      </div>
                      <p>{phase.focus}</p>
                      <div className="deliverables-list">
                        {phase.tasks.map((task) => (
                          <div key={task.id} className={`deliverable-item execution-task ${task.done ? 'done' : 'todo'}`}>
                            {task.done ? 'DONE' : 'TODO'} · {task.label}
                            <span className="owner-badge">{task.owner}</span>
                          </div>
                        ))}
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Orch Interfaces</div>
              <div className="labs-grid categories-grid">
                {labsOverview?.orch_interfaces.map((item) => (
                  <article key={item.id} className="labs-card category-card">
                    <div className="tool-card-top"><div className="card-chip">{item.status}</div><div className="criticality-pill building">mechanics</div></div>
                    <h3>{item.name}</h3>
                    <p>{item.summary}</p>
                    <div className="deliverables-list">{item.mechanics.map((mechanic) => <div key={mechanic} className="deliverable-item">{mechanic}</div>)}</div>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section split-section">
              <div className="split-panel">
                <div className="section-heading">Cloud Expansion</div>
                <div className="labs-grid access-grid">
                  {labsOverview?.cloud_stacks.map((stack) => (
                    <article key={stack.id} className="labs-card phase-card">
                      <div className="tool-card-top"><div className={`criticality-pill ${stack.priority}`}>{criticalityLabel(stack.priority)}</div><div className="card-chip">{stack.provider}</div></div>
                      <h3>{stack.name}</h3>
                      <p>{stack.summary}</p>
                      <div className="deliverables-list">{stack.focus.map((focus) => <div key={focus} className="deliverable-item">{focus}</div>)}</div>
                    </article>
                  ))}
                </div>
              </div>
              <div className="split-panel">
                <div className="section-heading">Connector Workflows</div>
                <div className="labs-grid access-grid">
                  {labsOverview?.connector_workflows.map((workflow) => (
                    <article key={workflow.id} className="labs-card compact-card">
                      <div className="tool-card-top"><h3>{workflow.name}</h3><div className="card-chip">{workflow.status}</div></div>
                      <p>{workflow.summary}</p>
                    </article>
                  ))}
                </div>
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Installer And Connector Actions</div>
              <div className="labs-grid access-grid">
                {labsOverview?.installer_actions.map((action) => (
                  <article key={action.id} className="labs-card compact-card">
                    <div className="tool-card-top"><h3>{action.title}</h3><div className="card-chip">{action.surface}</div></div>
                    <p>{action.summary}</p>
                    <button type="button" className="forge-button" onClick={() => void runConnectorAction(action.id)}>Run Playbook</button>
                  </article>
                ))}
              </div>
              {connectorResult && <article className="labs-card console-reply-card"><pre className="connector-output">{connectorResult}</pre></article>}
            </section>

            <section className="labs-section">
              <div className="section-heading">South Africa Tool Catalog</div>
              <div className="labs-grid tools-grid">
                {labsOverview?.tools.map((tool) => (
                  <article key={tool.id} className="labs-card tool-card">
                    <div className="tool-card-top"><div className="card-chip">{tool.phase}</div><div className={`criticality-pill ${tool.criticality}`}>{criticalityLabel(tool.criticality)}</div></div>
                    <h3>{tool.name}</h3>
                    <div className="tool-meta">{tool.category} · {tool.status}</div>
                    <p>{tool.summary}</p>
                    <div className="impact-label">Impact</div>
                    <div className="impact-copy">{tool.impact}</div>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Orch Forge Live</div>
              <div className="forge-shell">
                <article className="labs-card forge-create-card">
                  <div className="tool-card-top"><h3>Premiere A Forge</h3><div className="criticality-pill high">LIVE</div></div>
                  <label className="forge-label"><span>Name</span><input value={roomName} onChange={(e) => setRoomName(e.target.value)} className="forge-input" /></label>
                  <label className="forge-label"><span>Mission</span><textarea value={roomMission} onChange={(e) => setRoomMission(e.target.value)} className="forge-textarea" rows={3} /></label>
                  <button type="button" className="forge-button" onClick={() => void createCoworkRoom()}>Launch Orch Forge</button>
                </article>

                <article className="labs-card forge-rooms-card">
                  <div className="tool-card-top"><h3>Forge Rooms</h3><div className="card-chip">{coworkRooms.length} rooms</div></div>
                  <div className="forge-room-list">
                    {coworkRooms.map((room) => (
                      <button key={room.id} type="button" className={`forge-room-button ${activeRoom?.id === room.id ? 'active' : ''}`} onClick={() => void fetchCoworkRoomDetail(room.id)}>
                        <span>{room.name}</span><span>{room.status}</span>
                      </button>
                    ))}
                  </div>
                </article>
              </div>

              {activeRoom && (
                <article className="labs-card forge-room-detail">
                  <div className="tool-card-top">
                    <div><div className="section-heading">Active Forge</div><h3>{activeRoom.name}</h3></div>
                    <div className="forge-summary-strip">
                      <div>{activeRoom.dispatch_summary.total_tasks} total</div>
                      <div>{activeRoom.dispatch_summary.in_progress} active</div>
                      <div>{activeRoom.dispatch_summary.completed} done</div>
                      <div>{activeRoom.artifact_summary.total_artifacts} artifacts</div>
                    </div>
                  </div>
                  <p>{activeRoom.mission}</p>
                  <div className="forge-lanes">
                    {laneOrder.map((lane) => (
                      <div key={lane} className="forge-lane" onDragOver={(event) => event.preventDefault()} onDrop={() => { if (draggedTaskId !== null) { void moveTaskToLane(draggedTaskId, lane); setDraggedTaskId(null); } }}>
                        <div className="forge-lane-header">{lane}</div>
                        {(activeRoom.lanes[lane] ?? []).map((task) => (
                          <div key={task.id} className="forge-task" draggable onDragStart={() => setDraggedTaskId(task.id)} onDragEnd={() => setDraggedTaskId(null)}>
                            <div className="tool-card-top"><strong>{task.title}</strong><div className={`criticality-pill ${task.priority}`}>{criticalityLabel(task.priority)}</div></div>
                            <p>{task.description}</p>
                            <div className="forge-controls">
                              <select value={task.owner} className="forge-select" onChange={(e) => void updateTaskOwner(task.id, e.target.value)}>{ownerOptions.map((owner) => <option key={owner} value={owner}>{owner}</option>)}</select>
                              <select value={task.status} className="forge-select" onChange={(e) => void updateTaskStatus(task.id, e.target.value)}>
                                <option value="queued">queued</option><option value="in_progress">in progress</option><option value="completed">completed</option>
                              </select>
                            </div>
                            <button
                              type="button"
                              className="ghost-button"
                              onClick={() => {
                                const editable = toEditableTask(task);
                                setEditingTaskId(editable.id);
                                setTaskTitle(editable.title);
                                setTaskDescription(editable.description);
                                setTaskOwner(editable.owner);
                                setTaskPriority(editable.priority);
                              }}
                            >
                              Edit Task
                            </button>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                  <div className="forge-artifact-layout">
                    <article className="labs-card forge-artifact-create">
                      <div className="tool-card-top"><h3>{editingTaskId ? 'Edit Task' : 'Add Task'}</h3><div className="card-chip">forge lane work</div></div>
                      <label className="forge-label"><span>Title</span><input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} className="forge-input" /></label>
                      <label className="forge-label"><span>Description</span><textarea value={taskDescription} onChange={(e) => setTaskDescription(e.target.value)} className="forge-textarea" rows={3} /></label>
                      <div className="forge-controls">
                        <select value={taskOwner} className="forge-select" onChange={(e) => setTaskOwner(e.target.value)}>{ownerOptions.map((owner) => <option key={owner} value={owner}>{owner}</option>)}</select>
                        <select value={taskPriority} className="forge-select" onChange={(e) => setTaskPriority(e.target.value)}><option value="critical">critical</option><option value="high">high</option><option value="building">building</option></select>
                      </div>
                      <button type="button" className="forge-button" onClick={() => void createOrUpdateTask()}>{editingTaskId ? 'Save Task' : 'Add Task'}</button>
                    </article>
                    <article className="labs-card forge-artifact-create">
                      <div className="tool-card-top"><h3>{editingArtifactId ? 'Edit Artifact' : 'Add Artifact'}</h3><div className="card-chip">prompt · api · screen · note</div></div>
                      <label className="forge-label"><span>Type</span><select value={artifactType} className="forge-select" onChange={(e) => setArtifactType(e.target.value)}><option value="prompt">prompt</option><option value="api">api</option><option value="screen">screen</option><option value="note">note</option></select></label>
                      <label className="forge-label"><span>Title</span><input value={artifactTitle} onChange={(e) => setArtifactTitle(e.target.value)} className="forge-input" /></label>
                      <label className="forge-label"><span>Summary</span><textarea value={artifactSummary} onChange={(e) => setArtifactSummary(e.target.value)} className="forge-textarea" rows={3} /></label>
                      <button type="button" className="forge-button" onClick={() => void createArtifact()}>{editingArtifactId ? 'Save Artifact' : 'Add Artifact Card'}</button>
                    </article>
                  </div>
                  <div className="forge-artifact-layout">
                    <div className="artifact-grid">
                      {activeRoom.artifacts.map((artifact) => (
                        <article key={artifact.id} className="labs-card artifact-card">
                          <div className="tool-card-top"><div className="card-chip">{artifact.artifact_type}</div><div className="card-chip">{artifact.status}</div></div>
                          <h3>{artifact.title}</h3>
                          <p>{artifact.summary}</p>
                          {artifact.link && <div className="artifact-link">{artifact.link}</div>}
                          <button type="button" className="ghost-button" onClick={() => { const editable = toEditableArtifact(artifact); setEditingArtifactId(editable.id); setArtifactType(editable.artifact_type); setArtifactTitle(editable.title); setArtifactSummary(editable.summary); }}>Edit Artifact</button>
                        </article>
                      ))}
                    </div>
                  </div>
                </article>
              )}
            </section>

            <section className="labs-section split-section">
              <div className="split-panel">
                <div className="section-heading">Orch Code Controls</div>
                <article className="labs-card forge-room-detail">
                  <div className="tool-card-top"><h3>{orchCodeProfile?.title ?? 'Orch Code'}</h3><button type="button" className="forge-button secondary-button" onClick={() => void teachOrchCode()}>Teach From Repo</button></div>
                  <div className="forge-summary-strip"><div>{orchCodeProfile?.summary.total_lessons ?? 0} lessons</div><div>{orchCodeProfile?.summary.learned_lessons ?? 0} learned</div><div>{orchCodeProfile?.summary.learning_lessons ?? 0} in flight</div></div>
                  <div className="lesson-control-list">
                    {orchCodeProfile?.lessons.map((lesson) => (
                      <div key={lesson.lesson_key} className="lesson-control-card">
                        <div className="tool-card-top"><strong>{lesson.title}</strong><div className="card-chip">{lesson.track}</div></div>
                        <div className="tool-meta">{lesson.source}</div>
                        <div className="forge-controls">
                          <select value={lesson.status} className="forge-select" onChange={(e) => void updateLessonStatus(lesson.lesson_key, e.target.value as LessonState, lesson.confidence)}>{orchCodeProfile.control_states.map((state) => <option key={state} value={state}>{state}</option>)}</select>
                          <input type="range" min="0" max="100" value={lesson.confidence} className="glow-knob" onChange={(e) => void updateLessonStatus(lesson.lesson_key, lesson.status, Number(e.target.value))} />
                        </div>
                      </div>
                    ))}
                  </div>
                </article>
              </div>
              <div className="split-panel">
                <div className="section-heading">Universal MCP Console</div>
                <div className="labs-card forge-room-detail">
                  <div className="tool-card-top"><h3>MCP Chat</h3><div className="criticality-pill high">Model-backed</div></div>
                  <label className="forge-label"><span>Model</span><select value={selectedModel} className="forge-select" onChange={(e) => setSelectedModel(e.target.value)}>{(consoleReply?.model_options ?? [{ id: 'deterministic', label: 'deterministic fallback', model: 'deterministic-fallback' }]).map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}</select></label>
                  <label className="forge-label"><span>Ask About IDE, OS, CLI, Skills, Connectors, Azure, Or AWS</span><textarea value={consoleMessage} onChange={(e) => setConsoleMessage(e.target.value)} className="forge-textarea" rows={4} /></label>
                  <div className="forge-controls">
                    <button type="button" className="forge-button" onClick={() => void sendConsoleMessage()}>Send To MCP Console</button>
                    <button type="button" className="forge-button secondary-button" onClick={() => void streamConsoleMessage()}>Stream Reply</button>
                  </div>
                  <div className="console-reply-card">
                    <div className="tool-card-top"><div className="card-chip">{consoleReply?.topic ?? 'waiting'}</div><div className="card-chip">{consoleReply?.model_used ?? 'deterministic-fallback'}</div></div>
                    <p>{consoleStream || consoleReply?.response || 'Ask a question to get orchestration guidance and connector next steps.'}</p>
                    {consoleReply && <>
                      <div className="section-heading">Suggested Actions</div>
                      <div className="deliverables-list">{consoleReply.suggested_actions.map((action) => <div key={action} className="deliverable-item">{action}</div>)}</div>
                      <div className="section-heading">Surfaces</div>
                      <div className="forge-summary-strip">{consoleReply.surfaces.map((surface) => <div key={surface}>{surface}</div>)}</div>
                    </>}
                  </div>
                </div>
              </div>
            </section>

            <section className="labs-section split-section">
              <div className="split-panel">
                <div className="section-heading">Creator Throughput</div>
                <div className="labs-grid access-grid">
                  {labsAnalytics?.forge.creator_throughput.map((entry) => (
                    <article key={entry.owner} className="labs-card compact-card">
                      <div className="tool-card-top"><h3>{entry.owner}</h3><div className="card-chip">{entry.count} tasks</div></div>
                      <p>Measured from persisted Forge ownership and movement events.</p>
                    </article>
                  ))}
                </div>
              </div>
              <div className="split-panel">
                <div className="section-heading">Console Analytics</div>
                <div className="labs-grid access-grid">
                  <article className="labs-card compact-card">
                    <div className="tool-card-top"><h3>Usage</h3><div className="card-chip">{labsAnalytics?.mcp_console.requests ?? 0} requests</div></div>
                    <p>Sessions: {labsAnalytics?.mcp_console.sessions ?? 0} · Avg latency: {labsAnalytics?.mcp_console.average_latency_ms ?? 0} ms</p>
                  </article>
                  {labsAnalytics?.mcp_console.top_topics.map((topic) => (
                    <article key={topic.topic} className="labs-card compact-card">
                      <div className="tool-card-top"><h3>{topic.topic}</h3><div className="card-chip">{topic.count}</div></div>
                      <p>Persisted MCP console topic frequency for workflow prioritization.</p>
                    </article>
                  ))}
                </div>
              </div>
            </section>
          </div>
        ) : !isAuditMode ? (
          agentList.map((id) => {
            const isStudent = id === 'orch';
            const isThinking = thinkingAgent === id;
            const isResponding = activeAgent === id;
            const lastMsg = messages.filter((message) => message.agent === id).slice(-1)[0];
            return (
              <div key={id} className={`chamber ${id} ${isThinking ? 'thinking' : ''} ${isResponding ? 'responding' : ''} ${isStudent ? 'student' : 'mentor'}`}>
                <div className="agent-rank">{isStudent ? '[STUDENT]' : '[MENTOR]'}</div>
                <div className="agent-id">{id}</div>
                {isThinking && <div className="glow-orb" />}
                <div className="response-text">{isThinking ? (isStudent ? 'SYNTHESIZING DEEP REASONING...' : 'PROVIDING EXPERT ADVICE...') : lastMsg?.content || 'STANDBY...'}</div>
                {(lastMsg?.value_score !== undefined || lastMsg?.override_score !== undefined) && <div className="value-meter"><div className="value-fill" style={{ width: `${(lastMsg.override_score ?? lastMsg.value_score ?? 0) * 10}%` }} /></div>}
              </div>
            );
          })
        ) : (
          <div className="audit-container">
            <div className="sidebar-title">Forensic Audit: {selectedSession?.topic}</div>
            {selectedSession?.rounds?.map((round) => (
              <div key={round.id} className="round-section">
                <div className="sidebar-title audit-round">ROUND {round.round_number} ANALYSIS</div>
                {round.blocks.map((block) => (
                  <div key={block.block_id} className={`audit-card ${block.is_student ? 'student' : 'mentor'}`}>
                    <div className="card-header"><div className="card-agent">{block.agent.toUpperCase()}</div><div className="value-tag">MASTER SCORE: {block.override_score ?? block.value_score ?? 0}/10</div></div>
                    <div className="thought-body thought-primary">{block.content}</div>
                    <div className="thought-body">Reasoning Trace: {block.reasoning}</div>
                    <div className="override-container"><input type="range" min="0" max="10" value={block.override_score ?? block.value_score ?? 0} className="glow-knob" aria-label="Master Override Logic Score" onChange={(e) => void overrideScore(block.block_id, parseInt(e.target.value, 10))} /></div>
                    {block.improvement_hint && <div className="improvement-hint">Master Hint: {block.improvement_hint}</div>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
