import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).parents[1] / "kopano-core" / "kopano" / "swfus_engine.py"
spec = importlib.util.spec_from_file_location("swfus_engine_vnext", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class SwfusProgressiveUpdateTests(unittest.TestCase):
    def setUp(self):
        self.engine = mod.SwfusHierarchy()

    def update(self, **overrides):
        payload = dict(
            update_id="update-001",
            node_id="node-001",
            operation=mod.CrudOperation.CREATE,
            lane="arena.public-state",
            context_route="fivesarena.locality",
            protocol="APU->CRUD->SWFUS",
            idempotency_key="idem-001",
            value={"province": "western-cape"},
            apu_status="GREEN",
            poc_validated=True,
            foc_detected=False,
            invariant_passed=True,
            authority_effect="none",
            state_class="non_authoritative",
            evidence_refs=("receipt://poc/001",),
            correlation_id="corr-001",
            boundary_marker="#NB",
        )
        payload.update(overrides)
        return mod.ProgressiveUpdate(**payload)

    def test_exact_canonical_stage_order_is_always_receipted(self):
        receipt = self.engine.execute_update(self.update())
        self.assertEqual(
            [stage.stage for stage in receipt.stages],
            list(mod.SWFUS_STAGE_ORDER),
        )
        self.assertEqual(receipt.disposition, mod.UpdateDisposition.APPLIED.value)
        self.assertTrue(receipt.synchronized)
        self.assertFalse(receipt.canonical_authority_changed)

    def test_red_or_foc_update_never_reaches_state_or_distribution(self):
        receipt = self.engine.execute_update(
            self.update(apu_status="RED", foc_detected=True)
        )
        statuses = {stage.stage: stage.status for stage in receipt.stages}
        self.assertEqual(receipt.disposition, mod.UpdateDisposition.REJECTED.value)
        self.assertEqual(statuses["POC_FOC_CHECK"], "REJECT")
        self.assertEqual(statuses["STATE_UPDATE"], "NOT_REACHED")
        self.assertEqual(statuses["DISTRIBUTION"], "NOT_REACHED")
        self.assertNotIn("node-001", self.engine.projection_store)
        self.assertEqual(self.engine.distribution_log, [])

    def test_yellow_apu_holds_before_mutation(self):
        receipt = self.engine.execute_update(self.update(apu_status="YELLOW"))
        self.assertEqual(receipt.disposition, mod.UpdateDisposition.HELD.value)
        self.assertNotIn("node-001", self.engine.projection_store)
        self.assertFalse(receipt.synchronized)

    def test_mutation_without_poc_or_evidence_is_held(self):
        no_poc = self.engine.execute_update(
            self.update(idempotency_key="no-poc", poc_validated=False)
        )
        no_evidence = self.engine.execute_update(
            self.update(update_id="update-002", idempotency_key="no-evidence", evidence_refs=())
        )
        self.assertEqual(no_poc.disposition, mod.UpdateDisposition.HELD.value)
        self.assertEqual(no_evidence.disposition, mod.UpdateDisposition.HELD.value)
        self.assertEqual(self.engine.distribution_log, [])

    def test_authoritative_state_or_authority_effect_is_rejected(self):
        authoritative_class = self.engine.execute_update(
            self.update(idempotency_key="auth-class", state_class="constitutional_truth")
        )
        authority_effect = self.engine.execute_update(
            self.update(update_id="update-002", idempotency_key="auth-effect", authority_effect="canonical-write")
        )
        self.assertEqual(authoritative_class.disposition, mod.UpdateDisposition.REJECTED.value)
        self.assertEqual(authority_effect.disposition, mod.UpdateDisposition.REJECTED.value)
        self.assertFalse(authoritative_class.canonical_authority_changed)
        self.assertFalse(authority_effect.canonical_authority_changed)

    def test_read_is_available_after_routing_and_never_mutates_or_distributes(self):
        created = self.engine.execute_update(self.update())
        before = dict(self.engine.projection_store["node-001"])
        distribution_count = len(self.engine.distribution_log)
        read = self.engine.execute_update(
            self.update(
                update_id="read-001",
                operation=mod.CrudOperation.READ,
                idempotency_key="read-idem",
                protocol="",
                poc_validated=False,
                evidence_refs=(),
            )
        )
        self.assertEqual(created.disposition, mod.UpdateDisposition.APPLIED.value)
        self.assertEqual(read.disposition, mod.UpdateDisposition.OBSERVED.value)
        self.assertEqual(self.engine.projection_store["node-001"], before)
        self.assertEqual(len(self.engine.distribution_log), distribution_count)
        statuses = {stage.stage: stage.status for stage in read.stages}
        self.assertEqual(statuses["ROUTING"], "PASS")
        self.assertEqual(statuses["STATE_UPDATE"], "OBSERVE")
        self.assertEqual(statuses["DISTRIBUTION"], "SKIP")

    def test_create_update_delete_are_bounded_and_versioned(self):
        create = self.engine.execute_update(self.update())
        self.assertEqual(create.disposition, "APPLIED")
        self.assertEqual(self.engine.projection_store["node-001"]["version"], 1)

        update = self.engine.execute_update(
            self.update(
                update_id="update-002",
                operation=mod.CrudOperation.UPDATE,
                idempotency_key="idem-002",
                value={"province": "gauteng"},
                expected_version=1,
            )
        )
        self.assertEqual(update.disposition, "APPLIED")
        self.assertEqual(self.engine.projection_store["node-001"]["version"], 2)
        self.assertEqual(self.engine.projection_store["node-001"]["value"]["province"], "gauteng")

        stale = self.engine.execute_update(
            self.update(
                update_id="update-stale",
                operation=mod.CrudOperation.UPDATE,
                idempotency_key="idem-stale",
                value={"province": "limpopo"},
                expected_version=1,
            )
        )
        self.assertEqual(stale.disposition, "HELD")
        self.assertEqual(self.engine.projection_store["node-001"]["version"], 2)

        delete = self.engine.execute_update(
            self.update(
                update_id="delete-001",
                operation=mod.CrudOperation.DELETE,
                idempotency_key="idem-delete",
                value=None,
                expected_version=2,
            )
        )
        self.assertEqual(delete.disposition, "APPLIED")
        self.assertNotIn("node-001", self.engine.projection_store)

    def test_exact_idempotent_replay_has_no_duplicate_effect_or_distribution(self):
        update = self.update()
        first = self.engine.execute_update(update)
        version = self.engine.projection_store["node-001"]["version"]
        event_count = len(self.engine.distribution_log)
        second = self.engine.execute_update(update)

        self.assertEqual(first.receipt_id, second.receipt_id)
        self.assertTrue(second.replayed)
        self.assertEqual(self.engine.projection_store["node-001"]["version"], version)
        self.assertEqual(len(self.engine.distribution_log), event_count)

    def test_idempotency_collision_fails_closed(self):
        first = self.engine.execute_update(self.update())
        collision = self.engine.execute_update(
            self.update(value={"different": True})
        )
        self.assertEqual(first.disposition, "APPLIED")
        self.assertEqual(collision.disposition, "REJECTED")
        self.assertIn("collision", collision.stages[0].reason)
        self.assertEqual(len(self.engine.distribution_log), 1)

    def test_distribution_failure_rolls_back_projection(self):
        def fail(_event):
            raise RuntimeError("transport unavailable")

        engine = mod.SwfusHierarchy(distribution_sink=fail)
        receipt = engine.execute_update(self.update())
        self.assertEqual(receipt.disposition, "HELD")
        self.assertFalse(receipt.synchronized)
        self.assertNotIn("node-001", engine.projection_store)
        self.assertEqual(engine.distribution_log, [])
        self.assertEqual(receipt.stages[-1].stage, "DISTRIBUTION")
        self.assertEqual(receipt.stages[-1].status, "HOLD")

    def test_boundary_marker_is_enforced_without_inventing_expansion(self):
        receipt = self.engine.execute_update(
            self.update(boundary_marker="invented-expansion")
        )
        self.assertEqual(receipt.disposition, "REJECTED")
        self.assertEqual(receipt.stages[4].stage, "INVARIANT_AUDIT")
        self.assertIn("#NB", receipt.stages[4].reason)

    def test_legacy_payload_is_routed_through_new_gates(self):
        safe = mod.SwfusPayload("legacy-node", "TELEMETRY_INGESTION", 42.0, False)
        unsafe = mod.SwfusPayload("bad-node", "TELEMETRY_INGESTION", 101.0, False)
        self.assertTrue(self.engine.execute(safe))
        self.assertFalse(self.engine.execute(unsafe))
        self.assertIn("legacy-node", self.engine.projection_store)
        self.assertNotIn("bad-node", self.engine.projection_store)
        self.assertEqual(len(self.engine.distribution_log), 1)

    def test_legacy_exact_retry_reuses_prior_receipt_without_update_side_effect(self):
        payload = mod.SwfusPayload(
            "legacy-retry-node",
            "TELEMETRY_INGESTION",
            21.0,
            False,
        )
        self.assertTrue(self.engine.execute(payload))
        first_record = dict(self.engine.projection_store["legacy-retry-node"])
        first_events = len(self.engine.distribution_log)

        self.assertTrue(self.engine.execute(payload))
        self.assertEqual(
            self.engine.projection_store["legacy-retry-node"],
            first_record,
        )
        self.assertEqual(len(self.engine.distribution_log), first_events)
        self.assertEqual(first_record["version"], 1)


if __name__ == "__main__":
    unittest.main()
