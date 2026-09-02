import { useState } from "react";
import dashboardState from "../../../governance/kpgs-vnext/kc/dashboard-state.json";
import EverydayMode from "./EverydayMode";
import OperatorMode from "./OperatorMode";
import { KCSpatialLab } from "./components/KCSpatialLab";
import { RTCCouncilIdentities } from "./components/RTCCouncilIdentities";
import "./everyday.css";

type ViewMode = "everyday" | "operator" | "spatial_lab" | "rtc_council";

export default function App() {
  // Everyday Mode is intentionally the default.
  // RTC Council, Spatial Lab and Operator Mode are accessible on-demand.
  const [mode, setMode] = useState<ViewMode>("everyday");

  if (mode === "rtc_council") {
    return <RTCCouncilIdentities onBackToEveryday={() => setMode("everyday")} />;
  }

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
      onOpenRtcCouncil={() => setMode("rtc_council")}
    />
  );
}
