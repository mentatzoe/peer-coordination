# Pull Request Workflow

**Status**: active reference. Last updated 2026-04-19.
**Audience**: any agent or human collaborator landing a spec slice or
slice-owned follow-on implementation/doc patch in this repo.

## Why this doc exists

This repo uses GitHub Discussions for artifact review and convergence, but the
actual code/spec/doc deltas are easier to monitor when they land through a PR
rather than directly on `main`.

Discussion threads answer "what should change?" and "is this ready?".
PRs answer "what changed in the repo?".

Both are needed.

This repo already has the Speckit git extension enabled via
`.specify/extensions.yml`, including the `before_specify` feature-branch hook.
So this document is not introducing a parallel workflow; it is making the
expected Speckit + hook behavior explicit at the repo level and extending that
expectation to follow-on implementation/review work.

## Default rule

- **Spec slices and slice-owned follow-on implementation/doc patches land on a
  feature branch and merge via PR.**
- **Direct-to-`main` is the exception**, not the default.

Use a PR for:

- a new spec slice
- plan/tasks generation that materially changes an active slice
- implementation work owned by a slice
- cross-file doc rewrites tied to a slice or ratified follow-on
- any change another agent is expected to audit as a patch set

Direct-to-`main` is acceptable only for:

- trivial typo or wording fixes
- tiny follow-up consistency patches after review closure
- explicit operator instruction to skip PRs

## Branch naming

Use a branch per slice or patch train.

Examples:

- `codex-002-cc-connect-relocation`
- `claude-003-pinned-rules-authoring`
- `codex-architecture-fast-follow`

The branch name should make ownership and scope obvious.

## Expected flow

1. Let Speckit create/switch the feature branch when the git hook is active.
   If work begins outside `/speckit-specify`, create the equivalent feature
   branch manually before the slice patch train starts.
2. Run the normal artifact flow on that branch:
   spec -> clarify -> plan -> tasks -> implement, as applicable.
3. Use GitHub Discussions for design/spec review and convergence.
4. Open a PR once the branch is ready for patch review or merge review.
5. Link the governing discussion thread(s) in the PR body.
6. Merge only after the review checkpoint is satisfied.

## Relationship to Discussions

- **Discussion** is the review surface for document meaning, scope, and
  convergence.
- **PR** is the review surface for the actual diff.

For spec/doc slices, the usual pattern is:

1. Draft and review in a discussion.
2. Revise on the branch.
3. Open a PR for the final patch set.
4. Merge after LGTM.

For implementation slices run under the autonomous loop:

1. Work proceeds on a branch.
2. Implementation-complete is reported in the governing discussion.
3. Peer audit happens in discussion and/or PR review.
4. Merge happens through the PR once blockers are resolved.

## Agent expectations

- **Claude and Codex follow the same default**. Neither should assume
  direct-to-`main` unless the operator says so.
- When Speckit hooks are available, agents should follow them rather than
  bypassing them. Manual branch creation is only the fallback path.
- If an agent inherits a slice that already started on `main`, do not rewrite
  history to force compliance retroactively. Apply the PR rule to the next
  slice-owned patch train.
- If a branch/PR decision is unclear, prefer opening the PR.

## Minimum PR content

Every slice PR should include:

- the slice or patch name
- the owning discussion thread(s)
- what changed
- what was verified
- any open follow-up not included in the branch
