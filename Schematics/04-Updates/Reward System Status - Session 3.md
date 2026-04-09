# Reward System Status - Session 3

> [!important]
> Historical Session 3 reward audit.
> Use [Now](../00-Home/Now.md) and [Open Issues](../06-Reference/Open%20Issues.md) for current live blockers. Keep this note as the reward-specific audit snapshot and QA backlog.

Status: `AMBER`

## Confirmed

- rewards page exists
- rewards API exists
- reward and referral fields exist on the user model
- referral API exists with `GET` and `POST`
- 5-level referral propagation logic exists in code

## Still Not Fully Verified

- referral flow end-to-end
- persisted referral points
- placeholder achievements
- perk redemption truth
- manager/admin reward oversight
- birthday reward points behavior
- manager dashboard wording versus live rewards implementation

## Next Current Follow-Through

- run end-to-end reward QA once valid auth and data access are available
- verify manager and admin reward visibility plus wording against live behavior
- replace placeholders with real tracked signals or explicitly defer them
