# Hallucination Solutions Library

## Role-Mapping Hallucination

- **Fix owner:** AI + Lead
- **Prevention:** check the current control note or image before restating roster truth
- **Known solution:** update the canonical roster notes immediately and log the incident

## Phantom Completion

- **Fix owner:** AI + Lead
- **Prevention:** verify file existence and contents before accepting completion
- **Known solution:** require evidence-first completion review and move the dev to stricter supervision if repeated

## Fabricated Technical Detail

- **Fix owner:** AI
- **Prevention:** state uncertainty early and inspect the repo before claiming specifics
- **Known solution:** replace memory claims with direct evidence and log the false detail

## Control-State Hallucination

- **Fix owner:** Lead
- **Prevention:** re-check `git status`, active diffs, and comms before planning or delegating
- **Known solution:** refresh the control notes and reduce further assignment until the state is corrected

## Optimism-Bias Drift

- **Fix owner:** Lead
- **Prevention:** act on repeated failure signals instead of hoping the next pass will self-correct
- **Known solution:** narrow scope, raise verification standards, or demote the failing lane
