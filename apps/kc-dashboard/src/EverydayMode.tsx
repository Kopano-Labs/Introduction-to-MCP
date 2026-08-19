import { useMemo } from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  connectionMessage,
  friendlyGate,
  nextPilotState,
  permissionExplanation,
  runtimeAdaptation,
  serializeProfile,
  type DetailDensity,
  type ExplanationStyle,
  type Initiative,
  type Pace,
} from "./everyday-model";
import {
  patchInteractionProfile,
  resetInteractionProfile,
  resetPilotProgress,
  setPilotProgress,
  useInteractionProfile,
  useOnlineStatus,
  usePilotProgress,
} from "./everyday-store";

type EverydayModeProps = {
  attentionItems: string[];
  snapshotLabel: string;
  onOpenOperatorMode: () => void;
};

const detailOptions: Array<{ value: DetailDensity; label: string }> = [
  { value: "compact", label: "Keep it short" },
  { value: "balanced", label: "Give me enough context" },
  { value: "detailed", label: "Show more detail" },
];
const paceOptions: Array<{ value: Pace; label: string }> = [
  { value: "calm", label: "Calm" },
  { value: "normal", label: "Normal" },
  { value: "fast", label: "Fast" },
];
const initiativeOptions: Array<{ value: Initiative; label: string }> = [
  { value: "low", label: "Wait for me" },
  { value: "balanced", label: "Suggest the next step" },
  { value: "high", label: "Be proactive" },
];
const explanationOptions: Array<{ value: ExplanationStyle; label: string }> = [
  { value: "plain", label: "Plain language" },
  { value: "steps", label: "Step by step" },
  { value: "why", label: "Explain why" },
];

