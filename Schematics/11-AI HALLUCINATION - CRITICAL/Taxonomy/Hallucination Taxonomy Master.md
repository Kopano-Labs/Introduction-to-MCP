# Hallucination Taxonomy Master

## Severity Scale

- `CRITICAL` - changes execution, repo safety, or trust boundaries materially
- `MID` - distorts governance, planning, or note truth in a meaningful but recoverable way
- `LOW` - small wording or state drift with low downstream consequence

## Domain Scale

- software
- hardware
- process
- hierarchy/control
- memory/context
- role-mapping
- research/factual

## Fix Ownership Scale

- AI-self-fixable
- lead-fixable
- developer-fixable
- system/platform-fixable
- owner-decision-fixable

## Active Types

### Role-Mapping Hallucination

- false statement about who holds which role
- current example: `DEV_4: Cicero` misapplied to `DEV_1`

### Phantom Completion

- work reported as completed when the output is missing, empty, or unverified

### Fabricated Technical Detail

- invented repo fact, configuration detail, or implementation state

### Control-State Hallucination

- false summary of current task, team state, or blocker order

### Optimism-Bias Drift

- continuing to trust a failing pattern despite enough evidence to stop

### Fallacy of Concept (MVP Ghosting)

- continuing to treat a retired, deprecated, or temporally-bound feature as active truth simply because its legacy code still persists in an MVP state
- example: hallucinating that a consumer arena app is a B2B platform, or treating a concluded World Cup tournament as live registration simply because the components were not fully purged

## Recurrence Rule

- if the same type appears twice, it must be flagged as a recurring pattern in the database
