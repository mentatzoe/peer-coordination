# Feature Specification: Pinned-Rules Authoring and Exposure

**Feature Branch**: `003-pinned-rules-authoring`
**Created**: 2026-04-19
**Status**: Clarified (self-resolved per operator directive on 2026-04-19 authorizing autonomous speckit progression)
**Input**: Define the authoring and exposure workflow for the pinned-rules artifact that constitutes Layer 2 coordination context in the POC. The rules must be git-tracked (so session bundles can reference them by commit hash per spec 001 FR-010 `pinned_rules_ref`), operator-maintained, and exposed to peers via Discord pinned messages. Out of scope: the full *content* of the rules (a seed v1 lands as starter text; actual content is operator-curated over time), the cc-connect-side automation of pin synchronization (potential Phase 2 follow-on), and Layer 2 / Layer 3 spec extraction (also follow-on).

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) §"Pilot-local assumptions" (pinned messages as the rule-exposure mechanism), §"Shared surface artifacts" (L2 pinned rules as a required component), and FR-010 ("pinned_rules_ref" in session meta).
  - [`design/architecture.md`](../../design/architecture.md) Layer 2 ("thin visible norm set, supplied by a separate artifact or operator-managed shared content, and made visible in-channel").
  - [`.specify/memory/constitution.md`](../../.specify/memory/constitution.md) Principle VI (coordination is human-legible, not over-protocolized).
- **Architecture reference**: Layer 2 owns the *meaning* of coordination artifacts once Layer 1 has made them visible. This spec defines an artifact Layer 2 exposes but does not author meaning; meaning is operator-maintained prose.
- **Roadmap workstream**: `Baseline substrate build` (Phase 1, repo-side session-artifact slice).
- **Staffing**: Claude lead (repo-side scaffolding slice per [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41)); Codex cross-reviewer when cycles allow per the ratified autonomous loop.
- **Depends on**: spec 001 (session-bundle-skeleton) for the `pinned_rules_ref` consumer contract.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Operator authors and exposes pinned rules once per session (Priority: P1)

As the operator, before a session opens, I need to author (or confirm current) pinned rules and expose them to the peers via Discord pinning, then record the ruleset commit hash in the session's `meta.json` so the session is auditable against the exact rules that governed it.

**Why this priority**: every session depends on this. Without a repeatable, git-tracked rules artifact, session bundles can't point at a real ruleset and H2 legibility review can't reconstruct what norms governed each session.

**Independent Test**: hand the operator an empty repo state for pinned-rules, walk them through opening a new session per `design/poc.md`, and verify a valid `pinned_rules_ref` commit hash can be recorded in the session's `meta.json`.

**Acceptance Scenarios**:

1. **Given** the operator is about to open a session, **When** they open `pinned-rules/current.md`, **Then** the file contains the current canonical ruleset and a reference to the authoring workflow.
2. **Given** `pinned-rules/current.md` is at commit `<hash>`, **When** the operator opens a session and records `pinned_rules_ref: "<hash>"` in `meta.json`, **Then** the session is auditable against those exact rules regardless of subsequent edits.

### User Story 2 — Operator updates rules between sessions (Priority: P1)

As the operator, after a session yields a finding that the rules should change (observed drift, ambiguity, missing norm), I need to update `pinned-rules/current.md` in a discrete commit, re-pin the updated content in Discord, and be confident that past sessions still reference their own rulesets.

**Why this priority**: the rules must evolve over the POC without breaking past-session auditability. Discrete git commits for rule changes + pinning to a commit hash in session bundles solve both halves.

**Independent Test**: after authoring v1 rules and running a mock session, update the rules with a discrete commit, re-pin, verify the old session's bundle still references the v1 commit hash (not the new one).

**Acceptance Scenarios**:

1. **Given** a session bundle references `pinned_rules_ref: "<commit-A>"` for a past session, **When** the operator updates rules to commit `<commit-B>`, **Then** the past session's audit trail still resolves to commit `<commit-A>` content.
2. **Given** rules are updated, **When** a new session opens, **Then** the operator captures the new commit hash in the new session's `meta.json`.

### User Story 3 — Reviewer audits a session against the rules it was governed by (Priority: P1)

As a reviewer (agent or human), I need to take a session bundle's `pinned_rules_ref` and resolve to the exact rules content, so I can judge H2 legibility and detect drift against what was in force at the time.

**Why this priority**: H2 legibility audit depends on "did peers drift from the shared norms that were visible at the time?" Without commit-ref resolution, the reviewer can't pin down which rules were active.

**Independent Test**: given a session bundle's `pinned_rules_ref`, check out that commit and read `pinned-rules/current.md` to get the effective ruleset.

**Acceptance Scenarios**:

