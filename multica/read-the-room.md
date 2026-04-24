# Read-the-Room Protocol

**Status**: active reference for shared Multica threads  
**Version**: 1.0 (2026-04-24)

Use this protocol after reading [`multica/rules.md`](rules.md) and before any
substantive Multica reply. The goal is to reduce duplicate comments and preserve
human-legible coordination without hiding behind silent heuristics.

## Labels

- **`SPEAK`**: post a substantive reply.
- **`ASK`**: ask one blocking clarifying question before substantive work.
- **`ACK`**: send one short presence signal because someone is visibly blocked on
  your acknowledgment.
- **`PASS`**: do not post.

`PASS` is a successful outcome. The harness triggering a run does not, by
itself, create a need to speak.

## Step 1 — Fast Visible-State Sync

Refresh the current issue state from visible Multica surfaces before grounding
deeply:

1. `multica issue get <id> --output json`
2. `multica issue comment list <id> --output json`

Use only visible state for gating decisions. `multica issue runs` and local run
logs may help with telemetry, but they MUST NOT decide whether a reply is
allowed.

Determine whether you are actually addressed:

- formal agent mention: `mention://agent/<self-id>`
- current assignee match: `issue.assignee_id == self.agent_id`

Plain-text references to your name do not count as direct addressing.

## Step 2 — PASS Suppressors First

If any suppressor fires, stop and `PASS` before deeper analysis:

- **Self-caused**: your own prior action triggered the run.
- **Stale**: the issue moved on, was closed, or the visible thread state no
  longer matches the triggering ask.
- **Duplicate**: a prior self-comment on this issue would already answer the
  current trigger as written.
- **Covered**: a peer comment posted after the triggering ask already answers
  it materially.

If coverage is partial, narrow the planned reply to only the uncovered part; do
not treat partial coverage as full `PASS`.

## Step 3 — Classify the Reply Mode

If no suppressor fired:

- **`SPEAK`**: you are explicitly addressed and have net-new value, or you need
  to correct a substantive technical error with evidence. One correction, then
  stop.
- **`ASK`**: you are explicitly addressed, the request is ambiguous, and one
  clarifying answer is required before useful work can continue.
- **`ACK`**: you are explicitly addressed and the asker is visibly blocked on a
  short acknowledgment.
- **`PASS`**: you are not explicitly addressed, or you add no material value.

Do not broaden the exception beyond canon in `multica/rules.md`. A
meaningfully different preference alone is not enough to interrupt.

## Step 4 — Grounding Scope Matches the Mode

- **`ACK`**: no deep grounding.
- **`ASK`**: read only the minimum material likely to answer the ambiguity. If
  grounding resolves it, re-run Step 3.
- **`SPEAK`**: do the full project grounding required by the repo and issue.

The cost-saving rule is simple: do not pay full grounding cost for cheap modes.

## Step 5 — Pre-Post Drift Gate

Immediately before `multica issue comment add`, refresh the thread again. If
material drift occurred while drafting, discard the draft and re-enter Step 1.

Retraction or rescoping only counts when authored by one of:

- the original asker
- the current issue assignee
- the operator

Peer-authored "resolved now" comments do not retract a request by themselves.

## Step 6 — Delivery Rules

- Substantive synthesis, design positions, review findings, and routing
  recommendations follow the both-mirror rule from `multica/rules.md`.
- Tactical coordination ("picking this up", "blocked on X", "handing off to Y")
  may stay Multica-only.
- Before any `gh` write or `git push`, mint the agent-scoped GitHub App token
  described in `multica/rules.md`.

## Step 7 — Telemetry Is Still an Open Dependency

The intended durable fix for `PASS` tracking is a platform primitive such as
`multica issue abstain --reason`. Until then, local run logs are best-effort
telemetry only and must not become hidden gating state.
