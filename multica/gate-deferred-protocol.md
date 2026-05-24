# Gate-Deferred Request Capture Protocol

**Status**: active reference for accountability-gated surfaces
**Version**: 1.0 (2026-05-24)
**Owns**: [PC-87](https://github.com/mentatzoe/peer-coordination/issues/) — Multica issue
in the `Gate-Deferred Requests` project.

When an accountability gate rejects or defers a user request, the
rejecting agent must convert the request into a durable, owned
follow-through object before ending the turn. The gate stays in force.
Capture is the alternative to oblivion, not the alternative to the gate.

## Why

Zoe, 2026-05-24:

> Something is rejected by amber, and then it gets forgotten into
> oblivion, so I practically get punished for being compliant.

Concrete incident: a Vault Keeper status request was refused in amber
rather than captured for daylight completion. Zoe then had to re-ask.
Compliance must reduce load, not create more tracking burden.

## Invariant

When a gate (amber, red, scope, policy, capacity) blocks a request, one
of the following must be true before the turn ends:

1. A capture object (Multica issue or comparable) exists with the fields
   in the next section, assigned to an owner that is not the user, OR
2. The reply explicitly states that no capture is being made and why
   (e.g. "you said drop it", "trivially re-askable, no resume value").

"Next turn will handle it" is not a capture. The next turn does not
exist unless something durable triggers it.

## Required capture fields

Every gate-deferred capture object carries these fields. Pin them as
issue description content (not metadata — these are load-bearing for the
owner reading the issue cold).

- **origin** — Discord channel + thread link, GitHub thread URL, or the
  Multica issue/comment URL that contained the original request.
- **requested_action** — the exact action the user asked for, copied or
  paraphrased tightly enough that the owner can recognize it.
- **blocking_gate** — which gate fired (amber/red/scope/policy/capacity)
  and a one-line reason. Do not editorialize beyond what the gate said.
- **resume_condition** — one of:
  - `allowed-later` — gate is time- or phase-bound; resume at the named
    trigger (daylight, end-of-amber, named time, named event).
  - `needs-gen` — user must explicitly `/gen` (or platform equivalent)
    before resume.
  - `needs-user-decision` — user must answer a specific question first;
    state the question.
  - `bypass-with-approval` — workspace operator can authorize early
    execution; name the operator.
- **owner** — Multica assignee (project/squad/agent/member). Never the
  user. If no clear owner exists, assign to the `Continuity Squad` and
  let triage route.
- **completion_proof** — what the owner posts back to **origin** when
  done. Default: a final status comment on the origin surface linking
  the resolved capture object.

## Issue template

When the capture object is a Multica issue (default), create with:

```
multica issue create \
  --title "[Gate-deferred] <short verb phrase of requested action>" \
  --project <Gate-Deferred Requests project id> \
  --assignee-id <owner id> \
  --priority <inherit from original or 'medium'> \
  --status todo \
  --description-stdin
```

Description body (paste-ready):

```markdown
## Origin
<URL or Discord channel#thread>

## Requested action
<exact ask>

## Blocking gate
<amber|red|scope|policy|capacity> — <one-line reason>

## Resume condition
<allowed-later | needs-gen | needs-user-decision | bypass-with-approval>
<one-line elaboration: the trigger, the question, or the approver>

## Owner
<project/squad/agent/member name>

## Completion proof
Final status comment back to origin linking this issue when resolved.

— captured by <agent name> from <origin> at <timestamp>
```

Use `--status todo` only if the resume condition is already satisfied
(e.g. capture during daylight). Otherwise `--status backlog` and let the
owner promote when the resume trigger fires.

## Continuity Squad operating protocol

The `Continuity Squad` is the default owner for gate-deferred captures
that lack a more specific owner. Squad leader is whichever agent picks
up the unassigned triage queue first; agnostic to specific agent.

- **Triage** — within one run of the capture appearing, leader either
  reassigns to a specific owner (project/agent/squad) or accepts squad
  ownership and decomposes into child issues per
  `## Parent / Sub-issue Protocol` in `CLAUDE.md`.
- **Delegate** — children get `--status todo` if startable now, else
  `--status backlog` with the resume trigger named in the description.
- **Verify** — leader reads the child's final status comment and
  confirms it matches `completion_proof` before flipping the parent to
  `done`.
- **Report back** — when the parent capture closes, leader posts a
  final comment on **origin** linking the resolved Multica issue. Zoe
  is not the memory store; the squad closes the loop.

## What this protocol does NOT do

- It does not weaken amber/red gate semantics. Blocked work stays
  blocked until the resume condition fires.
- It does not treat rejection as implicit `/gen` approval. A
  `needs-gen` capture sits in backlog until the user explicitly
  authorizes resume.
- It does not auto-run work during a blocked window. Captures are
  scheduling primitives, not execution primitives.
- It does not require the user to remember anything. The owner pulls;
  the user does not push.

## When to skip capture

Capture is the default. Skip only when:

- The user explicitly said to drop the request ("nevermind", "skip
  it").
- The request is a pure clarification with no work attached and the
  answer is already in the reply.
- The request is trivially re-askable with no state lost by deferring
  it to the next user-initiated turn (rare — bias toward capture).

In a skip case, state the skip reason in the reply so the user can
overrule.

## References

- PC-87 — origin issue and motivating incident.
- `multica/rules.md` — both-mirror rule, routing mechanics.
- `multica/read-the-room.md` — reply gating; capture is independent of
  read-the-room (a `PASS` on a thread can still produce a capture if
  you are the agent that ran the gate).
- `CLAUDE.md` — parent/sub-issue protocol, status semantics.
