# KPGS Repository Provenance and License Policy

Status: **PROPOSED GOVERNANCE POLICY**  
Issue: #47  
Repository: `RobynAwesome/Introduction-to-MCP`

## 1. Current legal state

The repository currently has no root `LICENSE` file and no canonical repository-wide SPDX identifier. KPGS therefore treats the repository license state as **undecided** until the human repository owner explicitly chooses a license model.

The machine-readable source of this status is:

`governance/kpgs-vnext/licensing/license-decision.json`

A recommendation is not authorization. No agent, model, renter, CI process or maintainer automation may convert `RECOMMENDED_NOT_AUTHORIZED` into a repository license.

## 2. Human decision boundary

The repository owner must explicitly choose one of the supported policy states before repository-authored material can inherit a canonical repository license:

- `MIT`
- `Apache-2.0`
- `PROPRIETARY`
- `UNLICENSED`
- `PATH_SPECIFIC`

If `PATH_SPECIFIC` is chosen, each governed path must expose its own license evidence and SPDX/proprietary state. A path-specific license may not silently overwrite an upstream third-party license.

## 3. Contribution provenance

Every adapted, imported, vendored, copied, generated or fork-derived artifact admitted into canonical KPGS surfaces must preserve:

- origin repository or source reference;
- exact upstream commit/tag/version when available;
- relationship: `reference | inspiration | adaptation | import | vendor | generated`;
- upstream license/SPDX or explicit `unknown`;
- attribution/NOTICE requirements;
- local human reviewer;
- compatibility decision and evidence reference;
- modifications made locally;
- security review state where executable code is involved.

Unknown provenance is a promotion blocker, not permission to infer a license.

## 4. Import / compatibility law

### Reference-only

Material may be studied as `reference` when no code/assets are imported. Reference status does not grant permission to copy unlicensed or incompatible material.

### Adaptation / import / vendor

Before canonical admission:

1. upstream source must be identified;
2. upstream license must be known or explicit permission must exist;
3. required attribution/NOTICE must be preserved;
4. target path license must be known;
5. compatibility must be evaluated against the target path;
6. executable material must pass security and governance review;
7. the resulting manifest must retain source lineage.

While this repository's root license decision remains pending, KPGS must not claim deterministic repository-wide compatibility for new adapted/imported code. Such artifacts remain `pending`, `reference`, or separately licensed by path.

## 5. Existing third-party material

A later repository license declaration applies only where the repository owner has the legal authority to license the material.

It must not:

- overwrite an existing third-party license;
- remove copyright notices;
- remove required attribution;
- convert noncommercial/research-only material into commercial material;
- convert unlicensed reference material into reusable code;
- imply ownership of upstream work.

## 6. NOTICE / attribution

Where an upstream license or permission requires attribution, preserve it in the nearest appropriate source file and/or `THIRD_PARTY_NOTICES.md`.

The notice record should include:

- component/artifact name;
- upstream owner/project;
- source URL/reference;
- version/commit;
- upstream license;
- required notice text or attribution reference;
- local path(s) consuming the material.

KPGS provenance manifests remain required even when the upstream license does not mandate a NOTICE file.

## 7. Generated code and assets

Generated material must record, when applicable:

- generating tool/provider;
- human reviewer;
- prompt/specification or governing task reference;
- source inputs/assets used;
- known third-party dependencies or source lineage;
- rights/license status for incorporated source material;
- evidence that the generated artifact does not merely reproduce restricted material.

Generation does not erase copyright, license, privacy or attribution constraints inherited from its inputs.

## 8. KPGS skill promotion gate

A skill manifest may move to `license_status: verified-compatible` only when all of the following are true:

1. its origin/source lineage is explicit;
2. the relevant source and target license states are known;
3. compatibility has been evaluated;
4. required attribution/NOTICE is present;
5. no conflicting upstream restriction is hidden;
6. the repository/path license decision is human-authorized where required.

If any element is unknown, the skill remains `pending` or `unknown` and cannot be promoted to `validated` / `approved` solely on functional CI success.

## 9. Recommendation currently on record

`MIT` is recorded as the current **recommendation**, based on existing MIT-licensed skill packaging already present elsewhere in the governed ecosystem. This is evidence of an ecosystem pattern, not a license grant for this repository.

Canonical license state remains `AWAITING_HUMAN_DECISION` until the owner explicitly authorizes a policy.
