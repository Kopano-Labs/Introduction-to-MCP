import { useState } from "react";
import dashboardState from "../../../governance/kpgs-vnext/kc/dashboard-state.json";
import EverydayMode from "./EverydayMode";
import OperatorMode from "./OperatorMode";
import "./everyday.css";

type ViewMode = "everyday" | "operator";

export default function App() {
  // Everyday Mode is intentionally the default. Technical topology remains
  // available to operators without forcing non-technical users through it.
  const [mode, setMode] = useState<ViewMode>("everyday");

  if (mode === "operator") {
    return <OperatorMode onOpenEverydayMode={() => setMode("everyday")} />;
  }

  return (
    <EverydayMode
      attentionItems={dashboardState.gates.map((gate) => gate.label)}
      snapshotLabel="saved system snapshot"
      onOpenOperatorMode={() => setMode("operator")}
    />
  );
}
