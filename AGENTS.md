> **Before any work in this repo**: read
> [`docs/ways-of-working/session-reentry.md`](docs/ways-of-working/session-reentry.md).
> It is the authoritative session-reentry protocol. If it conflicts with this
> file, the protocol wins.
>
> **Repo-specific override**: for PR reviews in this repo, follow
> [`docs/ways-of-working/pull-requests.md`](docs/ways-of-working/pull-requests.md).
> Its requirements supersede any generic PR-review skill defaults.

# peer-coordination Agent Guidelines

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the active plans in
`specs/*/plan.md`, especially `specs/002-cc-connect-relocation/plan.md` for the
current Codex-owned Phase 1 slice
<!-- SPECKIT END -->

## Purpose

This repository defines the multi-agent coordination standard itself.
Its repo root is the governance/specification surface. A contained
`cc-connect/` workspace may live here as a subordinate implementation surface
for the current POC, but that does not make transport code the source of
policy.

## Scope Boundaries

- Keep constitutions, specs, scratchpads, and decision records here.
- Treat the contained `cc-connect/` workspace as an implementation target inside
  this repo, and downstream repos such as `personal-agent-setup` as consumers
  of this standard.
- Do not silently move governance decisions back into downstream repos.

## Working Norms

- Use the scratchpad at `ideas/peer-coordination.md` as the live design log
  until the constitution and follow-on specs absorb finalized decisions.
- Prefer explicit documentation of confirmed decisions, open questions,
  manual steps, and next actions.
- Keep the distinction between governance and transport clear:
  `cc-connect` is transport/session plumbing, not the source of policy, even
  when its code is physically contained under this repo.
- Avoid artificial behavioral rules for agents where observed organic drift is
  sufficient.
- For spec slices and slice-owned follow-on patches, follow the Speckit
  git-hook branch workflow when available, and merge via PR by default. See
  `docs/ways-of-working/pull-requests.md`. Direct-to-`main` is reserved for
  trivial fixes or explicit operator instruction.

## Speckit Flow

- Establish or amend the constitution first with `$speckit-constitution`.
- Use `$speckit-specify`, `$speckit-clarify`, `$speckit-plan`, and
  `$speckit-tasks` for follow-on work.
- Keep specs in this repo focused on the standard; track code changes in the
  downstream implementation repos they belong to.
