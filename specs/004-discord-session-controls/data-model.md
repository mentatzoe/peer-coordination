# Data Model: Discord Session Controls

## Entities

### Bound Discord Surface

- `guild_id` (existing optional Discord scope hint)
- `channel_id` (new explicit Phase 1 bound channel)
- optional thread-parent relationship when `thread_isolation = true`

Represents the only Discord surface allowed to participate in the Phase 1
runtime for this bot instance.

### Runtime Session Gate

- bound surface key
- state: `closed` or `open`
- last control action: `operator_seed`, `resume`, `stop`

Represents whether the runtime is currently willing to dispatch inbound peer
messages for the bound surface.

### Session Control Command

- literal command text (`!stop`, `!resume`)
- issuer identity
- timestamp

Represents an operator-issued control action interpreted by the Discord
transport before normal agent dispatch.

## Relationships

- One **Bound Discord Surface** has one **Runtime Session Gate**.
- **Session Control Commands** mutate the **Runtime Session Gate**.
- The **Runtime Session Gate** controls whether inbound Discord messages are
  dispatched into the current `core.SessionManager` session or rejected.

## Notes

- The downstream `specs/001-session-bundle-skeleton/spec.md` contract expects
  later artifacts to preserve `channel_id`; this slice only ensures that the
  runtime channel identifier is stable and recoverable.
- No new governance-layer entities are introduced here.
