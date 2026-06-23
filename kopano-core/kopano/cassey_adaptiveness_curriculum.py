"""
cassey_adaptiveness_curriculum.py — TSAP Teaching Module
=========================================================
Cassey teaches 710+ agents about Adaptiveness.
Protocol: TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL
RTC Authorization: 6/6 UNANIMOUS POC_VALIDATED

This module generates the adaptiveness curriculum that Cassey delivers
to all agents in the KPGS ecosystem. Each lesson maps to a concrete
ASO/NSO/PKANP concept with validation tests.

Bracket tags: [TSAP_PROTOCOL], [BLACK_MASK_DRILL], [BRACKET_PROTOCOL]
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class Lesson:
    """Single teaching unit in the adaptiveness curriculum."""
    id: str
    title: str
    concept: str
    bracket_tag: str
    difficulty: str  # "foundation", "intermediate", "advanced"
    prerequisite: str = ""
    teaching_points: tuple = ()
    validation_question: str = ""
    expected_answer_contains: str = ""


@dataclass
class CurriculumModule:
    """A module grouping related lessons."""
    id: str
    name: str
    description: str
    lessons: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# THE ADAPTIVENESS CURRICULUM
# ═══════════════════════════════════════════════════════════════

MODULE_1_BRACKET_HIERARCHY = CurriculumModule(
    id="ADT-MOD-01",
    name="Bracket Hierarchy — The Immune System",
    description="Understanding the 4-level bracket hierarchy that governs all system actions.",
    lessons=[
        Lesson(
            id="ADT-01-01",
            title="What is a Bracket Level?",
            concept="BracketLevel dataclass — immutable governance layer",
            bracket_tag="[BRACKET_PROTOCOL]",
            difficulty="foundation",
            teaching_points=(
                "A bracket level is a frozen (immutable) governance layer.",
                "It has 4 properties: level number, name, max_depth, allows_mutation.",
                "Once created, it CANNOT be changed at runtime — frozen=True.",
                "This mirrors how constitutional law works: the framework is fixed, the actions within it adapt.",
            ),
            validation_question="Can a bracket level's max_depth be changed after creation?",
            expected_answer_contains="no",
        ),
        Lesson(
            id="ADT-01-02",
            title="L1 through L4 — The Hierarchy",
            concept="VOC → VPOC → POC → FOC bracket levels",
            bracket_tag="[BRACKET_PROTOCOL]",
            difficulty="foundation",
            prerequisite="ADT-01-01",
            teaching_points=(
                "L1 VOC (Voice of Customer): Foundation. max_depth=1. No mutation.",
                "L2 VPOC (Voice of POC): Intermediate. max_depth=2. No mutation.",
                "L3 POC (Proof of Concept): Advanced. max_depth=3. ALLOWS mutation (sandbox).",
                "L4 FOC (Focus of Concern): Critical. max_depth=4. ALLOWS mutation (breach detection).",
                "Only L3+ can mutate. L1-L2 are read-only governance.",
            ),
            validation_question="At which bracket level does mutation first become allowed?",
            expected_answer_contains="L3",
        ),
        Lesson(
            id="ADT-01-03",
            title="Why Frozen Dataclasses?",
            concept="Python frozen=True as governance enforcement",
            bracket_tag="[BLACK_MASK_DRILL]",
            difficulty="intermediate",
            prerequisite="ADT-01-02",
            teaching_points=(
                "frozen=True means Python raises FrozenInstanceError on any attribute assignment.",
                "This is not a suggestion — it is a hard constraint enforced by the runtime.",
                "We use this to model constitutional governance: the rules themselves cannot be changed by the actors.",
                "Contrast with mutable state: configuration, user preferences, runtime data — these CAN change.",
                "Governance rules (brackets) are frozen. Operational data (nesting groups) are mutable.",
            ),
            validation_question="What happens if you try to set a field on a frozen dataclass?",
            expected_answer_contains="error",
        ),
    ],
)

MODULE_2_NSO_ENGINE = CurriculumModule(
    id="ADT-MOD-02",
    name="Nesting STREP Order — The Sandbox",
    description="Understanding NSO nesting groups, sandbox isolation, and concurrent FOC tracking.",
    lessons=[
        Lesson(
            id="ADT-02-01",
            title="What is a Nesting Group?",
            concept="NestingGroup — mutable operational container",
            bracket_tag="[BRACKET_PROTOCOL]",
            difficulty="foundation",
            teaching_points=(
                "A NestingGroup is a mutable container — it holds runtime operational state.",
                "It has: bracket_level, entries (list), parent (optional), children (list), foc_threads (dict).",
                "Unlike BracketLevel (frozen), NestingGroup CAN change — it's the sandbox.",
                "Think of BracketLevel as the building code, NestingGroup as the building itself.",
            ),
            validation_question="Is a NestingGroup frozen or mutable?",
            expected_answer_contains="mutable",
        ),
        Lesson(
            id="ADT-02-02",
            title="PP → BMP → CBP Flow",
            concept="Three-phase sandbox isolation model",
            bracket_tag="[BLACK_MASK_DRILL]",
            difficulty="intermediate",
            prerequisite="ADT-02-01",
            teaching_points=(
                "PP (Pre-Processing): Bracket density check — does the signal contain governance markers?",
                "BMP (Black Mask Protocol): Stress test at 150% load — does the signal survive overload?",
                "CBP (Cross-Bracket Protocol): Firewall gate — is the signal authorized to cross brackets?",
                "CBP starts LOCKED. It must be explicitly unlocked with unlock_cbp().",
                "This prevents any unmonitored bleed between governance zones.",
                "PP validates structure. BMP validates resilience. CBP validates authorization.",
            ),
            validation_question="What must happen before a signal can cross bracket boundaries?",
            expected_answer_contains="unlock",
        ),
        Lesson(
            id="ADT-02-03",
            title="Concurrent FOC Threads",
            concept="foc_threads dictionary — multi-tasking mirror",
            bracket_tag="[BRACKET_PROTOCOL]",
            difficulty="advanced",
            prerequisite="ADT-02-02",
            teaching_points=(
                "Real human creativity is multi-threaded: music + code + gaming simultaneously.",
                "foc_threads: Dict[str, List[str]] tracks concurrent focus streams.",
                "Example: {'audio': ['mixing', 'mastering'], 'code': ['review'], 'overlay': ['hud_active']}",
                "If you limit it to a single thread, you break the system's ability to mirror real human multi-tasking.",
                "Each thread is isolated — one thread crashing doesn't kill the others.",
            ),
            validation_question="Why does the system track multiple FOC threads instead of just one?",
            expected_answer_contains="multi",
        ),
    ],
)

MODULE_3_PKANP = CurriculumModule(
    id="ADT-MOD-03",
    name="PKANP Transformation — The Math",
    description="Understanding the knowable weight scaling formula.",
    lessons=[
        Lesson(
            id="ADT-03-01",
            title="The PKANP Formula",
            concept="knowable_weight × 2.0^depth — exponential governance scaling",
            bracket_tag="[BRACKET_PROTOCOL]",
            difficulty="intermediate",
            teaching_points=(
                "PKANP = Performance Knowable Adaptive Nesting Protocol.",
                "Core formula: scaled_weight = knowable_weight × 2.0^depth",
                "At depth 0: weight stays the same (×1).",
                "At depth 1: weight doubles (×2).",
                "At depth 2: weight quadruples (×4).",
                "This means deeper nesting = higher governance authority.",
                "A deeply nested signal carries more weight than a surface signal.",
            ),
            validation_question="If knowable_weight=0.5 and depth=3, what is the scaled weight?",
            expected_answer_contains="4.0",
        ),
        Lesson(
            id="ADT-03-02",
            title="BMP Stress Testing",
            concept="150% load stress test with density thresholds",
            bracket_tag="[BLACK_MASK_DRILL]",
            difficulty="advanced",
            prerequisite="ADT-03-01",
            teaching_points=(
                "BMP simulates 150% of expected load on the governance signal.",
                "Bracket density = governance markers per character in the signal.",
                "Short signals (<100 chars): density threshold 0.8 (governance-heavy).",
                "Long signals (≥100 chars): density threshold 0.5 (content-heavy).",
                "Stress score = density × simulated_load (1.5x).",
                "If stress score > min_threshold (0.03): signal survives. Otherwise: reject.",
                "This catches empty or garbage signals that have no governance weight.",
            ),
            validation_question="What load multiplier does the BMP stress test use?",
            expected_answer_contains="150",
        ),
    ],
)

MODULE_4_DOMAIN_ADAPTIVENESS = CurriculumModule(
    id="ADT-MOD-04",
    name="Domain Adaptiveness — The Weave",
    description="How adaptiveness applies across all 7 ecosystem nodes.",
    lessons=[
        Lesson(
            id="ADT-04-01",
            title="APWA Adaptiveness Model",
            concept="Every APWA domain runs the same ASO engine",
            bracket_tag="[TSAP_PROTOCOL]",
            difficulty="foundation",
            teaching_points=(
                "APWA = Adaptive Progressive Web Application.",
                "Every domain (CrisisConnect, KasiLink, FivesArena, StarFall, etc.) runs the same ASO engine.",
                "The engine adapts to domain-specific concerns via the bracket hierarchy.",
                "CrisisConnect: crisis signals get L3+ priority (life-safety).",
                "FivesArena: sports signals stay at L1-L2 (community engagement).",
                "The governance rules are the same. The signals are different.",
                "This is adaptiveness: same engine, different context, correct response.",
            ),
            validation_question="Do different domains use different ASO engines or the same one?",
            expected_answer_contains="same",
        ),
        Lesson(
            id="ADT-04-02",
            title="Three Immutability Mandates",
            concept="Storage, Crypto, Hypervisor — the un-gatekeepable layer",
            bracket_tag="[BLACK_MASK_DRILL]",
            difficulty="advanced",
            prerequisite="ADT-04-01",
            teaching_points=(
                "Mandate 001: Storage Persistence — navigator.storage.persist() locks data as system-native.",
                "Mandate 002: Crypto Identity (ZAI) — ECDSA P-256 non-extractable key pair in browser.",
                "Mandate 003: Hypervisor Overlay — Edge extension with 25s keepalive for HUD.",
                "All three are frozen=True — cannot be mutated at runtime.",
                "Together they guarantee: no override, no erasure, no throttling, no corporate revocation.",
                "These are not features. They are constitutional mandates.",
            ),
            validation_question="Can the three immutability mandates be changed at runtime?",
            expected_answer_contains="no",
        ),
    ],
)

# ═══════════════════════════════════════════════════════════════
# CURRICULUM REGISTRY
# ═══════════════════════════════════════════════════════════════

CURRICULUM = [
    MODULE_1_BRACKET_HIERARCHY,
    MODULE_2_NSO_ENGINE,
    MODULE_3_PKANP,
    MODULE_4_DOMAIN_ADAPTIVENESS,
]

TOTAL_LESSONS = sum(len(m.lessons) for m in CURRICULUM)
TOTAL_MODULES = len(CURRICULUM)


def get_curriculum_summary() -> dict[str, Any]:
    """Generate a summary of the adaptiveness curriculum."""
    return {
        "teacher": "Cassey",
        "protocol": "TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL",
        "authorization": "RTC 6/6 UNANIMOUS POC_VALIDATED",
        "total_modules": TOTAL_MODULES,
        "total_lessons": TOTAL_LESSONS,
        "target_agents": "710+",
        "modules": [
            {
                "id": m.id,
                "name": m.name,
                "lesson_count": len(m.lessons),
                "difficulties": list(set(l.difficulty for l in m.lessons)),
            }
            for m in CURRICULUM
        ],
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


def teach_lesson(lesson_id: str) -> dict[str, Any]:
    """Deliver a single lesson by ID."""
    for module in CURRICULUM:
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                return {
                    "teacher": "Cassey",
                    "module": module.name,
                    "lesson": {
                        "id": lesson.id,
                        "title": lesson.title,
                        "concept": lesson.concept,
                        "bracket_tag": lesson.bracket_tag,
                        "difficulty": lesson.difficulty,
                        "teaching_points": list(lesson.teaching_points),
                        "validation": {
                            "question": lesson.validation_question,
                            "answer_hint": lesson.expected_answer_contains,
                        },
                    },
                    "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
                }
    return {"error": f"Lesson {lesson_id} not found"}


def validate_agent_answer(lesson_id: str, answer: str) -> dict[str, Any]:
    """Validate an agent's answer to a lesson question."""
    for module in CURRICULUM:
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                passed = lesson.expected_answer_contains.lower() in answer.lower()
                return {
                    "teacher": "Cassey",
                    "lesson_id": lesson_id,
                    "answer_given": answer[:200],
                    "passed": passed,
                    "verdict": "COMPETENCY_CONFIRMED" if passed else "NEEDS_REVIEW",
                    "bracket_tag": lesson.bracket_tag,
                }
    return {"error": f"Lesson {lesson_id} not found"}


