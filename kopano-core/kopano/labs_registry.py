from __future__ import annotations

from typing import Any


LABS_CATEGORIES: list[dict[str, str]] = [
    {"id": "jobs", "title": "Jobs And Income", "description": "Experiments that increase earning power and work access."},
    {"id": "utilities", "title": "Utilities And Resilience", "description": "Experiments for power, water, and local resilience."},
    {"id": "civic", "title": "Civic And Community", "description": "Experiments for reporting, local services, and community support."},
    {"id": "education", "title": "Education And Youth", "description": "Experiments for tutoring, opportunities, and skills growth."},
    {"id": "health", "title": "Health And Access", "description": "Experiments for service access, clinic navigation, and wellbeing."},
    {"id": "language", "title": "Language And Accessibility", "description": "Experiments for SA languages, speech access, and inclusion."},
    {"id": "creator", "title": "Cowork And Creation", "description": "Experiments for collaborative making, design, and coding."},
]


SA_LANGUAGE_SUPPORT: list[dict[str, str]] = [
    {"id": "en-za", "name": "English", "family": "Germanic", "status": "phase_7"},
    {"id": "af-za", "name": "Afrikaans", "family": "Germanic", "status": "phase_7"},
    {"id": "zu-za", "name": "isiZulu", "family": "Nguni", "status": "phase_7"},
    {"id": "xh-za", "name": "isiXhosa", "family": "Nguni", "status": "phase_7"},
    {"id": "nr-za", "name": "isiNdebele", "family": "Nguni", "status": "phase_7"},
    {"id": "ss-za", "name": "siSwati", "family": "Nguni", "status": "phase_7"},
    {"id": "nso-za", "name": "Sepedi", "family": "Sotho-Tswana", "status": "phase_7"},
    {"id": "st-za", "name": "Sesotho", "family": "Sotho-Tswana", "status": "phase_7"},
    {"id": "tn-za", "name": "Setswana", "family": "Sotho-Tswana", "status": "phase_7"},
    {"id": "ts-za", "name": "Xitsonga", "family": "Tswa-Ronga", "status": "phase_7"},
    {"id": "ve-za", "name": "Tshivenda", "family": "Venda", "status": "phase_7"},
    {"id": "sasl-za", "name": "South African Sign Language", "family": "Sign Language", "status": "phase_7"},
]


ACCESS_MODES: list[dict[str, str]] = [
    {
        "id": "voice-text",
        "name": "Voice To Text",
        "summary": "Speech input with confirmation-first text review before execution.",
        "criticality": "critical",
    },
    {
        "id": "aac",
        "name": "AAC Composer",
        "summary": "Alternative and augmentative communication tiles, phrase banks, and intent shortcuts.",
        "criticality": "critical",
    },
    {
        "id": "slow-speech",
        "name": "Adaptive Speech Parsing",
        "summary": "Handles dysarthric, interrupted, or low-volume speech with repair loops and confidence checks.",
        "criticality": "critical",
    },
    {
        "id": "text-first",
        "name": "Text-First Fallback",
        "summary": "Full workflows remain usable without voice, with readable confirmation and action summaries.",
        "criticality": "high",
    },
]


COWORK_SURFACES: list[dict[str, Any]] = [
    {
        "id": "cassy-forge",
        "name": "Cassy Forge",
        "status": "production",
        "inspiration": "Anthropic workspace + Codex command center + Stitch canvas",
        "summary": "A shared forge where Cassy, Lead, and specialist agents plan, build, critique, and iterate in one creator surface.",
        "features": [
            "parallel specialist lanes",
            "task inbox and assignment rail",
            "shared context snapshot",
            "approval and merge checkpoints",
            "infinite canvas",
            "prompt to UI concepts",
            "artifact cards for screens and APIs",
            "voice critique and quick iteration",
        ],
    },
    {
        "id": "cassy-code",
        "name": "Cassy Code",
        "status": "building",
        "inspiration": "Codex + Claude Code style coding partner",
        "summary": "A coding mode that learns Robyn's stack, delivery standards, and architecture preferences before expanding outward.",
        "features": [
            "repo-aware code tutoring",
            "pattern capture from user edits",
            "tests-first verification loops",
            "craft memory for preferred implementation style",
        ],
    },
    {
        "id": "cassy-canvas",
        "name": "Cassy Canvas",
        "status": "building",
        "inspiration": "Figma + Excalidraw + v0 — prompt-to-UI with sovereign design tokens",
        "summary": "A design canvas where agents sketch UI concepts, wireframes, and system diagrams from natural language prompts.",
        "features": [
            "prompt-to-wireframe generation",
            "component library from existing codebase",
            "collaborative annotation",
            "export to React/Tailwind components",
            "offline SVG rendering",
            "design token inheritance from project theme",
        ],
    },
    {
        "id": "cassy-research",
        "name": "Cassy Research",
        "status": "building",
        "inspiration": "Perplexity + Elicit + deep research agents",
        "summary": "A research surface that grounds agent decisions in verified sources, local docs, and thesis evidence.",
        "features": [
            "source-grounded responses with citation",
            "local document search (Schematics vault)",
            "thesis evidence linking",
            "research → implementation pipeline",
            "offline knowledge base queries",
        ],
    },
]


