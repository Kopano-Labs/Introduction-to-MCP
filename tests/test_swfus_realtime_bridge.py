import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest

KOPANO_DIR = Path(__file__).parents[1] / "kopano-core" / "kopano"

package = types.ModuleType("kopano")
package.__path__ = [str(KOPANO_DIR)]
sys.modules.setdefault("kopano", package)


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, KOPANO_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


realtime = load("kopano.realtime_event_plane", "realtime_event_plane.py")
bridge_mod = load("kopano.swfus_realtime_bridge", "swfus_realtime_bridge.py")


class SwfusRealtimeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.plane = realtime.RealtimeEventPlane(
            Path(self.tempdir.name) / "events.db"
        )
        self.context = bridge_mod.SwfusRealtimeContext(
            tenant_id="kopano",
            domain_id="fivesarena",
            session_id="session-live-001",
            task_id="task-update-001",
        )
        self.sink = bridge_mod.SwfusRealtimeDistributionSink(
            self.plane,
            self.context,
        )
        self.scope = realtime.EventScope(
            "kopano",
            "fivesarena",
            "session-live-001",
            "task-update-001",
        )

    def tearDown(self):
        self.plane.close()
        self.tempdir.cleanup()

    def distribution(self, **overrides):
        payload = {
            "schema": "kpgs.swfus.distribution.v1",
            "update_id": "update-001",
            "node_id": "arena-state-001",
            "operation": "UPDATE",
            "state_digest": "abc123",
            "evidence_refs": ["receipt://poc/001"],
            "correlation_id": "corr-001",
            "authority_effect": "none",
            "canonical": False,
            "transport_grants_authority": False,
        }
        payload.update(overrides)
        return payload

    def test_valid_swfus_distribution_becomes_replayable_progress(self):
        self.sink(self.distribution())
        events = self.plane.replay(self.scope)
        self.assertEqual(len(events), 1)
        event = events[0].as_dict()
        self.assertEqual(event["event_kind"], "task.progress")
        self.assertEqual(event["payload"]["stage"], "distribution")
        self.assertFalse(event["payload"]["canonical"])
        self.assertEqual(event["payload"]["authority_effect"], "none")
        self.assertEqual(event["evidence"][0]["ref"], "receipt://poc/001")

    def test_replayed_distribution_does_not_duplicate_observation(self):
        distribution = self.distribution()
        self.sink(distribution)
        self.sink(distribution)
        self.assertEqual(len(self.plane.replay(self.scope)), 1)

    def test_transport_cannot_accept_authority_widening(self):
        with self.assertRaises(ValueError):
            self.sink(self.distribution(authority_effect="grant"))
        with self.assertRaises(ValueError):
            self.sink(self.distribution(canonical=True))
        with self.assertRaises(ValueError):
            self.sink(self.distribution(transport_grants_authority=True))
        self.assertEqual(self.plane.replay(self.scope), [])

    def test_invalid_distribution_schema_is_fail_closed(self):
        with self.assertRaises(ValueError):
            self.sink(self.distribution(schema="other.schema"))
        self.assertEqual(self.plane.replay(self.scope), [])


if __name__ == "__main__":
    unittest.main()