function downloadProfile(payload: string) {
  const blob = new Blob([payload], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "my-interaction-settings.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function EverydayMode({
  attentionItems,
  snapshotLabel,
  onOpenOperatorMode,
}: EverydayModeProps) {
  const reduceMotion = useReducedMotion();
  const profile = useInteractionProfile();
  const pilot = usePilotProgress();
  const online = useOnlineStatus();
  const connection = connectionMessage({ online, reconnecting: false });
  const permission = permissionExplanation();
  const adaptation = useMemo(() => runtimeAdaptation(profile), [profile]);
  const friendlyItems = useMemo(
    () => attentionItems.map(friendlyGate),
    [attentionItems],
  );

  const move = (event: "continue" | "acknowledge" | "complete" | "restart") => {
    setPilotProgress(nextPilotState(pilot, event));
  };

  return (
    <main className="everyday-shell">
      <header className="everyday-topbar">
        <div className="everyday-brand">
          <div className="everyday-mark" aria-hidden="true">K</div>
          <div>
            <p className="everyday-kicker">Your system</p>
            <h1>What needs your attention?</h1>
          </div>
        </div>
        <button type="button" className="quiet-button" onClick={onOpenOperatorMode}>
          Operator view
        </button>
      </header>

      <section
        className={`connection-card ${online ? "is-online" : "is-offline"}`}
        aria-live="polite"
        aria-label="Connection status"
      >
        <span className="connection-dot" aria-hidden="true" />
        <div>
          <strong>{connection.title}</strong>
          <p>{connection.detail}</p>
          {connection.action && <small>{connection.action}</small>}
        </div>
        {!online && (
          <button type="button" className="secondary-button" onClick={() => window.location.reload()}>
            Try again
          </button>
        )}
      </section>

      <section className="everyday-grid">
        <motion.article
          className="everyday-card next-action-card"
          initial={reduceMotion ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.32 }}
          aria-labelledby="pilot-title"
        >
          <div className="card-heading">
            <div>
              <p className="everyday-kicker">One clear next step</p>
              <h2 id="pilot-title">Review what is still waiting</h2>
            </div>
            <span className="attention-count">{attentionItems.length} items</span>
          </div>

          {pilot.step === "understand" && (
            <div className="pilot-step">
              <p className="lead-copy">
                Some work is ready, and some still needs evidence before it can safely move forward.
                Start with a short review; nothing will be changed.
              </p>
              <ul className="friendly-list" aria-label="Items needing attention">
                {friendlyItems.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
              </ul>
              <button type="button" className="primary-button" onClick={() => move("continue")}>
                Review safely
              </button>
            </div>
          )}

          {pilot.step === "permission" && (
            <div className="pilot-step">
              <div className="permission-card">
                <span className="permission-icon" aria-hidden="true">✓</span>
                <div>
                  <strong>{permission.scope}</strong>
                  <p>{permission.consequence}</p>
                </div>
              </div>
              <details className="why-details">
                <summary>Why am I seeing this?</summary>
                <p>{permission.reason}</p>
                <p><strong>What this can do:</strong> {permission.action}.</p>
              </details>
              <label className="ack-row">
                <input
                  type="checkbox"
                  checked={pilot.permissionAcknowledged}
                  onChange={() => move("acknowledge")}
                />
                <span>I understand this is a read-only review.</span>
              </label>
              <button
                type="button"
                className="primary-button"
                disabled={!pilot.permissionAcknowledged}
                onClick={() => move("continue")}
              >
                Continue
              </button>
            </div>
          )}

          {pilot.step === "confirm" && (
            <div className="pilot-step">
              <p className="lead-copy">
                You have reviewed the current blockers. Finishing this review only saves your progress on this device.
              </p>
              <div className="safe-summary" role="status">
                <strong>No protected system state will change.</strong>
                <span>You can come back to this review after reconnecting or refreshing.</span>
              </div>
              <button type="button" className="primary-button" onClick={() => move("complete")}>
                Finish review
              </button>
            </div>
          )}

          {pilot.step === "complete" && (
            <div className="pilot-step complete-step" aria-live="polite">
              <span className="complete-mark" aria-hidden="true">✓</span>
              <div>
                <h3>Review complete</h3>
                <p>Your progress is saved on this device. No website, permission, release, or protected setting was changed.</p>
                <small>{pilot.completedAt ? `Saved ${new Date(pilot.completedAt).toLocaleString()}` : "Saved locally"}</small>
              </div>
              <button type="button" className="secondary-button" onClick={() => resetPilotProgress()}>
                Start again
              </button>
            </div>
          )}
        </motion.article>

        <aside className="everyday-card status-card" aria-labelledby="status-title">
          <p className="everyday-kicker">Current view</p>
          <h2 id="status-title">What you can trust here</h2>
          <div className="trust-row">
            <span>Saved preferences</span><strong>This device</strong>
          </div>
          <div className="trust-row">
            <span>Review progress</span><strong>This device</strong>
          </div>
          <div className="trust-row">
            <span>Live status</span><strong>{online ? "Available" : "May be stale"}</strong>
          </div>
          <p className="snapshot-note">Source view: {snapshotLabel}. A saved preference never becomes permission to change protected work.</p>
        </aside>
      </section>

      <section className="everyday-card settings-card" aria-labelledby="settings-title">
        <div className="card-heading">
          <div>
            <p className="everyday-kicker">Make it feel more like you</p>
            <h2 id="settings-title">Interaction settings</h2>
          </div>
          <div className="settings-actions">
            <button type="button" className="quiet-button" onClick={() => downloadProfile(serializeProfile(profile))}>
              Export
            </button>
            <button type="button" className="quiet-button" onClick={() => resetInteractionProfile()}>
              Reset
            </button>
          </div>
        </div>

        <div className="settings-grid">
          <label className="setting-field">
            <span>Warmth <b>{profile.warmth}/5</b></span>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={profile.warmth}
              onChange={(event) => patchInteractionProfile({ warmth: Number(event.target.value) })}
            />
          </label>

          <SelectSetting
            label="Detail"
            value={profile.detailDensity}
            options={detailOptions}
            onChange={(value) => patchInteractionProfile({ detailDensity: value as DetailDensity })}
          />
          <SelectSetting
            label="Pace"
            value={profile.pace}
            options={paceOptions}
            onChange={(value) => patchInteractionProfile({ pace: value as Pace })}
          />
          <SelectSetting
            label="Initiative"
            value={profile.initiative}
            options={initiativeOptions}
            onChange={(value) => patchInteractionProfile({ initiative: value as Initiative })}
          />
          <SelectSetting
            label="Explanation style"
            value={profile.explanationStyle}
            options={explanationOptions}
            onChange={(value) => patchInteractionProfile({ explanationStyle: value as ExplanationStyle })}
          />

          <label className="setting-field consent-field">
            <span>Account sync</span>
            <span className="toggle-copy">
              <input
                type="checkbox"
                checked={profile.accountSyncConsent}
                onChange={(event) => patchInteractionProfile({ accountSyncConsent: event.target.checked })}
              />
              <span>Allow these preferences to be synced if account sync is connected later.</span>
            </span>
            <small>No account sync is connected in this reference experience.</small>
          </label>
        </div>

        <details className="adaptation-details">
          <summary>How these settings affect responses</summary>
          <p>
            They can change response warmth, length, pace, initiative, and supported inference hints at runtime.
            They do not retrain model weights. Training or fine-tuning is a separate governed process and is not active here.
          </p>
          <code aria-label="Current runtime adaptation summary">
            {JSON.stringify(adaptation, null, 2)}
          </code>
        </details>
      </section>

      <footer className="everyday-footer">
        <span>Simple by default · details when you ask</span>
        <span>Your local preferences are not authority.</span>
      </footer>
    </main>
  );
}

function SelectSetting({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  onChange: (value: string) => void;
}) {
  return (
    <label className="setting-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option value={option.value} key={option.value}>{option.label}</option>
        ))}
      </select>
    </label>
  );
}
