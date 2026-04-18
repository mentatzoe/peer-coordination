# Specification Quality Checklist: Channel Policy and Presence

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-04-18
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — spec describes the policy surface and acceptance criteria; specific config formats and transport plumbing are deferred to the plan.
- [x] Focused on user value and business needs — each user story names the operator problem it solves.
- [x] Written for non-technical stakeholders — avoids Discord-specific API terminology where possible; terms like "activation mode" and "verbosity" are introduced with plain-language descriptions.
- [x] All mandatory sections completed (User Scenarios & Testing, Requirements, Success Criteria).

## Requirement Completeness

- [x] Functional requirements cover all four user stories.
- [x] Each user story has an independent-test description.
- [x] Each user story has acceptance scenarios in Given/When/Then form.
- [x] Edge cases surfaced for each of mode, verbosity, allowlist, and presence dimensions.
- [x] Key entities defined for every major concept the spec introduces.
- [x] Success criteria are measurable (observable rendered output, presence/absence of responses, inspection of effective policy).

## Governance Alignment

- [x] Preserves Principle II (transport is plumbing, not governance) — spec governs the policy declaration surface and defaults, not operational heuristics.
- [x] Preserves Principle VI (coordination is human-legible) — verbosity is a rendering concern, not an agent-capability concern.
- [x] Does not re-introduce operational heuristics (the 7 coordination heuristics, ack patterns, loop-management rules) into constitutional territory.
- [x] Roadmap tie honored — this is P2, and the spec notes the dependency on P1 (Transport MVP) for routing semantics.

## Scope Boundaries

- [x] In-scope items enumerated: activation-mode selection per channel, verbosity levels, allowlist, per-bot presence, defaults, inspection.
- [x] Out-of-scope items named with pointer: routing semantics per mode live in the Transport MVP Spec; approval workflows for policy changes live under Principle IV and future operations spec; Discord-specific config format is a plan-level concern.
- [x] Cross-spec dependencies noted: P2 can land before P1 in principle, but some acceptance scenarios depend on Transport MVP routing semantics being defined.

## Open Items

- [ ] Plan (`plan.md`) to specify the on-disk config format (extend `config.toml` / `access.json` or introduce a new surface).
- [ ] Plan to specify the propagation mechanism for live policy changes (file-watch, daemon signal, hot reload).
- [ ] Plan to document how the `--channels` plugin for Claude Code will adopt the same declaration format, if at all.
- [ ] Tasks (`tasks.md`) to break out FRs into dependency-ordered implementation work.
