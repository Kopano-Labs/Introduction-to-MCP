# Fork Assimilation Decision

Issue: #43

Decision date: 2026-08-17

## Decision

The Aug 14–17 learning window is accepted as a **governed reference estate**, not a code-import queue.

Canonical assimilation remains denied by default. Each source must independently cross provenance, licensing, dependency/security, KPGS compatibility and validation gates before a later decision can authorize `vendor` or `import`.

Current dispositions:

- **`no-import`** — `sketchbook`, `DesignerNewsApp`, `kage`, `jwt-auth`, `towers`, `adk_tutorial`, `JavaScriptMastery-gsap-cc-starter`. Their upstream lineage is known, but this audit did not establish a reusable repository license. Concepts may inform independent implementation; source/assets may not cross the canonical boundary.
- **`extract-patterns`** — `claude-code-templates` (MIT), `Skills` (MIT), `JavaScriptMastery-skills` (MIT), `OmniRoute` (MIT), `generative-ai` (Apache-2.0). Licensing establishes candidates, not production approval. Prefer interfaces, protocols and independently implemented KPGS contracts over bulk source import.
- **`reference`** — `my-react-app` (MIT). Keep it as a small conformance/test-fixture candidate until dependency review completes.
- **`external-workload`** — `paws-and-potjie` and `cars4mars-project`. GitHub identifies both as first-party non-forks. Use them to prove KPGS integration from outside the canonical runtime; do not assimilate their domain code merely to make tests pass.

## Explicit kage gate

`RobynAwesome/kage` remains **reference-only / no-import**. Its parent is `MengTo/kage`, but GitHub exposes no repository license for the fork/upstream metadata inspected by this gate. No code, assets, shaders, textures or other source material may be copied into `Introduction-to-MCP` unless explicit reusable licensing or permission is subsequently recorded and reviewed.

## Mapping into KPGS work

- UX/PWA references map to the canonical adapter boundary in #36 rather than forcing frontend rewrites.
- Agent workflow references map to the specification-first loop in #39 and skill runtime in #37.
- Auth/session references map to #42 and remain fail-closed until both licensing and security review permit more than conceptual reference.
- Stateless workload candidates map to #34 and #36.
- Routing/gateway concepts from OmniRoute map to #35/#42; the repository's large and fast-moving dependency surface requires a dedicated review before code reuse.
- `.NET` model integration concepts from `generative-ai` map to #36/#37 under Apache-2.0 provenance, with model/data/dependency review still required.

## Promotion rule

A later change from `reference`, `extract-patterns`, or `no-import` to `vendor`/`import` MUST attach:

1. exact upstream repository + revision;
2. license/SPDX and attribution obligations;
3. dependency/security review evidence;
4. exact reusable path(s) or component(s);
5. destination KPGS issue/protocol/skill;
6. compatibility validation evidence;
7. provenance metadata retained with the imported material.

Absent any one of those, CI must reject the assimilation decision.