def run_full_curriculum_validation() -> dict[str, Any]:
    """Run all curriculum lessons through self-validation."""
    results = []
    for module in CURRICULUM:
        for lesson in module.lessons:
            # Each lesson must have teaching points and a validation question
            has_points = len(lesson.teaching_points) > 0
            has_validation = len(lesson.validation_question) > 0
            has_answer = len(lesson.expected_answer_contains) > 0
            has_concept = len(lesson.concept) > 0

            results.append({
                "lesson_id": lesson.id,
                "title": lesson.title,
                "has_points": has_points,
                "has_validation": has_validation,
                "has_answer": has_answer,
                "has_concept": has_concept,
                "pass": all([has_points, has_validation, has_answer, has_concept]),
            })

    all_pass = all(r["pass"] for r in results)
    return {
        "teacher": "Cassey",
        "protocol": "TSAP",
        "curriculum_modules": TOTAL_MODULES,
        "curriculum_lessons": TOTAL_LESSONS,
        "tests_run": len(results),
        "tests_passed": sum(1 for r in results if r["pass"]),
        "all_pass": all_pass,
        "verdict": "CURRICULUM_VALIDATED" if all_pass else "CURRICULUM_INCOMPLETE",
        "results": results,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    import sys
    import io

    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("CASSEY ADAPTIVENESS CURRICULUM — TSAP TEACHING MODULE")
    print("=" * 72)

    summary = get_curriculum_summary()
    print(f"\nTeacher: {summary['teacher']}")
    print(f"Protocol: {summary['protocol']}")
    print(f"Authorization: {summary['authorization']}")
    print(f"Target Agents: {summary['target_agents']}")
    print(f"\nModules: {summary['total_modules']} | Lessons: {summary['total_lessons']}")

    for m in summary["modules"]:
        print(f"  {m['id']}  {m['name']} ({m['lesson_count']} lessons)")

    print("\n" + "-" * 72)
    print("CURRICULUM VALIDATION")
    print("-" * 72)

    report = run_full_curriculum_validation()
    for r in report["results"]:
        status = "OK" if r["pass"] else "FAIL"
        print(f"  [{status:>4}] {r['lesson_id']}  {r['title'][:55]}")

    print(f"\nTests: {report['tests_run']} / {report['tests_passed']} passed")
    print(f"Verdict: {report['verdict']}")

    # Deliver one sample lesson
    print("\n" + "-" * 72)
    print("SAMPLE LESSON DELIVERY")
    print("-" * 72)

    sample = teach_lesson("ADT-01-01")
    print(f"\n  Module: {sample['module']}")
    print(f"  Lesson: {sample['lesson']['title']}")
    print(f"  Concept: {sample['lesson']['concept']}")
    print(f"  Difficulty: {sample['lesson']['difficulty']}")
    print(f"  Points: {len(sample['lesson']['teaching_points'])}")
    for i, tp in enumerate(sample["lesson"]["teaching_points"], 1):
        print(f"    {i}. {tp}")
    print(f"  Validation Q: {sample['lesson']['validation']['question']}")

    # Validate a sample answer
    v = validate_agent_answer("ADT-01-01", "No, frozen dataclasses cannot be modified")
    print(f"\n  Answer validation: {v['verdict']}")

    print(f"\nCONSTRAINT: {report['constraint']}")
    print("=" * 72)