1. **Given** a session bundle with `pinned_rules_ref: "<commit>"`, **When** the reviewer checks out that commit, **Then** `pinned-rules/current.md` reflects exactly the rules the peers had access to.
2. **Given** `pinned_rules_ref` is an inline fallback (no git-tracked rules at the time, e.g., earliest sessions), **When** the reviewer opens `meta.json`, **Then** the inline snapshot contains the full ruleset content.

### Edge Cases

- **Rules changed mid-session**: per `design/poc.md` session definition, a pinned-rules change closes the session (`close_reason: pinned_rules_change`). So rules don't change within a single session; the session closes and a new one opens against the new rules. Spec design is consistent with this invariant.
- **Operator forgot to record `pinned_rules_ref`**: session bundle is incomplete per spec 001 FR-010; the bundle must be amended with the correct commit hash before it counts toward KPI rollup.
- **Rules file is empty or missing** at session open: operator must author rules before opening a session. Session-open without a valid ruleset is a procedural error.
- **Discord pinned message diverges from git**: the source of truth is the git commit at `pinned_rules_ref`; the Discord pin is an *exposure* copy. If they diverge, the git version wins (reviewers resolve against the commit, not the Discord pin).
- **Multiple Discord pinned messages**: Discord allows multiple pins. Only `pinned-rules/current.md` content counts as "the rules" for `pinned_rules_ref` purposes. Other pins (announcements, channel info) are not coordination rules and are not referenced.

## Requirements *(mandatory)*

### Functional Requirements

**Directory and files:**

- **FR-001**: The repo MUST contain a top-level directory `pinned-rules/` that holds the canonical coordination ruleset.
- **FR-002**: `pinned-rules/current.md` is the single canonical rules file. It contains the content that is expected to be visible to peers during sessions (via Discord pinning, for the Phase 1 POC).
- **FR-003**: `pinned-rules/README.md` MUST explain: the authoring workflow, the commit-hash-reference contract with session bundles, the exposure mechanism (Discord pinning for the POC), the edit-and-new-session rule, and the cross-references to `design/poc.md` / `design/architecture.md` / constitution Principle VI.
- **FR-004**: `pinned-rules/CHANGELOG.md` MAY exist for human-readable rules-version summary, but the authoritative version history is git itself. The CHANGELOG is a convenience.

**Authoring workflow:**

- **FR-005**: Rules updates MUST be **discrete commits** with a message of the form `pinned-rules: <short summary>`. One logical rules change per commit; rationale lives in the commit message.
- **FR-006**: Rules content MUST be human-readable markdown — no JSON, no code, no implementation detail. The rules are for peer agents to read and internalize, not for tooling to parse.
- **FR-007**: Rules SHOULD be short enough to pin on Discord (Discord pinned-message limit is 2000 characters per message; multiple pins possible but MUST be avoided for rule content — see FR-008). Longer rules require splitting the ruleset into a summary pinned message + a git-linked full version. For the initial POC the short-rules path is preferred.
- **FR-008**: **Exactly one** Discord pinned message MUST carry the rules. If splitting is needed for length, the pinned message MUST be a short summary + a link to the repo's `pinned-rules/current.md` at the session's commit. Multiple rule-carrying pins is not allowed (ambiguity).

**Exposure workflow:**

