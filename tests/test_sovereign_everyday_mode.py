from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/kc-dashboard/src/App.tsx"
EVERYDAY = ROOT / "apps/kc-dashboard/src/EverydayMode.tsx"
STORE = ROOT / "apps/kc-dashboard/src/everyday-store.ts"
MODEL = ROOT / "apps/kc-dashboard/src/everyday-model.ts"
CSS = ROOT / "apps/kc-dashboard/src/everyday.css"


class SovereignEverydayModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = APP.read_text(encoding="utf-8")
        cls.everyday = EVERYDAY.read_text(encoding="utf-8")
        cls.store = STORE.read_text(encoding="utf-8")
        cls.model = MODEL.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")

    def test_everyday_mode_is_default_but_operator_view_is_preserved(self):
        self.assertIn('useState<ViewMode>("everyday")', self.app)
        self.assertIn("<EverydayMode", self.app)
        self.assertIn("<OperatorMode", self.app)
        self.assertIn("Operator view", self.everyday)

    def test_everyday_surface_avoids_infrastructure_jargon(self):
        # Technical terms remain available in OperatorMode, not in the default
        # non-technical surface.
        visible_source = self.everyday.casefold()
        for forbidden in ("kpgs", "mcp", ".net", "websocket", "sub-membrane"):
            self.assertNotIn(forbidden, visible_source)

    def test_permission_reason_and_consequence_are_progressively_disclosed(self):
        self.assertIn("Why am I seeing this?", self.everyday)
        self.assertIn("permission.reason", self.everyday)
        self.assertIn("permission.consequence", self.everyday)
        self.assertIn("I understand this is a read-only review.", self.everyday)
        self.assertIn("disabled={!pilot.permissionAcknowledged}", self.everyday)

    def test_profile_reset_cannot_touch_pilot_progress_storage(self):
        match = re.search(
            r"export function resetInteractionProfile\(\) \{(?P<body>.*?)\n\}",
            self.store,
            flags=re.S,
        )
        self.assertIsNotNone(match)
        body = match.group("body") if match else ""
        self.assertIn("PROFILE_STORAGE_KEY", body)
        self.assertNotIn("PILOT_STORAGE_KEY", body)
        self.assertNotIn("pilotSnapshot", body)
        self.assertNotEqual(
            re.search(r'PROFILE_STORAGE_KEY = "([^"]+)"', self.model).group(1),
            re.search(r'PILOT_STORAGE_KEY = "([^"]+)"', self.model).group(1),
        )

    def test_account_sync_requires_explicit_consent_and_is_not_claimed_live(self):
        self.assertIn("accountSyncConsent", self.everyday)
        self.assertIn("event.target.checked", self.everyday)
        self.assertIn("No account sync is connected", self.everyday)
        self.assertIn("accountSyncAllowed", self.model)

    def test_runtime_adaptation_is_separate_from_weight_training(self):
        self.assertIn("modelWeightTraining: false", self.model)
        self.assertIn("They do not retrain model weights", self.everyday)
        self.assertIn("fine-tuning is a separate governed process", self.everyday)

    def test_offline_state_is_visible_and_recoverable(self):
        self.assertIn('aria-label="Connection status"', self.everyday)
        self.assertIn('aria-live="polite"', self.everyday)
        self.assertIn("Try again", self.everyday)
        self.assertIn("window.location.reload()", self.everyday)
        self.assertIn("Live status may be out of date", self.model)

    def test_accessibility_uses_semantic_controls_and_reduced_motion(self):
        self.assertGreaterEqual(self.everyday.count('type="button"'), 6)
        self.assertIn("<label", self.everyday)
        self.assertIn("<details", self.everyday)
        self.assertIn("<summary", self.everyday)
        self.assertIn("aria-live", self.everyday)
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn(":focus-visible", self.css)

    def test_mobile_controls_have_touch_sized_targets(self):
        self.assertIn("@media (max-width: 620px)", self.css)
        self.assertRegex(self.css, r"\.primary-button,\s*\n\s*\.secondary-button \{[^}]*min-height: 48px")
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("grid-template-columns: 1fr", self.css)

    def test_completion_copy_cannot_be_confused_with_system_mutation(self):
        self.assertIn("No protected system state will change.", self.everyday)
        self.assertIn("No website, permission, release, or protected setting was changed.", self.everyday)
        self.assertIn("canonicalWorkflowState: false", self.model)


if __name__ == "__main__":
    unittest.main()
