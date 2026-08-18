import unittest

from kopano import kasilink_realtime
from kopano.realtime_event_plane import EventScope, RealtimeEventPlane


class KasiLinkRealtimeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.previous_plane = kasilink_realtime._plane_instance
        self.plane = RealtimeEventPlane(":memory:")
        kasilink_realtime._plane_instance = self.plane

    def tearDown(self):
        kasilink_realtime._plane_instance = self.previous_plane
        self.plane.close()

    def test_real_match_workflow_emits_live_progress_without_authority(self):
        live = kasilink_realtime.begin_match(
            "session-kasilink-001",
            "task-kasilink-001",
            "corr-kasilink-001",
        )
        metadata = kasilink_realtime.complete_match(
            live,
            {"matches": [{"provider_id": "provider-001"}]},
        )

        scope = EventScope(
            "kopano",
            "kasilink",
            "session-kasilink-001",
            "task-kasilink-001",
        )
        events = [event.as_dict() for event in self.plane.replay(scope)]

        self.assertEqual(
            [event["event_kind"] for event in events],
            ["task.accepted", "task.started", "task.completed"],
        )
        self.assertEqual(
            [event["payload"]["state"] for event in events],
            ["working", "working", "done"],
        )
        self.assertEqual(metadata["state"], "done")
        self.assertEqual(metadata["transport_authority"], "none")
        self.assertEqual(metadata["resume_cursor"], events[-1]["cursor"])
        self.assertTrue(
            all(
                event["governing_spec_ref"]
                == "governance/kpgs-vnext/realtime/EVENT_PLANE.md"
                for event in events
            )
        )

    def test_replaying_same_domain_task_does_not_duplicate_events(self):
        first = kasilink_realtime.begin_match(
            "session-kasilink-002",
            "task-kasilink-002",
            "corr-kasilink-002",
        )
        second = kasilink_realtime.begin_match(
            "session-kasilink-002",
            "task-kasilink-002",
            "corr-kasilink-002",
        )
        self.assertEqual(first["resume_cursor"], second["resume_cursor"])

        scope = EventScope(
            "kopano",
            "kasilink",
            "session-kasilink-002",
            "task-kasilink-002",
        )
        events = self.plane.replay(scope)
        self.assertEqual(len(events), 2)
        self.assertEqual(
            [event.event_kind for event in events],
            ["task.accepted", "task.started"],
        )

    def test_partial_started_failure_preserves_accepted_identity(self):
        original_publish = kasilink_realtime._publish
        calls = 0

        def flaky_publish(**kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated journal interruption")
            return original_publish(**kwargs)

        kasilink_realtime._publish = flaky_publish
        try:
            live = kasilink_realtime.begin_match(
                "session-kasilink-003",
                "task-kasilink-003",
                "corr-kasilink-003",
            )
        finally:
            kasilink_realtime._publish = original_publish

        self.assertEqual(live["realtime_state"], "degraded")
        self.assertEqual(live["task_id"], "task-kasilink-003")
        scope = EventScope(
            "kopano",
            "kasilink",
            "session-kasilink-003",
            "task-kasilink-003",
        )
        events = self.plane.replay(scope)
        self.assertEqual([event.event_kind for event in events], ["task.accepted"])


if __name__ == "__main__":
    unittest.main()
