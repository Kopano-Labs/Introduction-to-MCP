# Fork Assimilation Workflow

Issue: #43

## Purpose

This workflow governs how a reference repository can influence KPGS without silently becoming canonical code.

```text
discover -> witness -> classify -> map -> review -> decide -> validate -> assimilate-or-reference -> monitor
```

## 1. Discover / witness

Record:

- local `owner/repo`;
- whether GitHub identifies it as a fork;
- exact parent/source `owner/repo` for forks;
- default branch or explicit inspected ref;
- repository license/SPDX exposed by the authoritative source;
- observation date and source.

If any fork lacks an upstream parent/source, stop. Do not infer lineage from naming similarity.

## 2. Classify

Choose one repository kind:

- `fork`
- `first_party_non_fork`

Choose one current disposition:

- `reference` — inspect and compare only;
- `rewrite` — independently implement the useful contract/pattern;
- `extract-patterns` — document interfaces/ideas while preserving source provenance;
- `external-workload` — exercise KPGS against the repository without copying its domain code;
- `no-import` — explicit fail-closed boundary;
- `vendor` / `import` — allowed only after every promotion gate is complete.

## 3. Map before reuse

Every source must map to at least one KPGS issue, protocol or skill. Record reusable material narrowly; avoid whole-repository descriptions such as “use everything.”

For copied/derived content, provenance must remain attached at file/package/component level, not only in this inventory.

## 4. License gate

A GitHub fork relationship is not a license.

- MIT / Apache-2.0 or another explicitly reviewed license may establish a **candidate**.
- No GitHub-detected license means KPGS has not established reusable permission through this audit.
- Unknown/unverified licensing cannot authorize `vendor` or `import`.
- First-party ownership/provenance may support internal workload use, but this workflow does not make legal conclusions about third-party material or dependencies contained inside that repository.

## 5. Security and dependency gate

Before `vendor` or `import`, record both reviews as `complete` and attach evidence in the governing PR/issue.

Review at minimum:

- transitive dependencies and lockfiles;
- known vulnerabilities/advisories where relevant;
- install/build scripts and lifecycle hooks;
- credential/network/filesystem behavior;
- generated or vendored artifacts;
- runtime privileges;
- tenant/data boundary implications;
- compatibility with the target KPGS protocol and capability lease.

Security-sensitive references such as auth, routing/gateway and model clients require dedicated review even when the repository license is compatible.

## 6. Upstream sync rule

A fork used as a living reference may be synchronized with upstream, but synchronization itself never updates the canonical KPGS implementation.

For every sync that could affect a KPGS decision:

1. witness the new upstream ref/revision;
2. compare the relevant paths/behavior;
3. re-evaluate license/provenance if upstream ownership or licensing changed;
4. re-run dependency/security review when relevant dependencies or privileged behavior changed;
5. update the matrix inspection ref/notes;
6. attach new validation evidence before changing disposition.

Do not automatically merge upstream into `Introduction-to-MCP`.

## 7. Promotion to vendor/import

A promotion PR must include:

- exact upstream and revision;
- license/SPDX + required attribution/notice handling;
- exact source paths/components proposed for reuse;
- destination path and KPGS binding;
- dependency review evidence;
- security review evidence;
- compatibility/conformance tests;
- validation owner and `approved_for_assimilation` status;
- rollback/removal plan.

The matrix validator fails closed when these prerequisite statuses are absent.

## 8. Reference/rewrite path

When licensing is missing or direct reuse is undesirable, KPGS may learn the problem/behavior and implement its own contract independently. The record must distinguish:

- upstream concept observed;
- independently implemented KPGS behavior;
- validation proving the KPGS behavior;
- no copied source/assets claim where that is the chosen boundary.

## 9. CI

Run:

```bash
python scripts/ci/validate_fork_assimilation.py
python -m pytest -q tests/test_fork_assimilation_gate.py
```

Repository CI runs the pytest gate on supported Python versions. Any change that removes provenance, widens an unlicensed source to import/vendor, removes KPGS mapping, or attempts import without completed security/dependency/validation state must fail.
