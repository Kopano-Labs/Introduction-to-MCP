export type PageId = 'council' | 'labs' | 'forge' | 'console' | 'admin';
export type ConnectionState = 'connecting' | 'live' | 'error';
export type LessonState = 'queued' | 'learning' | 'learned' | 'shipping';

export interface ReasoningBlock {
  block_id: string;
  agent: string;
  role: string | null;
  content: string;
  reasoning: string;
  value_score: number;
  override_score: number | null;
  improvement_hint: string | null;
  is_student: number;
}

export interface Round {
  id: string;
  round_number: number;
  blocks: ReasoningBlock[];
}

export interface Lesson {
  id: string;
  topic: string;
  created_at: string;
  rounds?: Round[];
  audit_events?: number;
  round_count?: number;
}

export interface LiveMessage {
  type: string;
  agent: string;
  block_id: string;
  content: string;
  reasoning: string;
  round: number;
  value_score?: number;
  override_score?: number;
  improvement_hint?: string;
}

export interface GuiUser {
  id: number;
  email: string;
  full_name?: string | null;
  role: string;
  god_mode: boolean;
  is_active: boolean;
  created_at: string;
}

export interface FeedLogEntry {
  id: string;
  type: string;
  agent?: string;
  content?: string;
  reasoning?: string;
  round?: number;
  received_at: string;
  source: 'ws' | 'poll' | 'system';
}

export interface LabsCategory {
  id: string;
  title: string;
  description: string;
}

export interface LabsTool {
  id: string;
  name: string;
  category: string;
  criticality: string;
  status: string;
  summary: string;
  impact: string;
  phase: string;
}

export interface LabsPhase {
  id: string;
  title: string;
  criticality: string;
  status: string;
  summary: string;
  deliverables: string[];
}

export interface LabsLanguage {
  id: string;
  name: string;
  family: string;
  status: string;
}

export interface AccessMode {
  id: string;
  name: string;
  summary: string;
  criticality: string;
}

export interface CoworkSurface {
  id: string;
  name: string;
  status: string;
  inspiration: string;
  summary: string;
  features: string[];
}

export interface OrchCodeTrack {
  id: string;
  title: string;
  priority: string;
  summary: string;
  topics: string[];
}

export interface OrchInterface {
  id: string;
  name: string;
  status: string;
  summary: string;
  mechanics: string[];
}

export interface CloudStack {
  id: string;
  name: string;
  provider: string;
  priority: string;
  status: string;
  summary: string;
  focus: string[];
}

export interface ConnectorWorkflow {
  id: string;
  name: string;
  status: string;
  summary: string;
}

export interface InstallerAction {
  id: string;
  surface: string;
  title: string;
  provider: string;
  status: string;
  summary: string;
  commands: string[];
}

export interface CoworkTask {
  id: number;
  room_id: number;
  title: string;
  description: string;
  owner: string;
  status: string;
  priority: string;
  lane: string;
}

export interface CoworkArtifact {
  id: number;
  room_id: number;
  artifact_type: string;
  title: string;
  summary: string;
  status: string;
  link: string | null;
}

export interface CoworkRoom {
  id: number;
  name: string;
  mission: string;
  lead: string;
  status: string;
  tasks: CoworkTask[];
  artifacts: CoworkArtifact[];
  lanes: Record<string, CoworkTask[]>;
  dispatch_summary: {
    total_tasks: number;
    queued: number;
    in_progress: number;
    completed: number;
    owners: string[];
  };
  artifact_summary: {
    total_artifacts: number;
    artifact_types: string[];
  };
}

export type CoworkRoomSummary =
  Pick<CoworkRoom, 'id' | 'name' | 'mission' | 'lead' | 'status'>
  & Partial<Omit<CoworkRoom, 'id' | 'name' | 'mission' | 'lead' | 'status'>>;

export interface ConsoleAnalytics {
  sessions: number;
  requests: number;
  average_latency_ms: number;
  top_topics: Array<{ topic: string; count: number }>;
}

export interface McpConsoleReply {
  session_id: number;
  input: string;
  topic: string;
  response: string;
  suggested_actions: string[];
  surfaces: string[];
  model_used: string;
  model_options: Array<{ id: string; label: string; model: string }>;
  analytics: ConsoleAnalytics;
}

export interface LabsOverview {
  title: string;
  positioning: string;
  categories: LabsCategory[];
  tools: LabsTool[];
  phases: LabsPhase[];
  languages: LabsLanguage[];
  access_modes: AccessMode[];
  cowork_surfaces: CoworkSurface[];
  orch_code_tracks: OrchCodeTrack[];
  kopano_interfaces: OrchInterface[];
  cloud_stacks: CloudStack[];
  connector_workflows: ConnectorWorkflow[];
  installer_actions: InstallerAction[];
  metrics: {
    categories: number;
    tools: number;
    critical_tools: number;
    live_tools: number;
    languages: number;
    access_modes: number;
    interfaces: number;
    cloud_stacks: number;
    installer_actions: number;
  };
}

export interface LabsAnalytics {
  forge: {
    rooms: number;
    tasks: number;
    artifacts: number;
    completed_tasks: number;
    creator_throughput: Array<{ owner: string; count: number }>;
    event_volume: Array<{ event_type: string; count: number }>;
  };
  mcp_console: ConsoleAnalytics;
}

export interface MicrosoftEnvStatus {
  configured: boolean;
  missing: string[];
}

export interface MicrosoftReadiness {
  summary: {
    required_ready: number;
    required_total: number;
    optional_ready: number;
    optional_total: number;
    demo_ready: boolean;
  };
  tooling: {
    az: { installed: boolean; version: string | null; path: string | null; healthy: boolean; error: string; };
    azd: { installed: boolean; version: string | null; path: string | null; healthy: boolean; error: string; };
    python_packages: { azure_monitor_opentelemetry: boolean; azure_identity: boolean; };
    telemetry: { attempted: boolean; configured: boolean; reason: string; };
  };
  azure_account: {
    logged_in: boolean;
    subscription_name: string | null;
    subscription_id: string | null;
    tenant_id: string | null;
    reason: string;
  };
  env: {
    azure_openai: MicrosoftEnvStatus;
    app_insights: MicrosoftEnvStatus;
    hosting: MicrosoftEnvStatus;
    azure_ai_search: MicrosoftEnvStatus;
    managed_identity: MicrosoftEnvStatus;
  };
  frontend: {
    application_insights_web: {
      installed: boolean;
      version: string | null;
    };
  };
  commands: string[];
  next_steps: string[];
}

export interface CouncilCard {
  id: string;
  lastMsg?: LiveMessage;
  isStudent: boolean;
  isThinking: boolean;
  isResponding: boolean;
}