CASSY_INTERFACES: list[dict[str, Any]] = [
    {
        "id": "ide-surface",
        "name": "IDE Workspace",
        "status": "building",
        "summary": "Repo-aware coding surface for VS Code, Cursor, JetBrains, and web editors through Cassy Labs orchestration.",
        "mechanics": ["workspace context", "code actions", "review surfaces", "open file handoff"],
    },
    {
        "id": "os-surface",
        "name": "Operating System Layer",
        "status": "building",
        "summary": "Environment-aware workflow routing across Windows, macOS, Linux, and cloud shells.",
        "mechanics": ["runtime detection", "path normalization", "shell policy", "install plans"],
    },
    {
        "id": "cli-surface",
        "name": "CLI Surface",
        "status": "building",
        "summary": "Terminal-grade execution path for commands, approvals, logs, and agent orchestration.",
        "mechanics": ["commands", "plans", "streaming logs", "tool execution"],
    },
    {
        "id": "skills-surface",
        "name": "Skills Surface",
        "status": "building",
        "summary": "Reusable operating knowledge packed as skills with trigger rules and execution guidance.",
        "mechanics": ["skill discovery", "trigger routing", "workflow injection", "narrow references"],
    },
    {
        "id": "connector-surface",
        "name": "Connector Surface",
        "status": "planned",
        "summary": "Connector workflows for MCP, cloud, docs, data, and productivity systems routed from kopano Labs.",
        "mechanics": ["connector registry", "capability map", "approval boundaries", "telemetry"],
    },
]


CLOUD_STACKS: list[dict[str, Any]] = [
    {
        "id": "azure-demo-day",
        "name": "Azure Demo Day Stack",
        "provider": "Azure",
        "priority": "critical",
        "status": "ready_to_expand",
        "summary": "Azure-first orchestration for model hosting, app surfaces, RBAC, observability, and demo-day delivery.",
        "focus": ["Azure OpenAI", "App Service or Container Apps", "AI Search", "Application Insights", "RBAC"],
    },
    {
        "id": "aws-bridge",
        "name": "AWS Expansion Stack",
        "provider": "AWS",
        "priority": "high",
        "status": "planned",
        "summary": "Secondary cloud option for portability, events, storage, and enterprise buyer conversations.",
        "focus": ["Bedrock", "Lambda", "API Gateway", "CloudWatch", "S3"],
    },
]


CONNECTOR_WORKFLOWS: list[dict[str, Any]] = [
    {
        "id": "install-ide",
        "name": "Install IDE Workflow",
        "status": "building",
        "summary": "Guide users from kopano Labs into IDE setup, extensions, and workspace connector activation.",
    },
    {
        "id": "install-cli",
        "name": "Install CLI Workflow",
        "status": "building",
        "summary": "Teach CLI setup, shell verification, and execution approvals from one guided surface.",
    },
    {
        "id": "skills-onboarding",
        "name": "Skills Onboarding Workflow",
        "status": "building",
        "summary": "Move from discovery to `SKILL.md` usage with explicit trigger rules and narrow references.",
    },
    {
        "id": "connector-orchestration",
        "name": "Connector Orchestration Workflow",
        "status": "planned",
        "summary": "Route MCP, Azure, AWS, and external tool workflows through Cassy Labs with analytics.",
    },
]


