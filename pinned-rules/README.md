# Pinned Rules

This directory holds the canonical **Layer 2 coordination ruleset** for the peer-coordination POC. Rules live in [`current.md`](current.md); versioning is via git commits.

**Authoritative spec**: [`specs/003-pinned-rules-authoring/spec.md`](../specs/003-pinned-rules-authoring/spec.md).
**Architecture context**: [`design/architecture.md`](../design/architecture.md) Layer 2 — "thin visible norm set, supplied by a separate artifact or operator-managed shared content, and made visible in-channel so peers can infer how to collaborate."
**Governing principle**: Constitution [Principle VI](../.specify/memory/constitution.md#vi-coordination-is-human-legible-not-over-protocolized).

## What these rules are

- **Short, human-readable prose** that tells peers (and the operator) how to coordinate during a POC session.
- **Operator-maintained**. Agents do not edit these rules autonomously in Phase 1; agents may propose changes via discussion or scratchpad, operator ratifies and commits.
- **Visible in-channel**. For the Phase 1 Discord POC, the content of `current.md` is copied into a Discord pinned message before a session opens.

## What these rules are NOT

- Not governance. Constitutional principles live in `.specify/memory/constitution.md` and are ratified with versioned amendments. Rules cite the constitution; they don't duplicate or amend it.
- Not implementation detail. Transport mechanics (how `!stop` works at the wire level, etc.) live in `cc-connect/` and specs. Rules describe the norm peers should interpret, not the machinery that enforces them.
- Not a protocol. Per Principle VI, rules prefer heuristics over brittle handshake protocols.

## Authoring workflow

1. **Propose**: anyone (operator, agents) can propose a rule change via a discussion thread, scratchpad turn, or observation entry. For agents, proposals land in discussion comments; agents do not commit directly to this directory.
2. **Ratify**: the operator reviews and decides whether to change the rules.
3. **Commit**: the operator updates `current.md` and commits with message `pinned-rules: <short summary>`. One logical change per commit.
4. **Re-pin**: the operator updates the Discord pinned message to match the new `current.md` content. Old pin is removed.
5. **Close any in-flight session**: per [`design/poc.md`](../design/poc.md) session definition, a pinned-rules change **closes the current session** (close_reason: `pinned_rules_change`). A new session opens against the new ruleset.

## Commit-reference contract with session bundles

Every committed session bundle records `meta.json.pinned_rules_ref` per [spec 001 FR-010](../specs/001-session-bundle-skeleton/spec.md):

- **Preferred**: commit hash of `pinned-rules/current.md` at session open.
- **Fallback**: `{"inline": "<raw content>"}` when no git-tracked rules existed at the time (should be rare after this directory lands).

A reviewer takes a session's `pinned_rules_ref`, checks out that commit, and reads `pinned-rules/current.md` to get the exact ruleset the peers had access to. This is the anchor for H2 legibility audit.

## Exposure discipline (Discord pin)

- **One pinned message carries the rules.** Multiple rule-carrying pins is not allowed (ambiguity).
- **If rules outgrow ~1500 rendered characters**, use the summary + repo-link split pattern: the pin is a short summary + a link to `pinned-rules/current.md` at the specific commit. Initial POC keeps short rules.
- **Discord is exposure, not source of truth.** If the pinned message diverges from `current.md` at the session's commit, the git version wins. Operator must keep them in sync by re-pinning after every rules change.

## Why single `current.md` + git versioning

Alternatives considered:

- `v1.md` / `v2.md` / etc. per-version files — creates drift, forces reader to pick, duplicates content.
- Multiple pinned messages with sub-rules — creates ambiguity about which pin is authoritative.

Single `current.md` with git commits as versions keeps the mental model flat: "what's the current ruleset?" = HEAD; "what ruleset governed session X?" = checkout the commit referenced in that session's bundle.

## CHANGELOG.md

Optional convenience. Git log is authoritative. See [CHANGELOG.md](CHANGELOG.md) if present.

## Cross-references

- [`specs/003-pinned-rules-authoring/spec.md`](../specs/003-pinned-rules-authoring/spec.md) — the authoritative spec.
- [`specs/003-pinned-rules-authoring/plan.md`](../specs/003-pinned-rules-authoring/plan.md) — implementation plan.
- [`specs/001-session-bundle-skeleton/spec.md`](../specs/001-session-bundle-skeleton/spec.md) — consumer contract (`pinned_rules_ref`).
- [`design/poc.md`](../design/poc.md) — Pilot-local assumptions, Session Definition, Layer 2 shared-surface components.
- [`design/architecture.md`](../design/architecture.md) — Layer 2 capability requirements.
- [`.specify/memory/constitution.md`](../.specify/memory/constitution.md) — Principle VI.
