# Quickstart: Transport MVP

## Purpose

This quickstart describes how to use the Transport MVP spec as the source of
truth when turning the pilot requirements into downstream implementation work.

## Read in this order

1. `spec.md` — user-facing requirements and success criteria
2. `plan.md` — design scope, structure, and constitutional gates
3. `research.md` — key decisions and rejected alternatives
4. `data-model.md` — core entities and relationships
5. `contracts/pilot-channel-contract.md` — operator-visible behavior contract

## Use this spec to prepare implementation work

1. Confirm the implementation still targets `mentatzoe/cc-connect`.
2. Split downstream implementation work by ownership:
   - Vigil / Codex: `!stop` / `!resume`, open-floor mode
   - Dalgos / Claude: emoji reacts, approval-via-react
   - Dalgos / Claude second pass: pinned-rules ingestion
3. Generate `tasks.md` from this feature directory so every slice has explicit
   acceptance criteria and expected touched files before coding starts.
4. After `tasks.md` exists, sync tasks into GitHub issues for durable tracking.

## Pilot readiness checks

Before declaring the MVP ready for pilot use:

1. Open-floor mode works only in the designated pilot channel.
2. `!stop` halts outbound activity until explicit `!resume`.
3. Approval-gated actions remain blocked until the configured human approval
   reaction is observed.
4. Pinned channel rules are available in new session context.
5. Full coordination heuristics remain documented in spec/policy artifacts
   rather than hard-coded wholesale into transport logic.
