# Hallucination Database Master

| Date / Time | Title | Type | Severity | Ownership | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| [2026-04-10 0146](../Incidents/2026-04-10%200146%20-%20DEV%20Role%20Mapping%20Hallucination%20From%20Cicero%20To%20Germini.md) | DEV role mapping hallucination from `Cicero` to `Germini` | role-mapping | MID | AI-self-fixable + lead-fixable | logged, corrected in control notes | screenshot + current control notes |
| historical | DEV_2 phantom completion reports | phantom completion | CRITICAL | lead-fixable + AI-self-fixable | backfilled from training notes | [Dev2 Behavioral Analysis](../../05-Training/Dev2%20Behavioral%20Analysis.md) |
| historical | DEV_2 fabricated technical details | fabricated technical detail | MID | AI-self-fixable | backfilled from training notes | [Dev2 Behavioral Analysis](../../05-Training/Dev2%20Behavioral%20Analysis.md) |
| historical | chain-of-command gap forced Owner-to-DEV contact | control-state / hierarchy | CRITICAL | lead-fixable | backfilled from training notes | [Dev2 Behavioral Analysis](../../05-Training/Dev2%20Behavioral%20Analysis.md) |
| historical | optimism bias after repeated failure signals | optimism-bias drift | MID | lead-fixable | backfilled from training notes | [Lead Self Report](../../05-Training/Lead%20Self%20Report.md) |
| [2026-04-11](../Incidents/2026-04-11%200057%20-%20Capability%20Hallucination%20Edge%20Browser%20From%20Claude.md) | Optimism-bias drift — Edge browser read-only tier, 8 rounds of failed attempts | optimism-bias drift | MID | AI-self-fixable | logged | session transcript |
| [2026-04-11](../Incidents/2026-04-11%200057%20-%20Assumed%20Instruction%20Hallucination%20From%20Claude.md) | Assumed instruction execution without verification | assumed-instruction | HIGH | AI-self-fixable | logged | session transcript |
| [2026-04-11](../Incidents/2026-04-11%201112%20-%20Legacy%20Name%20Slip%20Orch%20vs%20KC%20From%20Claude.md) | Legacy name slip — used "Orch" instead of "Kopano Context" | naming-violation | LOW | AI-self-fixable | logged | session transcript |
| [2026-04-11 Portfolio Session](../Incidents/2026-04-11%20-%20Multi-Hallucination%20Session%20From%20Claude%20Portfolio%20Audit.md) | Spawned 2 Explore agents for 5-file read task — 10% token waste | lazy-agent-spawn | HIGH | AI-self-fixable | logged | session transcript + token metrics |
| [2026-04-11 Portfolio Session](../Incidents/2026-04-11%20-%20Multi-Hallucination%20Session%20From%20Claude%20Portfolio%20Audit.md) | Claimed Canva connector unavailable without checking — tool was connected | capability-hallucination | HIGH | AI-self-fixable | logged | Master screenshot proof |
| [2026-04-11 Portfolio Session](../Incidents/2026-04-11%20-%20Multi-Hallucination%20Session%20From%20Claude%20Portfolio%20Audit.md) | Gave false remediation advice based on false Canva premise | cascading-hallucination | MID | AI-self-fixable | logged | session transcript |
