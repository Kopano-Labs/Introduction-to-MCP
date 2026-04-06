from __future__ import annotations

from typing import Any


LABS_CATEGORIES: list[dict[str, str]] = [
    {"id": "jobs", "title": "Jobs And Income", "description": "Experiments that increase earning power and work access."},
    {"id": "utilities", "title": "Utilities And Resilience", "description": "Experiments for power, water, and local resilience."},
    {"id": "civic", "title": "Civic And Community", "description": "Experiments for reporting, local services, and community support."},
    {"id": "education", "title": "Education And Youth", "description": "Experiments for tutoring, opportunities, and skills growth."},
    {"id": "health", "title": "Health And Access", "description": "Experiments for service access, clinic navigation, and wellbeing."},
    {"id": "language", "title": "Language And Accessibility", "description": "Experiments for SA languages, speech access, and inclusion."},
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
        "status": "planned",
        "summary": "Makes orch understand and respond in all official South African languages.",
        "impact": "National accessibility instead of English-only AI.",
        "phase": "Phase 7",
    },
    {
        "id": "speech-access-assistant",
        "name": "Speech Access Assistant",
        "category": "language",
        "criticality": "critical",
        "status": "planned",
        "summary": "Supports users with speech impairment through adaptive speech and alternative communication flows.",
        "impact": "Inclusive AI use for more South Africans.",
        "phase": "Phase 7",
    },
]


LABS_PHASES: list[dict[str, Any]] = [
    {
        "id": "phase-6",
        "title": "Phase 6: Orch Labs",
        "criticality": "critical",
        "status": "in_progress",
        "summary": "Build a Google-Labs-style experiment layer on top of orch for South African tools.",
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
        "status": "planned",
        "summary": "Add all SA languages and speech-impairment-aware support.",
        "deliverables": [
            "All official South African language plan",
            "Multilingual routing layer",
            "Speech-impairment-aware interaction design",
            "Voice and text fallback accessibility flows",
        ],
    },
    {
        "id": "phase-8",
        "title": "Phase 8: Public Impact Studio",
        "criticality": "high",
        "status": "planned",
        "summary": "Run public-impact AI experiments with visibility, metrics, and iteration loops.",
        "deliverables": [
            "Tool analytics",
            "Impact dashboard",
            "Pilot workflow",
            "Community feedback loop",
        ],
    },
]


def get_labs_overview() -> dict[str, Any]:
    return {
        "title": "Orch Labs",
        "positioning": "A Google-Labs-style experiment layer on top of orch for South African public-impact AI tools.",
        "categories": LABS_CATEGORIES,
        "tools": LABS_TOOLS,
        "phases": LABS_PHASES,
        "metrics": {
            "categories": len(LABS_CATEGORIES),
            "tools": len(LABS_TOOLS),
            "critical_tools": sum(1 for tool in LABS_TOOLS if tool["criticality"] == "critical"),
            "live_tools": sum(1 for tool in LABS_TOOLS if tool["status"] == "live"),
        },
    }
