import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).parents[1] / "kopano-core" / "kopano" / "realtime_event_plane.py"
spec = importlib.util.spec_from_file_location("realtime_event_plane_vnext", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class RealtimeEventPlaneTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "events.db"
        self.plane = mod.RealtimeEventPlane(
            self.db,
            max_events_per_stream=4,
            queue_limit=1,
        )
        self.scope = mod.EventScope("kopano", "kasilink", "session-001")
        self.principal = {
            "tenant_id": "kopano",
            "domain_id": "kasilink",
            "is_active": True,
        }

    def tearDown(self):
        self.plane.close()
        self.tempdir.cleanup()

    def event(self, n, kind="task.progress", idem=None, payload=None):
        return mod.make_event(
            event_id=f"event-{n:03d}",
            event_kind=kind,
            tenant_id="kopano",
            domain_id="kasilink",
            session_id="session-001",
            task_id="task-001",
            correlation_id="corr-001",
            idempotency_key=idem,
            payload=payload or {"step": n},
        )

    def test_socket_disconnect_does_not_delete_persisted_events(self):
        first = self.plane.publish(self.event(1, "task.accepted"))
        subscription, replay = self.plane.subscribe(
            self.principal,
            self.scope,
            after_cursor=0,
            subscription_id="sub-1",
        )
        self.assertEqual([event.cursor for event in replay], [first.cursor])

        self.plane.unsubscribe(subscription.subscription_id)
        self.plane.close()
        self.plane = mod.RealtimeEventPlane(
            self.db,
            max_events_per_stream=4,
            queue_limit=1,
        )
        restored = self.plane.replay(self.scope, after_cursor=0)
        self.assertEqual([event.event_id for event in restored], ["event-001"])

    def test_reconnect_resumes_after_acknowledged_cursor(self):
        one = self.plane.publish(self.event(1, "task.accepted"))
        two = self.plane.publish(self.event(2, "task.started"))

        replay = self.plane.polling_fallback(
            self.principal,
            self.scope,
            after_cursor=one.cursor,
        )
        self.assertEqual(
            [event["event_id"] for event in replay["events"]],
            [two.event_id],
        )
        self.assertEqual(replay["resume_cursor"], two.cursor)
        self.assertTrue(replay["caught_up"])

    def test_duplicate_delivery_is_idempotent_and_collision_is_rejected(self):
        event = self.event(1, idem="idem-1")
        first = self.plane.publish(event)
        again = self.plane.publish(event)
        self.assertEqual(first.cursor, again.cursor)
        self.assertEqual(len(self.plane.replay(self.scope)), 1)

        collision = self.event(2, idem="idem-1", payload={"step": 999})
        with self.assertRaises(mod.EventConflict):
            self.plane.publish(collision)

    def test_unauthorized_scope_is_rejected_server_side(self):
        wrong = {
            "tenant_id": "other",
            "domain_id": "kasilink",
            "is_active": True,
        }
        with self.assertRaises(mod.UnauthorizedScope):
            self.plane.polling_fallback(wrong, self.scope)
        with self.assertRaises(mod.UnauthorizedScope):
            self.plane.subscribe(
                wrong,
                self.scope,
                subscription_id="forbidden",
            )

    def test_bounded_queue_never_blocks_producer_and_replay_recovers(self):
        subscription, _ = self.plane.subscribe(
            self.principal,
            self.scope,
            subscription_id="slow",
        )
        self.plane.publish(self.event(1, "task.started"))
        self.plane.publish(self.event(2, "task.completed"))

        self.assertTrue(subscription.overflowed)
        self.assertEqual(
            [event.event_id for event in self.plane.replay(self.scope)],
            ["event-001", "event-002"],
        )

    def test_noncritical_overflow_is_counted_without_claiming_delivery(self):
        subscription, _ = self.plane.subscribe(
            self.principal,
            self.scope,
            subscription_id="slow",
        )
        self.plane.publish(self.event(1, "task.progress"))
        self.plane.publish(self.event(2, "task.progress"))

        self.assertFalse(subscription.overflowed)
        self.assertEqual(subscription.dropped_noncritical, 1)

    def test_expired_cursor_requires_snapshot_recovery(self):
        for number in range(1, 7):
            self.plane.publish(self.event(number))

        with self.assertRaises(mod.CursorExpired) as context:
            self.plane.replay(self.scope, after_cursor=1)
        self.assertEqual(context.exception.oldest_cursor, 3)

    def test_ack_cannot_move_backward_or_ahead(self):
        event = self.plane.publish(self.event(1))
        subscription, _ = self.plane.subscribe(
            self.principal,
            self.scope,
            subscription_id="sub",
        )
        self.plane.acknowledge(subscription, event.cursor)
        with self.assertRaises(mod.RealtimeEventError):
            self.plane.acknowledge(subscription, 0)
        with self.assertRaises(mod.RealtimeEventError):
            self.plane.acknowledge(subscription, event.cursor + 10)

    def test_task_filtered_polling_uses_relevant_highwater(self):
        self.plane.publish(self.event(1, "task.started"))
        other = mod.make_event(
            event_id="event-other",
            event_kind="task.started",
            tenant_id="kopano",
            domain_id="kasilink",
            session_id="session-001",
            task_id="task-002",
            correlation_id="corr-002",
            payload={"step": "other"},
        )
        self.plane.publish(other)

        task_scope = mod.EventScope(
            "kopano",
            "kasilink",
            "session-001",
            "task-001",
        )
        result = self.plane.polling_fallback(
            self.principal,
            task_scope,
            after_cursor=0,
        )
        self.assertEqual(
            [item["event_id"] for item in result["events"]],
            ["event-001"],
        )
        self.assertEqual(result["latest_cursor"], 1)
        self.assertTrue(result["caught_up"])

    def test_canonical_failure_fields_survive_transport_framing(self):
        event = self.event(1, "task.failed")
        event["failure"] = {
            "code": "execution_failed",
            "recoverability": "retry",
        }
        persisted = self.plane.publish(event)
        self.assertEqual(
            persisted.as_dict()["failure"]["code"],
            "execution_failed",
        )


if __name__ == "__main__":
    unittest.main()
