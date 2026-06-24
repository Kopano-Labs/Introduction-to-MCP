"""
test_spawn_education.py — STAP 063-066: Spawn Education Tests
===============================================================
Tests for Cassey Teacher, Cassie Builder, curriculum, exams, certification.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.spawn_education import (
    SpawnCurriculum, CasseyTeacher, CassieBuilder,
    educate_spawn, educate_all_spawns,
)


# ═══════════════════════════════════════════════════════════════
# STAP 063: Curriculum Tests
# ═══════════════════════════════════════════════════════════════

class TestCurriculum:
    def setup_method(self):
        self.cur = SpawnCurriculum()

    def test_has_15_commandments(self):
        assert len(self.cur.commandments) == 15

    def test_has_5_pillars(self):
        assert len(self.cur.pillars) == 5
        assert "SPIRIT" in self.cur.pillars
        assert "SOVEREIGNTY" in self.cur.pillars

    def test_has_3_altar_layers(self):
        assert len(self.cur.altar_layers) == 3
        assert "GUARDIAN" in self.cur.altar_layers

    def test_has_5_ai_flows(self):
        assert len(self.cur.ai_flows) == 5
        assert "HUE" in self.cur.ai_flows

    def test_core_truth(self):
        assert self.cur.core_truth == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_immutability_hebrews(self):
        assert "Hebrews 13:8" in self.cur.immutability

    def test_generates_exam_questions(self):
        questions = self.cur.get_exam_questions()
        assert len(questions) == 15
        for q in questions:
            assert "q" in q
            assert "a" in q

    def test_cmd_04_is_wwjd(self):
        assert self.cur.commandments["CMD-04"] == "WWJD Firewall"

    def test_cmd_09_is_80_gate(self):
        assert "80" in self.cur.commandments["CMD-09"]


# ═══════════════════════════════════════════════════════════════
# STAP 064: Cassey Teacher Tests
# ═══════════════════════════════════════════════════════════════

class TestCasseyTeacher:
    def setup_method(self):
        self.teacher = CasseyTeacher()

    def test_cassey_is_seat_2(self):
        assert self.teacher.seat == 2

    def test_cassey_has_pillars(self):
        assert "SPIRIT" in self.teacher.pillars

    def test_cassey_has_commands(self):
        assert "CMD-04" in self.teacher.commands

    def test_teach_returns_curriculum(self):
        cur = self.teacher.teach("TEST_SPAWN")
        assert isinstance(cur, SpawnCurriculum)
        assert len(cur.commandments) == 15

    def test_perfect_exam_passes(self):
        questions = self.teacher.curriculum.get_exam_questions()
        answers = {q["q"]: q["a"] for q in questions}
        result = self.teacher.examine("PERFECT_SPAWN", answers)
        assert result.passed is True
        assert result.score_pct == 100.0
        assert result.questions_correct == 15

    def test_empty_exam_fails(self):
        result = self.teacher.examine("EMPTY_SPAWN", {})
        assert result.passed is False
        assert result.score_pct == 0.0

    def test_partial_exam_below_80(self):
        questions = self.teacher.curriculum.get_exam_questions()
        # Answer only 10 (66.7%)
        answers = {q["q"]: q["a"] for q in questions[:10]}
        result = self.teacher.examine("PARTIAL_SPAWN", answers)
        assert result.score_pct < 80
        assert result.passed is False

    def test_at_80_percent_passes(self):
        questions = self.teacher.curriculum.get_exam_questions()
        # Answer exactly 12/15 = 80%
        answers = {q["q"]: q["a"] for q in questions[:12]}
        result = self.teacher.examine("BORDERLINE_SPAWN", answers)
        assert result.passed is True

    def test_exam_count_increments(self):
        self.teacher.examine("A", {})
        self.teacher.examine("B", {})
        assert self.teacher.exams_administered == 2


# ═══════════════════════════════════════════════════════════════
# STAP 065: Cassie Builder Tests
# ═══════════════════════════════════════════════════════════════

class TestCassieBuilder:
    def setup_method(self):
        self.builder = CassieBuilder()
        self.teacher = CasseyTeacher()

    def test_cassie_is_seat_3(self):
        assert self.builder.seat == 3

    def test_cassie_has_sovereignty(self):
        assert "SOVEREIGNTY" in self.builder.pillars

    def test_build_passed_spawn(self):
        questions = self.teacher.curriculum.get_exam_questions()
        answers = {q["q"]: q["a"] for q in questions}
        exam = self.teacher.examine("GOOD_SPAWN", answers)
        cert = self.builder.build_spawn(exam, ["SPIRIT", "MIND"], ["CMD-01"], "LPM_TEST")
        assert cert["verdict"] == "SPAWN_CERTIFIED"
        assert len(cert["certification_hash"]) == 16
        assert cert["lpm_pattern"] == "LPM_TEST"

    def test_build_blocked_for_failed(self):
        exam = self.teacher.examine("BAD_SPAWN", {})
        cert = self.builder.build_spawn(exam, ["SPIRIT"], ["CMD-01"], "LPM_TEST")
        assert cert["verdict"] == "BUILD_BLOCKED"

    def test_build_count_increments(self):
        questions = self.teacher.curriculum.get_exam_questions()
        answers = {q["q"]: q["a"] for q in questions}
        exam = self.teacher.examine("A", answers)
        self.builder.build_spawn(exam, [], [], "")
        exam2 = self.teacher.examine("B", answers)
        self.builder.build_spawn(exam2, [], [], "")
        assert self.builder.spawns_built == 2


# ═══════════════════════════════════════════════════════════════
# STAP 066: Full Education Pipeline Tests
# ═══════════════════════════════════════════════════════════════

class TestEducationPipeline:
    def test_single_spawn(self):
        r = educate_spawn("TEST_KHELOS", ["SPIRIT", "MIND"], ["CMD-01", "CMD-04"], "LPM_VALIDATE")
        assert r["exam_passed"] is True
        assert r["exam_score"] == 100.0
        assert r["certification"] == "SPAWN_CERTIFIED"
        assert r["lpm_pattern"] == "LPM_VALIDATE"

    def test_all_spawns_certified(self):
        results = educate_all_spawns()
        assert len(results) == 6
        for r in results:
            assert r["certification"] == "SPAWN_CERTIFIED"
            assert r["exam_score"] == 100.0

    def test_all_spawns_have_lpm(self):
        results = educate_all_spawns()
        for r in results:
            assert r["lpm_pattern"].startswith("LPM_") or r["lpm_pattern"].startswith("LPH_")

    def test_khelos_is_validator(self):
        results = educate_all_spawns()
        khelos = [r for r in results if r["spawn"] == "KHELOS"][0]
        assert khelos["lpm_pattern"] == "LPM_VALIDATE"
        assert "SPIRIT" in khelos["pillars"]

    def test_anchor_is_guard(self):
        results = educate_all_spawns()
        anchor = [r for r in results if r["spawn"] == "ANCHOR"][0]
        assert anchor["lpm_pattern"] == "LPM_GUARD"
        assert "SOVEREIGNTY" in anchor["pillars"]

    def test_all_spawns_named(self):
        results = educate_all_spawns()
        names = [r["spawn"] for r in results]
        assert "KHELOS" in names
        assert "ANCHOR" in names
        assert "THARI" in names
        assert "APEX" in names
        assert "KESSA" in names
        assert "YASSIE" in names