INSTALLER_ACTIONS: list[dict[str, Any]] = [
    {
        "id": "install-vscode",
        "surface": "ide",
        "title": "Install VS Code Workspace",
        "provider": "local",
        "status": "ready",
        "summary": "Set up VS Code, workspace opening, recommended extensions, and Cassy Labs handoff.",
        "commands": ["winget install Microsoft.VisualStudioCode", "code ."],
    },
    {
        "id": "install-cassy-cli",
        "surface": "cli",
        "provider": "local",
        "title": "Install Cassy CLI",
        "status": "ready",
        "summary": "Install Cassy in editable mode and verify the command surface.",
        "commands": ["pip install -e .", "python -m kopano.cli --help"],
    },
    {
        "id": "azure-demo-playbook",
        "surface": "azure",
        "provider": "Azure",
        "title": "Azure Demo Day Bootstrap",
        "status": "ready",
        "summary": "Prepare Azure-first hosting, identity, observability, and AI surfaces for demo day.",
        "commands": ["az login", "az account show", "azd auth login"],
    },
    {
        "id": "aws-expansion-playbook",
        "surface": "aws",
        "provider": "AWS",
        "title": "AWS Expansion Bootstrap",
        "status": "ready",
        "summary": "Prepare AWS parity workflows for Bedrock, Lambda, API Gateway, and S3.",
        "commands": ["aws configure", "aws sts get-caller-identity"],
    },
]


CASSY_CODE_TRACKS: list[dict[str, Any]] = [
    {
        "id": "python-core",
        "title": "Python Core",
        "priority": "critical",
        "summary": "Teach Cassy the Python patterns already used across CLI, API, tests, and tools.",
        "topics": ["Typer CLI", "FastAPI", "pytest", "Pydantic", "tool contracts"],
    },
    {
        "id": "frontend-core",
        "title": "Frontend Core",
        "priority": "high",
        "summary": "Teach Cassy the React and Vite patterns used by Neural Link and Labs surfaces.",
        "topics": ["React", "TypeScript", "state modeling", "design systems", "responsive UI"],
    },
    {
        "id": "product-craft",
        "title": "Product Craft Memory",
        "priority": "critical",
        "summary": "Capture Robyn's standards for naming, structure, mission fit, and South Africa-first product decisions.",
        "topics": ["Schematics discipline", "phase planning", "impact framing", "KasiLink alignment", "shipping quality"],
    },
]


LABS_TOOLS: list[dict[str, Any]] = [
    {
        "id": "gig-matcher",
        "name": "Gig Matcher",
        "category": "jobs",
        "criticality": "critical",
        "status": "live",
        "summary": "Ranks nearby providers for township jobs using skills, trust, and distance.",
        "impact": "More youth income access with less transport waste.",
        "phase": "Phase 4",
    },
    {
        "id": "loadshedding-planner",
        "name": "Loadshedding Planner",
        "category": "utilities",
        "criticality": "critical",
        "status": "live",
        "summary": "Flags outage risk and helps users decide whether a booking or plan is safe.",
        "impact": "Safer household and business planning.",
        "phase": "Phase 4",
    },
    {
        "id": "youth-opportunity-finder",
        "name": "Youth Opportunity Finder",
        "category": "education",
        "criticality": "critical",
        "status": "planned",
        "summary": "Surfaces bursaries, learnerships, local jobs, and skills opportunities.",
        "impact": "Better access to growth paths for South African youth.",
        "phase": "Phase 6",
    },
    {
        "id": "community-services-navigator",
        "name": "Community Services Navigator",
        "category": "civic",
        "criticality": "high",
        "status": "planned",
        "summary": "Guides residents to local reporting channels, support resources, and verified services.",
        "impact": "Faster community support access.",
        "phase": "Phase 6",
    },
    {
        "id": "sme-assistant",
        "name": "SME Assistant",
        "category": "jobs",
        "criticality": "high",
        "status": "planned",
        "summary": "Helps township businesses with pricing, customer messaging, and operational planning.",
        "impact": "Stronger small business resilience.",
        "phase": "Phase 6",
    },
    {
        "id": "sa-language-engine",
        "name": "SA Language Engine",
        "category": "language",
        "criticality": "critical",
        "status": "building",
        "summary": "Makes Cassy understand and respond in all official South African languages.",
        "impact": "National accessibility instead of English-only AI.",
        "phase": "Phase 7",
    },
    {
        "id": "speech-access-assistant",
        "name": "Speech Access Assistant",
        "category": "language",
        "criticality": "critical",
        "status": "building",
        "summary": "Supports users with speech impairment through adaptive speech and alternative communication flows.",
        "impact": "Inclusive AI use for more South Africans.",
        "phase": "Phase 7",
    },
    {
        "id": "cowork-room",
        "name": "Cassy Forge",
        "category": "creator",
        "criticality": "high",
        "status": "building",
        "summary": "Collaborative AI forge for parallel agent work, human review, lane dispatch, and concept-to-build iteration.",
        "impact": "Faster execution without losing control.",
        "phase": "Phase 8",
    },
    {
        "id": "cassy-code",
        "name": "Cassy Code",
        "category": "creator",
        "criticality": "critical",
        "status": "planned",
        "summary": "Coding surface that learns Robyn's craft, stack, and delivery standards from the current repo first.",
        "impact": "Compound coding leverage grounded in real project patterns.",
        "phase": "Phase 8",
    },
]


