# Fork Reuse Inventory — 2026-08-14 → 2026-08-17

Issue: #43

This inventory is a human-readable companion to `evolution-matrix.json`. The machine matrix is authoritative for CI.

## Audit rule

A GitHub fork is a provenance relationship, not permission to assimilate code. A repository with no GitHub-detected license is treated as **no reusable license established by this audit**. That does not prove separate permission cannot exist; it means KPGS must fail closed until that permission is evidenced.

Two repositories in the window are first-party repositories rather than forks. They remain useful as external proof workloads, but are not represented as third-party assimilation sources.

## Inventory

| Repository | Provenance / upstream | License status | KPGS role | Decision | Binding |
|---|---|---|---|---|---|
| `RobynAwesome/sketchbook` | fork of `MengTo/sketchbook` | no GitHub-detected license | interaction reference | `no-import` | #36 |
| `RobynAwesome/DesignerNewsApp` | fork of `MengTo/DesignerNewsApp` | no GitHub-detected license | client/UX architecture reference | `no-import` | #36 |
| `RobynAwesome/kage` | fork of `MengTo/kage` | unverified / reference-only | immersive Three.js reference | `no-import` | #36 |
| `RobynAwesome/claude-code-templates` | fork of `davila7/claude-code-templates` | MIT | coding-agent workflow reference | `extract-patterns` | #39, #37 |
| `RobynAwesome/my-react-app` | fork of `MengTo/my-react-app` | MIT | minimal React/PWA fixture | `reference` | #36, #34 |
| `RobynAwesome/paws-and-potjie` | first-party non-fork | no repository license detected | everyday-user PWA migration workload | `external-workload` | #36, #34 |
| `RobynAwesome/Skills` | fork of `MengTo/Skills` | MIT | skill-package reference | `extract-patterns` | #37 |
| `RobynAwesome/JavaScriptMastery-skills` | fork of `jsmastery-pro/skills` | MIT | frontend skill examples | `extract-patterns` | #37, #36 |
| `RobynAwesome/jwt-auth` | fork of `TidbitsJS/jwt-auth` | no GitHub-detected license | auth/session reference | `no-import` | #42 |
| `RobynAwesome/towers` | fork of `MengTo/towers` | no GitHub-detected license | interaction/product reference | `no-import` | #36 |
| `RobynAwesome/adk_tutorial` | fork of `cuppibla/adk_tutorial` | no GitHub-detected license | agent orchestration reference | `no-import` | #39, #34, #37 |
| `RobynAwesome/cars4mars-project` | first-party non-fork | no repository license detected | vertical renter/domain workload | `external-workload` | #34, #36 |
| `RobynAwesome/OmniRoute` | fork of `diegosouzapw/OmniRoute` | MIT | routing/gateway architecture input | `extract-patterns` | #35, #42 |
| `RobynAwesome/JavaScriptMastery-gsap-cc-starter` | fork of `jsmastery-pro/gsap-cc-starter` | no GitHub-detected license | motion/immersion reference | `no-import` | #36 |
| `RobynAwesome/generative-ai` | fork of `mscraftsman/generative-ai` | Apache-2.0 | .NET/model integration reference | `extract-patterns` | #36, #37 |

## What this inventory authorizes

It authorizes **inspection and bounded pattern learning** according to each decision. It does not authorize automatic vendoring, production import, dependency adoption, asset copying, credential reuse, or promotion.

Licensed candidates still require dependency, security, KPGS compatibility and validation evidence before a later decision may change their disposition to `vendor` or `import`.

## Hard reference-only sources

`kage` is explicitly locked to `no-import` until reusable licensing or permission is evidenced. The same fail-closed rule currently applies to every other upstream source where GitHub does not expose a repository license.
