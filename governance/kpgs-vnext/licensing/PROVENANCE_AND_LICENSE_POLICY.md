# KPGS Repository Provenance and License Policy

Status: **ACTIVE — HUMAN APPROVED**  
Issue: #47  
Repository: `RobynAwesome/Introduction-to-MCP`  
Canonical SPDX: `Apache-2.0`

## 1. Current legal state

The repository owner has explicitly authorized **Apache License 2.0** as the canonical repository license for repository-authored material for which the owner has legal authority to license.

The root `LICENSE` file contains the Apache License 2.0 text. The machine-readable source of the decision is:

`governance/kpgs-vnext/licensing/license-decision.json`

The repository-wide declaration does **not** overwrite third-party, vendored, imported, fork-derived, path-specific or otherwise separately licensed material.

## 2. Human decision boundary

The human-owner decision recorded under issue #47 is now `HUMAN_APPROVED` with canonical SPDX `Apache-2.0`.

Any future change to the canonical legal model remains a human decision. No agent, model, renter, CI process or maintainer automation may silently change the repository license or infer authority over material whose rights are not established.

Supported future decision states remain:

- `MIT`
- `Apache-2.0`
- `PROPRIETARY`
- `UNLICENSED`
- `PATH_SPECIFIC`

If `PATH_SPECIFIC` is used for any governed path, that path must expose its own license evidence and SPDX/proprietary state. A path-specific declaration may not silently overwrite an upstream third-party license.

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
5. compatibility must be evaluated against Apache-2.0 or the explicitly governed target-path license;
6. executable material must pass security and governance review;
7. the resulting manifest must retain source lineage.

A root Apache-2.0 declaration is not evidence that an imported artifact is Apache-2.0-compatible. Compatibility is evaluated per artifact/path from actual upstream rights and obligations.

## 5. Existing third-party material

The repository-wide Apache-2.0 declaration applies only where the repository owner has the legal authority to license the material.

It must not:

- overwrite an existing third-party license;
- remove copyright notices;
- remove required attribution;
- convert noncommercial/research-only material into commercial material;
- convert unlicensed reference material into reusable code;
- imply ownership of upstream work.

Where a repository path contains material under another valid license, that material remains governed by its own terms unless the rights holder explicitly authorizes relicensing.

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

Apache-2.0 does not require creation of a repository `NOTICE` file merely because Apache-2.0 is selected. If this Work later includes a `NOTICE` file, Apache-2.0 redistribution requirements for that NOTICE apply. KPGS provenance manifests remain required even where an upstream license does not mandate a NOTICE file.

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
3. compatibility with Apache-2.0 or the governed target-path license has been evaluated;
4. required attribution/NOTICE is present;
5. no conflicting upstream restriction is hidden;
6. the repository/path license decision is human-authorized where required.

If any element is unknown, the skill remains `pending` or `unknown` and cannot be promoted to `validated` / `approved` solely on functional CI success.

## 9. Canonical decision

The prior MIT entry was a `RECOMMENDED_NOT_AUTHORIZED` ecosystem recommendation only. It never licensed this repository and is retained as historical evidence in `license-decision.json`.

The human owner has now selected **Apache-2.0**. This decision is canonical for repository-authored material within the owner's licensing authority because it preserves permissive reuse while adding an explicit contributor patent grant and clearer contribution/redistribution terms appropriate to long-lived KPGS protocols, runtimes, SDKs and multi-contributor infrastructure.

Canonical license state: `HUMAN_APPROVED / Apache-2.0`.