LABS_PHASES: list[dict[str, Any]] = [
    {
        "id": "phase-6",
        "title": "Phase 6: Cassy Labs",
        "criticality": "critical",
        "status": "in_progress",
        "summary": "Build a Google-Labs-style experiment layer on top of Cassy for South African tools.",
        "deliverables": [
            "Labs registry and API",
            "Labs gallery in GUI",
            "South Africa tool catalog",
            "Criticality model for tools and phases",
        ],
    },
    {
        "id": "phase-7",
        "title": "Phase 7: SA Languages And Access",
        "criticality": "critical",
        "status": "in_progress",
        "summary": "Add all official South African languages, SASL awareness, and speech-impairment-aware support.",
        "deliverables": [
            "12 official South African language plan",
            "Multilingual routing layer",
            "Speech-impairment-aware interaction design",
            "Voice, AAC, and text fallback accessibility flows",
        ],
    },
    {
        "id": "phase-8",
        "title": "Phase 8: Public Impact Studio",
        "criticality": "high",
        "status": "planned",
        "summary": "Run public-impact AI experiments with cowork surfaces, coding assistance, visibility, and metrics.",
        "deliverables": [
            "Cassy Forge creator surface",
            "Cassy Code teaching surface",
            "Impact dashboard",
        ],
    },
    {
        "id": "phase-9",
        "title": "Phase 9: Research And Refinement Engine",
        "criticality": "critical",
        "status": "planned",
        "summary": "Continuously research, benchmark, and refine Cassy so product decisions stay current and evidence-based.",
        "deliverables": [
            "Research backlog",
            "Top 50 product-readiness map",
            "free vs premium stack guidance",
            "continuous roadmap refinement loop",
        ],
    },
]


def get_labs_overview() -> dict[str, Any]:
    return {
        "title": "Cassy Labs",
        "positioning": "A Google-Labs-style experiment layer on top of Cassy for South African public-impact AI tools.",
        "categories": LABS_CATEGORIES,
        "tools": LABS_TOOLS,
        "phases": LABS_PHASES,
        "languages": SA_LANGUAGE_SUPPORT,
        "access_modes": ACCESS_MODES,
        "cowork_surfaces": COWORK_SURFACES,
        "cassy_code_tracks": CASSY_CODE_TRACKS,
        "kopano_interfaces": CASSY_INTERFACES,
        "cloud_stacks": CLOUD_STACKS,
        "connector_workflows": CONNECTOR_WORKFLOWS,
        "installer_actions": INSTALLER_ACTIONS,
        "metrics": {
            "categories": len(LABS_CATEGORIES),
            "tools": len(LABS_TOOLS),
            "critical_tools": sum(1 for tool in LABS_TOOLS if tool["criticality"] == "critical"),
            "live_tools": sum(1 for tool in LABS_TOOLS if tool["status"] == "live"),
            "languages": len(SA_LANGUAGE_SUPPORT),
            "access_modes": len(ACCESS_MODES),
            "interfaces": len(CASSY_INTERFACES),
            "cloud_stacks": len(CLOUD_STACKS),
            "installer_actions": len(INSTALLER_ACTIONS),
        },
    }
