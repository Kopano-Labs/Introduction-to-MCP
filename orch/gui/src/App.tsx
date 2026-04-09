import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import { appendStreamChunk, toEditableArtifact, toEditableTask } from './labsUi';

type ViewMode = 'council' | 'labs' | 'admin';
type LessonState = 'queued' | 'learning' | 'learned' | 'shipping';
type LabsSection = 'interfaces' | 'cloud' | 'actions' | 'tools' | 'forge' | 'console';

interface ReasoningBlock { block_id: string; agent: string; role: string | null; content: string; reasoning: string; value_score: number; override_score: number | null; improvement_hint: string | null; is_student: number; }
interface Round { id: string; round_number: number; blocks: ReasoningBlock[]; }
interface Lesson { id: string; topic: string; created_at: string; rounds?: Round[]; audit_events?: number; round_count?: number; }
interface LiveMessage { type: string; agent: string; block_id: string; content: string; reasoning: string; round: number; value_score?: number; override_score?: number; improvement_hint?: string; }
interface GuiUser { id: number; email: string; full_name?: string | null; role: string; god_mode: boolean; is_active: boolean; created_at: string; }
interface FeedLogEntry { id: string; type: string; agent?: string; content?: string; reasoning?: string; round?: number; received_at: string; source: 'ws' | 'poll' | 'system'; }
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
const executionPlanDev2Dev3LeadPhase: SquadPhase[] = [
  { id: 'phase-24', title: 'Phase 24', focus: 'Platform Rollout', tasks: [
    { id: 'p24-t1', label: 'Deployment command validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p24-t2', label: 'Environment parity verification', owner: 'DEV_2', done: true },
    { id: 'p24-t3', label: 'Rollback rehearsal evidence', owner: 'DEV_3 (Background)', done: true },
    { id: 'p24-t4', label: 'Build package integrity scan', owner: 'DEV_3 (Background)', done: true },
    { id: 'p24-t5', label: 'Release checklist confirmation', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-25', title: 'Phase 25', focus: 'Observability & Operations', tasks: [
    { id: 'p25-t1', label: 'Runtime log quality pass', owner: 'DEV_3 (Background)', done: true },
    { id: 'p25-t2', label: 'Alert threshold verification', owner: 'DEV_2', done: true },
    { id: 'p25-t3', label: 'Telemetry stream consistency check', owner: 'DEV_3 (Background)', done: true },
    { id: 'p25-t4', label: 'Incident routing validation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p25-t5', label: 'Ops signoff note', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-26', title: 'Phase 26', focus: 'Security & Reliability', tasks: [
    { id: 'p26-t1', label: 'Dependency risk triage', owner: 'DEV_3 (Background)', done: true },
    { id: 'p26-t2', label: 'Access-control change audit', owner: 'DEV_2', done: true },
    { id: 'p26-t3', label: 'Backup restore confirmation', owner: 'DEV_3 (Background)', done: true },
    { id: 'p26-t4', label: 'Failure-mode checklist run', owner: 'DEV_3 (Background)', done: true },
    { id: 'p26-t5', label: 'Reliability signoff capture', owner: 'DEV_2', done: true },
  ]},
  { id: 'phase-27', title: 'Phase 27', focus: 'Lead Solo Phase', tasks: [
    { id: 'p27-t1', label: 'Cross-phase acceptance review', owner: 'Lead', done: true },
    { id: 'p27-t2', label: 'Final UX readiness decision', owner: 'Lead', done: true },
    { id: 'p27-t3', label: 'Quality gate final approval', owner: 'Lead', done: true },
    { id: 'p27-t4', label: 'Delivery summary and handoff', owner: 'Lead', done: true },
    { id: 'p27-t5', label: 'Session compliance closeout', owner: 'Lead', done: true },
  ]},
];

const App: React.FC = () => {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<'connecting' | 'live' | 'error'>('connecting');
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
  const [isAuditMode, setIsAuditMode] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('council');
  const [labsSection, setLabsSection] = useState<LabsSection>('forge');
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
  const [adminUser, setAdminUser] = useState<GuiUser | null>(null);
  const [adminEmail, setAdminEmail] = useState('admin@orch.local');
  const [adminPassword, setAdminPassword] = useState('demo-admin');
  const [adminError, setAdminError] = useState<string | null>(null);
  const [adminLoading, setAdminLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const seenFeedIds = useRef<Set<string>>(new Set(['system-ready']));

  const activeRoom = coworkRooms.find((room) => room.id === activeRoomId) ?? coworkRooms[0] ?? null;
  const isAdminLoggedIn = adminUser?.role === 'admin';
  const completedExecutionTasks = executionPlan.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionTasksPhase6Plus = executionPlanPhase6Plus.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionLeadDev2 = executionPlanLeadDev2.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionDev2Dev3 = executionPlanDev2Dev3.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionDev2Dev3Cycle2 = executionPlanDev2Dev3Cycle2.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const completedExecutionDev2Dev3LeadPhase = executionPlanDev2Dev3LeadPhase.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0);
  const featuredAgentId = activeAgent ?? thinkingAgent ?? 'orch';
  const latestTransmission = messages[messages.length - 1] ?? null;
  const councilCards = agentList.map((id) => {
    const lastMsg = messages.filter((message) => message.agent === id).slice(-1)[0];
    const isStudent = id === 'orch';
    const isThinking = thinkingAgent === id;
    const isResponding = activeAgent === id;

    return { id, lastMsg, isStudent, isThinking, isResponding };
  });
  const featuredCouncilCard = councilCards.find((card) => card.id === featuredAgentId) ?? councilCards[0];
  const supportCouncilCards = councilCards.filter((card) => card.id !== featuredCouncilCard.id);
  const latestFeedEntries = feedLog.slice(-10).reverse();
  const activeTopView: ViewMode = isAuditMode ? 'admin' : viewMode;
  const openView = (nextView: ViewMode) => {
    setIsAuditMode(false);
    setViewMode(nextView);
  };
  const openLabsSurface = (section?: LabsSection) => {
    setIsAuditMode(false);
    setViewMode('labs');
    if (section) {
      window.setTimeout(() => scrollToLabsSection(section), 80);
    }
  };
  const publicLaunchers: Array<{ label: string; detail: string; value: string; action: () => void; active: boolean }> = [
    {
      label: 'Live Council',
      detail: 'Follow the council and the current reasoning handoff.',
      value: connectionState === 'live' ? 'Live' : connectionState === 'connecting' ? 'Linking' : 'Recover',
      action: () => openView('council'),
      active: activeTopView === 'council',
    },
    {
      label: 'Interfaces',
      detail: 'Public routes, audience fit, and surface mechanics.',
      value: String(labsOverview?.metrics.interfaces ?? 0),
      action: () => openLabsSurface('interfaces'),
      active: viewMode === 'labs' && labsSection === 'interfaces' && !isAuditMode,
    },
    {
      label: 'Forge',
      detail: 'Create rooms, route work, and keep demos tangible.',
      value: String(labsAnalytics?.forge.rooms ?? 0),
      action: () => openLabsSurface('forge'),
      active: viewMode === 'labs' && labsSection === 'forge' && !isAuditMode,
    },
    {
      label: 'Console',
      detail: 'Ask Orch how to move across tools, clouds, and MCP.',
      value: String(labsAnalytics?.mcp_console.requests ?? 0),
      action: () => openLabsSurface('console'),
      active: viewMode === 'labs' && labsSection === 'console' && !isAuditMode,
    },
  ];
  const audienceSignals = [
    'Mobile-first, quick to scan, and comfortable inside chat-native flows.',
    'Calm enough for trust, sharp enough to feel current and creative.',
    'Built for creators, learners, operators, and founders moving fast.',
  ];
  const adminFeedPreview = latestFeedEntries.slice(0, 8);

  const pushFeedLog = (entry: FeedLogEntry) => {
    if (seenFeedIds.current.has(entry.id)) return;
    seenFeedIds.current.add(entry.id);
    setFeedLog((prev) => [...prev, entry].slice(-60));
  };

  const logSystemEvent = (type: string, content: string) => {
    const stamp = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    pushFeedLog({
      id: `system:${type}:${stamp}`,
      type,
      content,
      received_at: new Date().toISOString(),
      source: 'system',
    });
  };

  const handleLiveEvent = (data: Partial<LiveMessage> & { type?: string }, source: 'ws' | 'poll') => {
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
        if (prev.some((message) => message.block_id === data.block_id)) return prev;
        return [...prev, nextMessage];
      });
      window.setTimeout(() => setActiveAgent((current) => (current === data.agent ? null : current)), 5000);
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
  };

  const scrollToLabsSection = (section: LabsSection) => {
    setLabsSection(section);
    const target = document.getElementById(`labs-${section}`);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

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
    let isMounted = true;
    const savedAdmin = window.localStorage.getItem('orch-admin-user');
    if (savedAdmin) {
      try {
        setAdminUser(JSON.parse(savedAdmin) as GuiUser);
      } catch {
        window.localStorage.removeItem('orch-admin-user');
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
        if (!Array.isArray(updates)) return;
        updates.forEach((update) => handleLiveEvent(update, 'poll'));
        if (updates.length > 0) {
          setConnectionState('live');
        }
      } catch {
        setConnectionState((current) => (current === 'live' ? current : 'error'));
      }
    }, 4000);

    const loadInitialData = async () => {
      const [sessionsData, overviewData, analyticsData, orchCodeData, roomsPayload] = await Promise.all([
        fetch(`${apiBase}/sessions`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/overview`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/analytics`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/orch-code/controls`).then((response) => response.json()),
        fetch(`${apiBase}/api/labs/cowork/rooms`).then((response) => response.json()),
      ]);

      if (!isMounted) return;

      setSessions(sessionsData);
        setLabsOverview(overviewData);
        setLabsAnalytics(analyticsData);
        setOrchCodeProfile(orchCodeData);
        setCoworkRooms(roomsPayload.rooms);
        logSystemEvent('bootstrap', 'Labs overview, analytics, and session vault loaded.');

        if (roomsPayload.rooms.length > 0) {
          const detailPayload = await fetch(`${apiBase}/api/labs/cowork/rooms/${roomsPayload.rooms[0].id}`).then((response) => response.json());
          if (!isMounted) return;

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
  }, []);

  const postJson = async (url: string, body: object) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const createCoworkRoom = async () => {
    const data = await (await postJson(`${apiBase}/api/labs/cowork/rooms`, { name: roomName, mission: roomMission, lead: 'Lead' })).json();
    await refreshLabs(data.room.id);
    logSystemEvent('forge', `Forge room "${data.room.name}" launched for demo execution.`);
  };
  const createArtifact = async () => {
    if (!activeRoom) return;
    if (editingArtifactId) {
      await postJson(`${apiBase}/api/labs/cowork/artifacts/${editingArtifactId}/edit`, { artifact_type: artifactType, title: artifactTitle, summary: artifactSummary, status: 'draft', link: 'Orch Forge' });
      setEditingArtifactId(null);
    } else {
      await postJson(`${apiBase}/api/labs/cowork/rooms/${activeRoom.id}/artifacts`, { artifact_type: artifactType, title: artifactTitle, summary: artifactSummary, status: 'draft', link: 'Orch Forge' });
    }
    await refreshLabs(activeRoom.id);
    logSystemEvent('artifact', `Artifact "${artifactTitle}" saved in ${activeRoom.name}.`);
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
    logSystemEvent('task', `Task "${taskTitle}" routed to ${taskOwner} in ${activeRoom.name}.`);
  };
  const updateTaskStatus = async (taskId: number, status: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/status`, { status });
    if (activeRoom) await refreshLabs(activeRoom.id);
    logSystemEvent('task-status', `Task ${taskId} moved to ${status}.`);
  };
  const updateTaskOwner = async (taskId: number, owner: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/owner`, { owner });
    if (activeRoom) await refreshLabs(activeRoom.id);
    logSystemEvent('task-owner', `Task ${taskId} reassigned to ${owner}.`);
  };
  const moveTaskToLane = async (taskId: number, lane: string) => {
    await postJson(`${apiBase}/api/labs/cowork/tasks/${taskId}/lane`, { lane });
    if (activeRoom) await refreshLabs(activeRoom.id);
    logSystemEvent('task-lane', `Task ${taskId} dropped into the ${lane} lane.`);
  };
  const runConnectorAction = async (actionId: string) => {
    const data = await (await postJson(`${apiBase}/api/labs/connectors/actions/execute`, { action_id: actionId })).json();
    setConnectorResult([data.title, data.summary, ...(data.commands ?? []), ...(data.next_steps ?? [])].join('\n'));
    logSystemEvent('connector', `${data.title} executed from Orch Labs.`);
  };
  const sendConsoleMessage = async () => {
    const data = await (await postJson(`${apiBase}/api/labs/mcp-console/chat`, { message: consoleMessage, session_id: consoleReply?.session_id ?? null, model_preference: selectedModel === 'deterministic' ? null : selectedModel })).json();
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
      logSystemEvent('console-stream', `Streaming console reply completed on topic "${finalPayload.topic}".`);
    }
    await fetchLabsAnalytics();
  };
  const teachOrchCode = async () => {
    await postJson(`${apiBase}/api/labs/orch-code/teach`, {});
    await fetchOrchCodeControls();
    logSystemEvent('orch-code', 'Orch Code teaching pass completed from repo data.');
  };
  const updateLessonStatus = async (lessonKey: string, status: LessonState, confidence: number) => {
    await postJson(`${apiBase}/api/labs/orch-code/lessons/${lessonKey}/status`, { status, confidence });
    await fetchOrchCodeControls();
    logSystemEvent('lesson', `${lessonKey} moved to ${status} at ${confidence}% confidence.`);
  };
  const loadSession = async (id: string) => { setViewMode('admin'); setIsAuditMode(true); setSelectedSession(await (await fetch(`${apiBase}/sessions/${id}`)).json()); };
  const overrideScore = async (blockId: string, score: number) => { if (selectedSession) await postJson(`${apiBase}/sessions/${selectedSession.id}/override`, { block_id: blockId, override_score: score }); };
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
      window.localStorage.setItem('orch-admin-user', JSON.stringify(data.user));
      setViewMode('admin');
      logSystemEvent('admin-login', `Admin session opened for ${data.user.email}.`);
    } catch {
      setAdminError('Unable to reach the Orch auth service.');
    } finally {
      setAdminLoading(false);
    }
  };
  const logoutAdmin = () => {
    setAdminUser(null);
    setAdminError(null);
    window.localStorage.removeItem('orch-admin-user');
    setViewMode('labs');
    logSystemEvent('admin-logout', 'Admin session closed. Returned to public Labs.');
  };

  return (
    <div className={`command-center ${activeTopView === 'admin' ? 'theme-admin' : 'theme-public'}`}>
      <div className="main-room">
        <header className="orch-topbar">
          <button type="button" className="brand-lockup" onClick={() => openView('council')}>
            <span className="brand-mark">OR</span>
            <span className="brand-copy">
              <strong>Orch</strong>
              <span>South African AI operating shell</span>
            </span>
          </button>
          <nav className="topbar-nav" aria-label="Primary">
            <button type="button" className={`nav-button ${activeTopView === 'council' ? 'active' : ''}`} onClick={() => openView('council')}>Live Council</button>
            <button type="button" className={`nav-button ${activeTopView === 'labs' ? 'active' : ''}`} onClick={() => openView('labs')}>Orch Labs</button>
            <button type="button" className={`nav-button ${viewMode === 'labs' && labsSection === 'forge' && !isAuditMode ? 'active' : ''}`} onClick={() => openLabsSurface('forge')}>Forge</button>
            <button type="button" className={`nav-button ${viewMode === 'labs' && labsSection === 'console' && !isAuditMode ? 'active' : ''}`} onClick={() => openLabsSurface('console')}>Console</button>
            <button type="button" className={`nav-button ${activeTopView === 'admin' ? 'active' : ''}`} onClick={() => openView('admin')}>Admin</button>
          </nav>
          <div className="topbar-status">
            <div className={`status-pill ${connectionState}`}>
              {connectionState === 'live' ? 'Live link' : connectionState === 'connecting' ? 'Connecting' : 'Attention'}
            </div>
            <div className="status-pill neutral">{sessions.length} sessions</div>
            <div className={`status-pill ${isAdminLoggedIn ? 'live' : 'neutral'}`}>
              {isAdminLoggedIn ? 'Admin unlocked' : 'Public mode'}
            </div>
          </div>
        </header>
        {isAuditMode ? (
          <div className="audit-container">
            <div className="sidebar-title">Forensic Audit: {selectedSession?.topic}</div>
            {selectedSession?.rounds?.length ? (
              selectedSession.rounds.map((round) => (
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
              ))
            ) : (
              <article className="audit-card audit-empty-card">
                <div className="tool-card-top">
                  <h3>No forensic rounds recorded yet</h3>
                  <div className="card-chip">vault waiting</div>
                </div>
                <p>This session was stored without an audit trail. Pick a session with recorded rounds from the vault or run a fresh live council session before demo.</p>
              </article>
            )}
          </div>
        ) : viewMode === 'labs' ? (
          <div className="labs-shell">
            <section className="labs-hero labs-public-hero">
              <div className="labs-kicker">ORCH LABS</div>
              <h1>Build, test, and show the next move.</h1>
              <p>
                Orch Labs is now the public demo shell: cleaner, faster to scan, and built around real actions instead of internal dashboards.
                Session history and governance stay in the Admin portal.
              </p>
              <div className="hero-note-grid">
                <article className="signal-card">
                  <span className="signal-label">Made for</span>
                  <strong>Young South African AI users</strong>
                  <p>Fast-scanning structure, chat-native cues, and direct routes into the surfaces that matter.</p>
                </article>
                <article className="signal-card">
                  <span className="signal-label">Design Rule</span>
                  <strong>Public stays polished, admin stays internal</strong>
                  <p>The page carries real functionality without exposing the operator backplane or activity preview.</p>
                </article>
              </div>
              <div className="labs-metrics labs-function-grid top-launch-grid">
                {publicLaunchers.map((launcher) => (
                  <button key={launcher.label} type="button" className={`metric-card labs-function-card ${launcher.active ? 'active' : ''}`} onClick={launcher.action}>
                    <span className="metric-value">{launcher.value}</span>
                    <span className="metric-label">{launcher.label}</span>
                    <span className="metric-copy">{launcher.detail}</span>
                  </button>
                ))}
              </div>
            </section>

            <section id="labs-interfaces" className="labs-section">
              <div className="section-heading">Public Interfaces</div>
              <div className="labs-grid access-grid">
                {audienceSignals.map((signal) => (
                  <article key={signal} className="labs-card compact-card">
                    <div className="card-chip">audience fit</div>
                    <p>{signal}</p>
                  </article>
                ))}
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

            <section id="labs-cloud" className="labs-section split-section">
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

            <section id="labs-actions" className="labs-section">
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

            <section id="labs-tools" className="labs-section">
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

            <section id="labs-forge" className="labs-section">
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

            <section id="labs-console" className="labs-section split-section">
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
              <div className="split-panel">
                <div className="section-heading">Console Posture</div>
                <article className="labs-card feed-log-panel">
                  <div className="feed-log-list">
                    <article className="feed-log-card">
                      <div className="feed-log-meta">
                        <span className="card-chip">requests</span>
                        <span className="feed-log-time">{labsAnalytics?.mcp_console.requests ?? 0}</span>
                      </div>
                      <strong>Public guidance stays outcome-focused.</strong>
                      <p>Detailed activity preview has moved to admin. Public users see answers and suggested actions, not operator logs.</p>
                    </article>
                    <article className="feed-log-card">
                      <div className="feed-log-meta">
                        <span className="card-chip">sessions</span>
                        <span className="feed-log-time">{labsAnalytics?.mcp_console.sessions ?? 0}</span>
                      </div>
                      <strong>Conversation memory remains live.</strong>
                      <p>Console sessions and latency metrics are still available without exposing the admin feed.</p>
                    </article>
                    {labsAnalytics?.mcp_console.top_topics.map((topic) => (
                      <article key={topic.topic} className="feed-log-card">
                        <div className="feed-log-meta">
                          <span className="card-chip">topic</span>
                          <span className="feed-log-time">{topic.count}</span>
                        </div>
                        <strong>{topic.topic}</strong>
                        <p>Frequently requested guidance route in the public console.</p>
                      </article>
                    ))}
                  </div>
                </article>
              </div>
            </section>
          </div>
        ) : viewMode === 'admin' ? (
          <div className="admin-shell">
            <section className="admin-hero">
              <div className="labs-kicker">ADMIN PORTAL</div>
              <h1>Internal controls and demo governance.</h1>
              <p>
                The admin surface now carries the vault, execution boards, lesson controls, and operator analytics that should not appear in the public demo layer.
              </p>
              <div className="council-status-row">
                <article className="signal-card">
                  <span className="signal-label">Access</span>
                  <strong>{isAdminLoggedIn ? adminUser?.email : 'Login required'}</strong>
                </article>
                <article className="signal-card">
                  <span className="signal-label">Vault</span>
                  <strong>{isAdminLoggedIn ? `${sessions.length} sessions unlocked` : 'Locked'}</strong>
                </article>
                <article className="signal-card">
                  <span className="signal-label">Feed Log</span>
                  <strong>{feedLog.length} events captured</strong>
                </article>
              </div>
            </section>

            {!isAdminLoggedIn ? (
              <section className="split-section">
                <div className="split-panel">
                  <article className="labs-card admin-login-card">
                    <div className="tool-card-top"><h3>Admin Login</h3><div className="status-pill connecting">Internal only</div></div>
                    <p>Use admin login to unlock the session vault, execution boards, lesson controls, and operator analytics for the demo run.</p>
                    <label className="forge-label"><span>Email</span><input value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} className="forge-input" /></label>
                    <label className="forge-label"><span>Password</span><input type="password" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} className="forge-input" /></label>
                    {adminError && <div className="admin-error">{adminError}</div>}
                    <button type="button" className="forge-button" onClick={() => void loginAdmin()} disabled={adminLoading}>
                      {adminLoading ? 'Signing in...' : 'Open Admin Portal'}
                    </button>
                  </article>
                </div>
                <div className="split-panel">
                  <article className="labs-card admin-login-card">
                    <div className="tool-card-top"><h3>Moved Off Public</h3><div className="card-chip">safety split</div></div>
                    <div className="deliverables-list">
                      <div className="deliverable-item">Session vault and forensic replay</div>
                      <div className="deliverable-item">Execution matrices and internal planning</div>
                      <div className="deliverable-item">Orch code lesson controls</div>
                      <div className="deliverable-item">Creator throughput and console analytics</div>
                      <div className="deliverable-item">Persistent operator activity log</div>
                    </div>
                  </article>
                  <article className="labs-card admin-login-card">
                    <div className="tool-card-top"><h3>Today First</h3><div className="card-chip">demo method</div></div>
                    <div className="deliverables-list">
                      <div className="deliverable-item">Verify admin login and vault access</div>
                      <div className="deliverable-item">Check live council and operator log flow</div>
                      <div className="deliverable-item">Run public Labs surfaces end-to-end</div>
                      <div className="deliverable-item">Confirm Forge task and artifact persistence</div>
                      <div className="deliverable-item">Update Schematics at each checkpoint</div>
                    </div>
                  </article>
                </div>
              </section>
            ) : (
              <>
                <section className="labs-section">
                  <div className="section-heading">Execution Boards</div>
                  <div className="labs-grid access-grid">
                    <article className="labs-card compact-card">
                      <div className="tool-card-top"><h3>Phase 1-5</h3><div className="card-chip">{completedExecutionTasks}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionTasks / 20) * 100}%` }} /></div>
                      <p>Core orchestration foundation, tools, governance, and UX readiness.</p>
                    </article>
                    <article className="labs-card compact-card">
                      <div className="tool-card-top"><h3>Phase 6-10</h3><div className="card-chip">{completedExecutionTasksPhase6Plus}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionTasksPhase6Plus / 20) * 100}%` }} /></div>
                      <p>Deployment, observability, security, reliability, and UX delivery checkpoints.</p>
                    </article>
                    <article className="labs-card compact-card">
                      <div className="tool-card-top"><h3>Lead + DEV_2 + DEV_3</h3><div className="card-chip">{completedExecutionLeadDev2}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionLeadDev2 / 20) * 100}%` }} /></div>
                      <p>Shared delivery board for release, observability, security, and reliability coverage.</p>
                    </article>
                    <article className="labs-card compact-card">
                      <div className="tool-card-top"><h3>Matrix Cycle A</h3><div className="card-chip">{completedExecutionDev2Dev3}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionDev2Dev3 / 20) * 100}%` }} /></div>
                      <p>Four-phase allocation with DEV_2 at five tasks and DEV_3 at ten.</p>
                    </article>
                    <article className="labs-card compact-card">
                      <div className="tool-card-top"><h3>Matrix Cycle B</h3><div className="card-chip">{completedExecutionDev2Dev3Cycle2}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionDev2Dev3Cycle2 / 20) * 100}%` }} /></div>
                      <p>Second internal execution cycle for rollout, ops, security, and delivery validation.</p>
                    </article>
                    <article className="labs-card compact-card admin-action-card">
                      <div className="tool-card-top"><h3>Lead Solo Phase</h3><div className="card-chip">{completedExecutionDev2Dev3LeadPhase}/20 complete</div></div>
                      <div className="execution-progress-track"><div className="execution-progress-fill" style={{ width: `${(completedExecutionDev2Dev3LeadPhase / 20) * 100}%` }} /></div>
                      <p>Final acceptance, UX readiness, and delivery summary approval.</p>
                      <button type="button" className="ghost-button" onClick={logoutAdmin}>Log Out</button>
                    </article>
                  </div>
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
                    <div className="section-heading">Activity Preview</div>
                    <article className="labs-card feed-log-panel">
                      <div className="feed-log-list">
                        {adminFeedPreview.map((entry) => (
                          <article key={entry.id} className="feed-log-card">
                            <div className="feed-log-meta">
                              <span className="card-chip">{entry.source}</span>
                              <span className="feed-log-time">{new Date(entry.received_at).toLocaleTimeString()}</span>
                            </div>
                            <strong>{entry.agent ? entry.agent.toUpperCase() : entry.type.toUpperCase()}</strong>
                            <p>{entry.content || entry.reasoning || 'No payload captured for this event.'}</p>
                          </article>
                        ))}
                      </div>
                    </article>
                  </div>
                </section>

                <section className="labs-section split-section">
                  <div className="split-panel">
                    <div className="section-heading">Session Vault</div>
                    <div className="vault-session-list">
                      {sessions.map((session) => (
                        <button key={session.id} type="button" className="vault-session-button" onClick={() => void loadSession(session.id)}>
                          <span className="vault-session-copy">
                            <span>{session.topic}</span>
                            <small>{session.audit_events ? `${session.round_count ?? 0} rounds · ${session.audit_events} audit events` : 'stored session · no audit trail yet'}</small>
                          </span>
                          <strong>{new Date(session.created_at).toLocaleString()}</strong>
                        </button>
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
                      {labsAnalytics?.forge.creator_throughput.map((entry) => (
                        <article key={entry.owner} className="labs-card compact-card">
                          <div className="tool-card-top"><h3>{entry.owner}</h3><div className="card-chip">{entry.count} tasks</div></div>
                          <p>Measured from persisted Forge ownership and movement events.</p>
                        </article>
                      ))}
                    </div>
                  </div>
                </section>
              </>
            )}
          </div>
        ) : (
          <div className="council-shell">
            <section className="council-hero">
              <div className="labs-kicker">Live Council</div>
              <h1>Fast local AI, framed for live decisions.</h1>
              <p>
                The council now reads like a stage instead of a dashboard: one featured voice,
                a visible support bench, and clear state changes so quiet moments still feel deliberate.
              </p>
              <div className="council-status-row">
                <article className="signal-card">
                  <span className="signal-label">Link</span>
                  <strong>{connectionState === 'live' ? 'Connected' : connectionState === 'connecting' ? 'Connecting' : 'Attention needed'}</strong>
                </article>
                <article className="signal-card">
                  <span className="signal-label">Live messages</span>
                  <strong>{messages.length}</strong>
                </article>
                <article className="signal-card">
                  <span className="signal-label">Session vault</span>
                  <strong>{isAdminLoggedIn ? `${sessions.length} archived lessons` : 'Admin only'}</strong>
                </article>
              </div>
            </section>

            <section className="council-layout">
              <article
                className={`chamber council-focus ${featuredCouncilCard.isThinking ? 'thinking' : ''} ${featuredCouncilCard.isResponding ? 'responding' : ''} ${featuredCouncilCard.isStudent ? 'student' : 'mentor'}`}
              >
                <div className="agent-rank">{featuredCouncilCard.isStudent ? '[STUDENT]' : '[MENTOR]'}</div>
                <div className="agent-id">{featuredCouncilCard.id}</div>
                {featuredCouncilCard.isThinking && <div className="glow-orb" />}
                <div className="focus-status-line">
                  <span className={`status-pill ${featuredCouncilCard.isThinking ? 'thinking' : featuredCouncilCard.isResponding ? 'live' : 'neutral'}`}>
                    {featuredCouncilCard.isThinking ? 'Reasoning' : featuredCouncilCard.isResponding ? 'Transmitting' : 'Queued'}
                  </span>
                  <span className="focus-status-meta">
                    {featuredCouncilCard.lastMsg ? `Round ${featuredCouncilCard.lastMsg.round}` : 'Awaiting next council trigger'}
                  </span>
                </div>
                <div className="response-text focus-copy">
                  {featuredCouncilCard.isThinking
                    ? featuredCouncilCard.isStudent
                      ? 'Synthesizing the next reasoning pass for the council.'
                      : 'Preparing the next expert intervention for the panel.'
                    : featuredCouncilCard.lastMsg?.content ||
                      'No live signal has been broadcast yet. Start the simulator or post to /broadcast to wake the room.'}
                </div>
                <div className="focus-reasoning">
                  {featuredCouncilCard.lastMsg?.reasoning || 'The featured chamber will show the last reasoning trace here as soon as the feed becomes active.'}
                </div>
                {(featuredCouncilCard.lastMsg?.value_score !== undefined || featuredCouncilCard.lastMsg?.override_score !== undefined) && (
                  <div className="value-meter">
                    <div
                      className="value-fill"
                      style={{ width: `${(featuredCouncilCard.lastMsg.override_score ?? featuredCouncilCard.lastMsg.value_score ?? 0) * 10}%` }}
                    />
                  </div>
                )}
              </article>

              <div className="council-side-grid">
                {supportCouncilCards.map((card) => (
                  <article
                    key={card.id}
                    className={`chamber compact-chamber ${card.isThinking ? 'thinking' : ''} ${card.isResponding ? 'responding' : ''} ${card.isStudent ? 'student' : 'mentor'}`}
                  >
                    <div className="agent-rank">{card.isStudent ? '[STUDENT]' : '[MENTOR]'}</div>
                    <div className="tool-card-top">
                      <div className="agent-id">{card.id}</div>
                      <div className={`status-pill ${card.isThinking ? 'thinking' : card.isResponding ? 'live' : 'neutral'}`}>
                        {card.isThinking ? 'Thinking' : card.isResponding ? 'Live' : 'Idle'}
                      </div>
                    </div>
                    <div className="response-text compact-copy">
                      {card.lastMsg?.content || 'Awaiting council handoff.'}
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="council-signal-strip">
              <article className="signal-card wide">
                <span className="signal-label">Latest transmission</span>
                <strong>{latestTransmission?.agent?.toUpperCase() ?? 'No live transmission yet'}</strong>
                <p>
                  {latestTransmission?.content ||
                    'The websocket is connected, but no simulator or broadcast event has pushed fresh council output into the room yet.'}
                </p>
              </article>
              <article className="signal-card">
                <span className="signal-label">Selected session</span>
                <strong>{selectedSession?.topic ?? 'Live view active'}</strong>
                <p>
                  {selectedSession?.created_at
                    ? new Date(selectedSession.created_at).toLocaleString()
                    : 'Choose a session from the vault to switch into forensic audit mode.'}
                </p>
              </article>
              <article className="signal-card">
                <span className="signal-label">Demo note</span>
                <strong>Quiet feed still looks intentional</strong>
                <p>
                  The council panels animate and re-prioritize when `/broadcast` or the simulator publishes new events.
                </p>
              </article>
            </section>
            <section className="labs-section">
              <div className="labs-grid access-grid">
                {publicLaunchers.map((launcher) => (
                  <button key={launcher.label} type="button" className={`metric-card labs-function-card ${launcher.active ? 'active' : ''}`} onClick={launcher.action}>
                    <span className="metric-value">{launcher.value}</span>
                    <span className="metric-label">{launcher.label}</span>
                    <span className="metric-copy">{launcher.detail}</span>
                  </button>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
