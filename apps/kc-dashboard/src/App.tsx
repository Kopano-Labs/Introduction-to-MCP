import { useState } from "react";
import dashboardState from "../../../governance/kpgs-vnext/kc/dashboard-state.json";
import EverydayMode from "./EverydayMode";
import OperatorMode from "./OperatorMode";
import { KCSpatialLab } from "./components/KCSpatialLab";
import "./everyday.css";

type ViewMode = "everyday" | "operator" | "spatial_lab";

export default function App() {
  // Everyday Mode is intentionally the default.
  // Spatial Lab and Operator Mode are accessible on-demand.
  const [mode, setMode] = useState<ViewMode>("everyday");

  if (mode === "spatial_lab") {
    return (
      <KCSpatialLab
        onBackToEveryday={() => setMode("everyday")}
        onOpenOperatorMode={() => setMode("operator")}
      />
    );
  }

  if (mode === "operator") {
    return <OperatorMode onOpenEverydayMode={() => setMode("everyday")} />;
  }

  return (
    <EverydayMode
      attentionItems={dashboardState.gates.map((gate) => gate.label)}
      snapshotLabel="saved system snapshot"
      onOpenOperatorMode={() => setMode("operator")}
      onOpenSpatialLab={() => setMode("spatial_lab")}
    />
  );
}
