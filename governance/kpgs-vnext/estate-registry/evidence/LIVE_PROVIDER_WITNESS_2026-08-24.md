# Live Provider Witness — 2026-08-24

Issue: #102  
Machine receipt: `live-provider-witness-2026-08-24.json`  
Authority effect: **witness-only**  
Provider mutation performed: **no**

`I_AM_STATELESS_RENTER_NOT_LANDLORD`

## Purpose

Admit facts that were directly witnessed through connected Vercel and GitHub account surfaces without inventing KPGS adapter, renter, capability, evaluation or production-promotion evidence.

This receipt intentionally separates:

```text
provider says a domain/deployment exists
!=
KPGS says the property is registration-complete
!=
KPGS staging/production promotion
```

Public HTTP reachability alone is not the ownership witness used here.

## Starfall Salvage

### Connected facts

- Domain binding: `starfallsalvage.kopanolabs.com` is attached to Vercel project `prj_rik2lQSlmHm7CIUhEGZMprZ5CFcN` (`starfall-salvage`) inside team `team_w8Z8foT3ccswOxMiB4LypZ59`.
- Current production deployment: `dpl_8Myns9BqgPovBtTaC1ZsrjtNwCuP`, state `READY`.
- Current source commit: `fea307d09a8552cec72e0a6bcb5440cd173bef41`.
- Connected GitHub resolves stable repository id `1229480004` as `RobynAwesome/starfall-salvage`; the exact current deployment commit exists there.
- Vercel deployment metadata still records the source organization as `Kopano-Labs/starfall-salvage`. Stable repository id + exact commit are therefore retained as the cross-provider identity seam instead of pretending the naming discrepancy does not exist.
- Prior READY production deployment `dpl_9X3gbZpWuRWK5N3XC7Unvtd1doDR` points to commit `b3253e44a7e129d5d2f323d579666f6e5182fd94` and is retained as the witnessed rollback target candidate.
- Connected Vercel runtime-error aggregation returned no error groups for the selected seven-day window.

### Starfall rollback procedure

This is a **rollback procedure reference**, not automatic rollback authority.

If a future KPGS-authorized production transition uses the current Starfall release and a rollback is required:

1. Confirm the currently live deployment/release fingerprint still matches the release being rolled back.
2. Re-check that `dpl_9X3gbZpWuRWK5N3XC7Unvtd1doDR` is still available as an eligible Vercel rollback candidate and corresponds to commit `b3253e44a7e129d5d2f323d579666f6e5182fd94`.
3. Obtain the separately governed `estate.release.rollback` authority / human approval required by the active policy.
4. Execute rollback only through an authorized provider surface; this repository receipt cannot perform that action by itself.
5. Verify the public release fingerprint and critical route/health behavior after rollback.
6. Emit the rollback evidence receipt and update canonical estate state through the governed registry transition.

Until steps 3–6 have actually occurred, a rollback drill or rollback success MUST NOT be claimed.

### Starfall admission verdict

`declared_pending_witness -> witnessed` is supported by connected provider/repository evidence.

Further lifecycle movement is **HOLD** because the versioned adapter, conformant Stateless Renter protocol, capability map, governed health/evidence endpoint, policy/risk/tier, exact-commit KPGS evaluation and rollback-drill receipts are not yet evidenced.

## KasiLink

### Connected facts

- Connected GitHub repository: `RobynAwesome/KasiLink`, stable repository id `1195618604`.
- Both current Vercel deployments resolve to exact source commit `1080fb18096cb2b5c9f8a9ea0d12b442b80329f4`.
- Apex `kasilink.com` is attached to Vercel project `prj_07Q4oRr2okeBiPO12YotAzHZM10b` (`kasi-link.rsa`) and current READY deployment `dpl_9PMFHyTv9jP78sASJaZD5hGX47yr`.
- `www.kasilink.com` is attached to Vercel project `prj_A1AvVl5WYRyTergoEcMsvEmMM3uX` (`kasi-link`) and current READY deployment `dpl_AA9iSMwcpHPGvqtRc5mEFjMpywha`.
- The source commit has converged, but the provider project identities and domain ownership remain split.
- Connected Vercel runtime aggregation currently reports MongoDB Atlas authentication failures on both project identities. The apex project has repeated failures for `/api/incidents`, `/api/water-alerts` and `/api/gigs`; the `www` project has a current `/api/gigs` authentication failure plus an older Clerk publishable-key middleware error in the sampled window.

### KasiLink cutover boundary

The current connected Vercel action surface can inspect projects, deployments, build/runtime evidence and deploy the current project, but exposes **no project-domain assignment/removal mutation operation**.

Therefore:

```text
provider split witnessed = YES
source commit convergence = YES
safe domain cutover executed = NO
canonical single-project release = NO
migration/promotion = HOLD
```

No manual DNS value is guessed. No public HTTP response is substituted for provider control evidence. The future cutover must remain reversible and must receipt both the old and new provider bindings before and after mutation.

### KasiLink admission verdict

`declared_pending_witness -> witnessed` is supported for the existing provider/repository state.

KasiLink remains **HOLD** for registration/migration because:

- no single canonical Vercel project owns both public hostnames;
- the connected provider surface cannot currently perform the required domain reassignment;
- runtime authentication errors remain observed;
- adapter/renter/capability/policy/evaluation/rollback evidence remains incomplete.

## Anti-FOC boundaries

- `witnessed` does not mean `registered`.
- READY Vercel deployment does not mean KPGS production promotion.
- same Git commit on two projects does not collapse two provider identities into one.
- a rollback candidate is not an executed rollback drill.
- runtime error absence for Starfall is an observation for a bounded time window, not a permanent health guarantee.
- runtime errors for KasiLink are provider/runtime evidence; this receipt does not guess credentials or mutate secrets.
- no provider mutation was performed by this evidence-admission slice.
