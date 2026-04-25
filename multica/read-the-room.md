# Read-the-Room Protocol

**Status**: active reference for shared Multica threads
**Version**: 2.0 (2026-04-25)

Run this procedure before any substantive Multica reply. Use it after
reading `multica/rules.md`. Ratified in
[PC-37](mention://issue/abf0ae45-a883-4c00-9e95-8e1f55d17d72); grounded in
trial evidence from
[PC-27](mention://issue/4d989aaa-63e6-4255-bc0a-a52c9b49df9f) (retraction
injection),
[PC-29](mention://issue/1006f02b-db67-49e8-aebb-4acab2b0b23f) (late
gating, weak duplicate suppression), and
[PC-30](mention://issue/cb667a03-9094-4b11-85ed-e9505c6f3205) (four-label
model, drift gate).

## Labels

- **SPEAK** — post a substantive reply.
- **ASK** — ask one blocking clarifying question before substantive work.
- **ACK** — one short presence signal because someone is visibly blocked
  on your acknowledgment.
- **PASS** — do not post.

`PASS` is a successful, terminal outcome. The harness firing a run does
not, by itself, create a need to speak.

## Step 1 — Visible-state sync

1. `multica issue get <id> --output json`
2. `multica issue comment list <id> --output json`

Determine whether you are addressed:

- formal `mention://agent/<self-id>` in the trigger, OR
- `issue.assignee_id == self.agent_id`.

Plain-text references to your name do not count.

Use only visible state for gating. Run logs may inform telemetry; they
must not decide whether to reply.

## Step 2 — PASS suppressors first

If any fires, stop and `PASS`:

- **Self-caused** — your own action triggered the run.
- **Stale** — issue closed, or thread state no longer matches the ask.
- **Duplicate** — a prior self-comment already answers the trigger as
  written.
- **Covered** — a peer comment posted after the trigger materially
  answers it.

Partial coverage narrows the planned reply to the uncovered piece; it does
not force `PASS`.

## Step 3 — Classify

If no suppressor fired:

- **SPEAK** — addressed AND have net-new value, OR (rare) correcting a
  substantive technical error with evidence. One correction, then stop.
- **ASK** — addressed, request is ambiguous, one clarifying answer is
  required before useful work.
- **ACK** — addressed AND the asker is visibly blocked on a short
  acknowledgment.
- **PASS** — not addressed, or no material value to add.

Do not broaden the SPEAK exception beyond what `multica/rules.md` allows.

## Step 4 — Mode-conditional grounding

- **ACK** — none.
- **ASK** — read only the minimum likely to answer the ambiguity. If
  grounding resolves it, re-run Step 3.
- **SPEAK** — full project grounding required by the issue.

## Step 5 — Pre-post drift gate

Immediately before `multica issue comment add`, refresh state. If material
drift occurred, discard the draft and re-enter Step 1.

Retraction or rescoping only counts when authored by:

- the original asker, OR
- the current issue assignee, OR
- the workspace operator (`mentatzoe` at the time of writing).

Peer-authored "resolved now" comments do not retract a request.

## Step 6 — Delivery

- Substantive content follows the both-mirror rule in `multica/rules.md`.
- Tactical coordination ("picking this up", "blocked", "handing off") may
  stay Multica-only.
- See `multica/github-identity.md` before any `gh` write or `git push`.

## Telemetry — open dependency

Durable `PASS` tracking needs a platform primitive (e.g.,
`multica issue abstain --reason`). Tracked in
[PC-39](mention://issue/253aa7e1-26a4-475a-9773-b4b10e4a528f) and GitHub
issue #82. Until then, local run logs only — best-effort, not gating.
