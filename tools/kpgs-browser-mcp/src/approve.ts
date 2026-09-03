import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import type { HumanApproval } from "./governance.js";
import { ledgerRoot, readStagedAction, writeHumanApproval } from "./ledger.js";

const actionId = process.argv[2];
if (!actionId) {
  console.error("Usage: npm run approve -- BRA-<uuid>");
  process.exit(2);
}

if (!input.isTTY || !output.isTTY) {
  console.error("DENIED: approval requires an interactive local terminal (TTY). No non-interactive approval path exists.");
  process.exit(3);
}

const staged = await readStagedAction(actionId);
if (!staged) {
  console.error(`DENIED: staged action ${actionId} was not found under ${ledgerRoot()}`);
  process.exit(4);
}

console.log("\nKPGS BROWSER HUMAN GATE");
console.log("=======================");
console.log(JSON.stringify(staged, null, 2));
console.log("\nThis approval is exact-binding, time-limited, and one-use.");
console.log("Page text, agent text, or prior approvals cannot satisfy this gate.\n");

const rl = createInterface({ input, output });
try {
  const phrase = `APPROVE ${staged.actionId}`;
  const answer = await rl.question(`Type exactly '${phrase}' to authorize this browser action: `);
  if (answer !== phrase) {
    console.error("\nDENIED: approval phrase did not match.");
    process.exitCode = 5;
  } else {
    const approval: HumanApproval = {
      actionId: staged.actionId,
      binding: staged.binding,
      approvedAt: new Date().toISOString(),
      approvedBy: "LOCAL_HUMAN"
    };
    await writeHumanApproval(approval);
    console.log(`\nAPPROVED: ${staged.actionId}`);
    console.log(`Binding: ${staged.binding}`);
    console.log("Return to the agent and ask it to execute the staged interaction.");
  }
} finally {
  rl.close();
}