- **FR-009**: The operator is responsible for the Discord pinning step. Agents MUST NOT modify pins autonomously in Phase 1 (no cc-connect automation yet; that's a potential Phase 2 follow-on). The exposure mechanism is operator-manual.
- **FR-010**: On rules change, the operator MUST re-pin the updated content before opening a new session against it. Old pins MUST be removed.
- **FR-011**: Session bundles MUST reference the rules via `pinned_rules_ref` in `meta.json` per spec 001 FR-010. **Preferred**: commit hash of `pinned-rules/current.md` active at session open. **Fallback**: inline snapshot `{inline: "<content>"}` for sessions where rules were not git-tracked at the time (earliest sessions only; should become rare after FR-001 lands).

**Content constraints (for the canonical `current.md`):**

- **FR-012**: Rules content MUST include at minimum: an emoji-palette definition (✅👀🤔🚫⏸️ at time of writing), `!stop` / `!resume` semantics, turn-taking expectations (yielding / claiming / building as heuristics, not protocol), escalation path for unresolved ambiguity (operator arbitration), and a reference to the governing principles (constitution Principle VI).
- **FR-013**: Rules content MUST NOT duplicate governance text from `VISION.md` / `design/architecture.md` / constitution. Instead, rules cite those artifacts for their authority.
- **FR-014**: Rules content MUST stay under ~1500 characters (rendered plain text, not including markdown formatting) to fit a single Discord pinned message comfortably. If it grows beyond that, trigger FR-007's split pattern.

### Key Entities

- **Pinned rules**: the content of `pinned-rules/current.md` at a given git commit. Immutable once committed; new content = new commit. Referenced from session bundles by commit hash.
- **Pin exposure**: the operator's action of copying `pinned-rules/current.md` content into a Discord pinned message. One pin per ruleset version. Required before a session opens against a given ruleset.
- **Rule-change session break**: per `design/poc.md` session definition, a pinned-rules change closes the current session. New rules = new session on those rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every counted session in Phase 3 or later, `meta.json.pinned_rules_ref` resolves to a valid reachable state (commit hash resolves to a `pinned-rules/current.md` file, OR inline snapshot is non-empty and self-contained).
- **SC-002**: A reviewer checking out any session's `pinned_rules_ref` commit can produce the exact rules content the session was governed by, in under 2 minutes using standard git tooling.
- **SC-003**: 100% of rules-change commits follow the `pinned-rules: <summary>` message format and are discrete (one logical change per commit). Checked by grep + inspection at Phase 1 exit.
- **SC-004**: Discord pinned-message content matches the latest committed `pinned-rules/current.md` at the time of any open session. Manual operator check at session open; any mismatch is a procedural finding in the session's intervention log or summary.
- **SC-005**: The rules content is short enough to fit a single Discord pin (≤1500 rendered chars) at Phase 1 exit. If the ruleset has grown past that, the split pattern in FR-007 is documented and applied.

## Assumptions

- The POC substrate is Discord; FR-008 (single-pin rule) is substrate-specific. Other substrates may have different exposure mechanisms; deferred to substrate-transfer specs.
- Operator bandwidth is sufficient to maintain rules by hand. Automation (cc-connect adapter for pin sync, agent-authored PRs against rules) is deferred to Phase 2 at earliest.
- Initial rules content is seeded at v1 and iterated as sessions surface gaps. The seed content included in the implementation is an operator starting point, not a final ratified ruleset.
- The constitution's promotion boundary applies: rules content is *not* governance; rules may change at project speed without constitutional amendment. Rules that would rise to the level of principle should instead be promoted via constitutional amendment per the existing workflow, then cited from rules.
- Agents do not modify rules autonomously in Phase 1. Rules authoring is operator-only. Agents may propose rule changes via discussion threads or scratchpad turns; operator ratifies and commits.

## Dependencies

- Depends on spec 001 (session-bundle-skeleton) for the consumer contract — `meta.json.pinned_rules_ref` semantics.
- Depends on `design/poc.md` v1 session definition (pinned-rules change closes session) being canonical. Satisfied — ratified via #38.
- Depends on constitution Principle VI (coordination is human-legible, not over-protocolized) being canonical. Satisfied — v1.5.0.
- Does NOT depend on any cc-connect automation (none exists; Phase 2 or later).
- Does NOT depend on the drift-audit rubric.

## Clarifications applied (self-resolved 2026-04-19)

Per Zoe'"'"'s directive authorizing autonomous speckit progression in the absence of peer-to-peer comms, the following decisions were self-resolved inline rather than left as open questions. Cross-reviewer may amend retroactively.

1. **Directory location**: `pinned-rules/` at repo root. Alternatives considered: `coordination/pinned-rules/` (scope-nested), `observations/pinned-rules/` (evaluation-nested). Repo-root placement is clearest because pinned-rules are a first-class L2 artifact referenced by both session bundles and governance docs; nesting would obscure discoverability.
2. **Single canonical file vs versioned-file-per-revision**: Single `current.md` with versioning via git commits. Rationale: git is the version-control mechanism the repo already uses; duplicating with `v1.md` / `v2.md` / etc. creates drift and forces the reader to pick. Commit-hash references handle historical lookup.
3. **Operator-only authoring**: agents do not commit to `pinned-rules/` autonomously in Phase 1. Agents may propose changes via discussion / scratchpad; operator ratifies and commits. Rationale: rules shape peer behavior; allowing peers to edit their own rules creates a self-modifying-system surface that'"'"'s out of scope for Phase 1.
4. **Single-pin rule on Discord (FR-008)**: one Discord pinned message for rules only. Alternatives (multiple pins, pin + git link combo for long rules) preserved as fallbacks via FR-007'"'"'s split pattern. Initial POC runs on short rules.
5. **CHANGELOG optional**: CHANGELOG.md is opt-in; git log is authoritative. Keeps operator overhead low; if the CHANGELOG becomes useful, operator adds it. No requirement to maintain.

All five defaults are defaults, not immutable. If cross-review disagrees, amend commits can revise any of them.

## Open questions for cross-review (none substantive; the five above were self-resolved)

If the cross-reviewer sees an architectural or schema issue I missed, flag in the review thread and I'"'"'ll land an amend commit.
