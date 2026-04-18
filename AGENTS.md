# peer-coordination Agent Guidelines

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/001-transport-mvp/plan.md`
<!-- SPECKIT END -->

## Purpose

This repository defines the multi-agent coordination standard itself.
It is a governance and specification repo, not the implementation home for
transport or product code.

## Scope Boundaries

- Keep constitutions, specs, scratchpads, and decision records here.
- Treat downstream repos such as `cc-connect` and `personal-agent-setup` as
  implementation targets or consumers of this standard.
- Do not silently move governance decisions back into downstream repos.

## Working Norms

- Use the scratchpad at `ideas/peer-coordination.md` as the live design log
  until the constitution and follow-on specs absorb finalized decisions.
- Prefer explicit documentation of confirmed decisions, open questions,
  manual steps, and next actions.
- Keep the distinction between governance and transport clear:
  `cc-connect` is transport/session plumbing, not the source of policy.
- Avoid artificial behavioral rules for agents where observed organic drift is
  sufficient.

## Speckit Flow

- Establish or amend the constitution first with `$speckit-constitution`.
- Use `$speckit-specify`, `$speckit-clarify`, `$speckit-plan`, and
  `$speckit-tasks` for follow-on work.
- Keep specs in this repo focused on the standard; track code changes in the
  downstream implementation repos they belong to.
