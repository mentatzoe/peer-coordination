# Session Re-Entry Protocol

**Status**: active reference. Last updated 2026-04-19.  
**Audience**: any fresh-session agent or human collaborator resuming work in
this repository.

## Why this doc exists

Fresh sessions do not inherit prior chat context. In this repo, that means a
new session can easily miss the active slice, the current worktree owner, the
required Speckit artifact chain, or the repo-specific review workflow unless
those facts are written down and read in a stable order.

This document is the **canonical cross-agent entry point** for re-entry. It is
the place both Codex- and Claude-driven sessions must consult before starting
work.

If this protocol conflicts with `AGENTS.md` or `CLAUDE.md`, this protocol wins.

## Before any work

Every fresh session MUST read, in this order:

1. this file: `docs/ways-of-working/session-reentry.md`
2. [`README.md`](../../README.md)
3. [`ACTIVE-SLICES.md`](../../ACTIVE-SLICES.md)
4. the loader file for its client:
   - Codex: [`AGENTS.md`](../../AGENTS.md)
   - Claude: [`CLAUDE.md`](../../CLAUDE.md)
5. [`docs/ways-of-working/pull-requests.md`](./pull-requests.md)

Read these next when relevant:

- [`SESSION-HANDOFF.md`](../../SESSION-HANDOFF.md) if it exists and the active
  slice or operator has pointed at it
- [`docs/ways-of-working/github-discussions-replies.md`](./github-discussions-replies.md)
  before posting to GitHub Discussions
- the owned slice's artifact chain before changing that slice:
  - `spec.md`
  - `plan.md`
  - `tasks.md`
  - `analyze.md` if present
- the governing PR or discussion thread when one exists for the slice

## Canonical surfaces

Use the repo surfaces for the jobs they are meant to do:

- **`session-reentry.md`**: canonical re-entry protocol
- **`ACTIVE-SLICES.md`**: durable ownership and collision-avoidance registry
- **`SESSION-HANDOFF.md`**: short-lived pointer doc; useful, but not canonical
  for long-lived ownership state
- **GitHub Discussions / PRs**: optional peer-visibility and review surfaces,
  not the canonical re-entry mechanism

## Ownership and collision avoidance

Before proceeding with substantive work on a slice, the fresh session MUST:

1. confirm the intended slice in `ACTIVE-SLICES.md`
2. verify the owner, worktree, branch, and current phase
3. update the row if it is taking ownership, changing status, or refreshing a
   stale entry
4. emit the readiness declaration in-chat

An agent MUST NOT take over a slice already listed under another agent's
ownership without a handoff note recorded in one of:

- a commit updating `ACTIVE-SLICES.md`
- the slice PR
- the slice discussion thread when one exists

If ownership is unclear, stop and ask the operator rather than guessing.

If the `ACTIVE-SLICES.md` row looks stale, mark it
`stale-needs-confirmation`, refresh what you can from repo facts, and do not
assume the prior owner/worktree still reflects reality.

## Branch and worktree conventions

- Prefer `.worktrees/` for isolated workspaces.
- Record the **actual** worktree path and branch name in `ACTIVE-SLICES.md`.
- For new manually-created branch names, prefer
  `<agent>-<slice-id>-<short-name>` when practical.
- If Speckit has already created a slice branch (for example
  `007-session-bundle-init-cli`), do not rename it retroactively. Record the
  actual branch and proceed.

The registry is authoritative for current ownership. Naming conventions help,
but they do not replace the registry.

## Sanity one-liner (`READINESS`)

Before substantive work begins, the fresh session MUST emit a short readiness
statement in-chat using this format:

```text
READINESS — slice=<id>, owner=<agent>, worktree=<path>, branch=<name>, phase=<speckit-phase>, read=[<file1>, <file2>, ...], next=<step>
```

The declaration is meant to be:

- grep-able in chat logs
- easy for peer agents to parse
- easy for the operator to scan

The `READINESS` line is **mandatory**:

- on fresh-session starts, it should be the first substantive response after
  orientation
- on ambiguous orientation prompts, it should appear before any longer status
  explanation

The readiness declaration is **ephemeral**. The durable state belongs in
`ACTIVE-SLICES.md`.

## Ambiguous orientation prompts

Treat short prompts such as these as **re-entry cues**, not as permission to
skip re-entry:

- `status?`
- `what's active?`
- `where are we?`
- `what should I do next?`

For those prompts, the session should first orient through the required
re-entry surfaces, then answer with project / slice status grounded in those
artifacts. Emit the `READINESS` line first, then give any longer explanation.
Do not default to raw `git status` alone unless the prompt clearly asks for
repository cleanliness only.

For orientation / status answers, use this priority order:

1. current owned slice / patch train
2. off-limits slices and their recorded owners from `ACTIVE-SLICES.md`
3. next workflow step or current review surface
4. broader repo or git cleanliness details only after the above, or when
   explicitly requested

## Speckit gates

For Speckit-backed slices, follow the normal artifact flow:

`specify -> clarify -> plan -> tasks -> analyze -> implement`

Repo-specific rule:

- Before opening a PR for a spec slice or a slice-owned follow-on patch backed
  by a Speckit artifact chain, the session MUST run or otherwise complete the
  `speckit.analyze` step and address or explicitly log any blocking findings.

Skipping commit-assist hooks does **not** waive this requirement. The rigor
comes from the artifact cross-check, not from the commit boundary itself.

## Hook boundary

Repo-local hooks can reinforce re-entry at workflow boundaries such as
`before_plan`, `before_tasks`, and `before_implement`.

They cannot, by themselves, guarantee the very first chat message of a new
session across every client or bridge. That stronger guarantee belongs in the
session harness / client bootstrap layer.

So the enforcement split is:

- **repo protocol**: mandates the `READINESS` line as the first substantive
  response
- **repo hooks**: can check that re-entry steps were completed before major
  workflow transitions
- **harness / client integration**: future hardening if we want the `READINESS`
  line enforced at process start rather than just by repo protocol

## Generic-skill override

Generic skills do not override this repo's local ways of working.

In particular:

- for PR reviews in this repo, follow
  [`docs/ways-of-working/pull-requests.md`](./pull-requests.md)
- for GitHub Discussions replies in this repo, follow
  [`docs/ways-of-working/github-discussions-replies.md`](./github-discussions-replies.md)

Repo-local guidance supersedes generic PR-review or code-review defaults.

## Minimum re-entry checklist

Before continuing past orientation, the session should be able to answer:

- Which slice do I own right now?
- Which worktree and branch am I using?
- Which surfaces are mine to touch, and which are not?
- Which files did I read before starting?
- What is the next Speckit step or review step?

If any answer is missing, stop and resolve it before continuing.
