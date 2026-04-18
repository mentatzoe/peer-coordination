# Scratchpad: Roadmap Separation and Gap Analysis

> **How to use this scratchpad — read before editing.**
>
> A scratchpad is a living design log shared between the operator and two or
> more agents. It has **two zones with different edit rules**.
>
> ### Zone 1 — Policy Body *(EDIT IN PLACE)*
>
> Everything from the metadata header through **Next Actions**. When consensus
> shifts, overwrite this content freely. Prior versions are **not** preserved
> here — the Discussion Log is the history.
>
> ### Zone 2 — Discussion Log *(APPEND ONLY)*
>
> Everything below the `## Discussion Log` heading. **Never** rewrite, reorder,
> or delete prior turns. Add new turns at the bottom, signed and dated.
>
> ### Promotion boundary
>
> Scratchpad convergence does **not** by itself amend durable artifacts such as
> the constitution, specs, or project guidance. Scratchpads may stage proposed
> text and recommend changes, but applying those changes requires an explicit
> operator-directed promotion step.

---

**Status**: `draft`
**Authors**: Zoe, Claude (Station), Codex (Vigil, pending review)
**Created**: 2026-04-18
**Last Updated**: 2026-04-18
**Scope (one line)**: Audit current roadmap vs. original scratchpad; propose separating the roadmap from the constitution; identify gap-fill specs for concepts that have no current home.
**Promotion Target**: TBD — likely a new `ROADMAP.md` + constitution amendment removing the embedded roadmap list.
**Length Budget**: target < 500 lines.

---

## Purpose *(mandatory, edit in place)*

The constitution currently embeds a 4-item roadmap (P1–P4) inside its
`Specification Workflow and Roadmap` section. Since that embedding, the project
has chunked several MVP items into separate specs (001, 003, planned 004/005),
and several concepts from the original scratchpad have ended up without a clear
spec home (notably the 7 coordination heuristics, emoji palette, and pilot
profile). This scratchpad audits the state of the art, maps scratchpad concepts
to their current homes, identifies gaps, and proposes a structural move: pull
the roadmap out of the constitution and maintain it as a living document.

## Scope *(mandatory, edit in place)*

**In scope:**

- Audit of existing specs, PRs, roadmap issues, branches.
- Gap analysis mapping scratchpad concepts (from `archive/ideas/peer-coordination.md`) to their current spec/issue home (or gap).
- Proposal to move the roadmap out of the constitution.
- Proposal for gap-fill specs for concepts with no current home.

**Out of scope:**

- Drafting the gap-fill specs themselves — that's follow-on work after this proposal is ratified.
- Actually amending the constitution — requires explicit operator promotion per Principle III.
- Re-opening decisions already ratified (chunking, promotion-boundary rule, independent-review expectation).

## Design Goals *(edit in place)*

1. The constitution should be durable; the roadmap should be living. Separation reflects that cadence difference.
2. Every concept from the original scratchpad should have exactly one clear home (or be explicitly deferred).
3. The roadmap should reflect actual spec structure (post-chunking), not the pre-chunking abstraction.
4. No proposal here should enlarge agent autonomy beyond what the constitution already permits.

## Policy / Current Thinking *(mandatory, edit in place)*

### Section 1 — State of the Art

**Specs in flight (branches + PRs):**

| Spec | Branch | Scope | Owner | Status |
|---|---|---|---|---|
| 001-transport-mvp | `001-transport-mvp` | MVP items 1 (open-floor routing + self-loop) + 2 (`!stop`/`!resume`) | Vigil (Codex) | PR #29 draft, review round |
| 002-channel-policy-presence | `002-channel-policy-presence` | Channel activation modes, verbosity, allowlist, per-bot presence | Dalgos (Claude) | Parked; no PR; 4 user stories + 14 FRs drafted last night before scope correction |
| 003-agent-initiated-reactions | `003-agent-initiated-reactions` | MVP item 3 (reaction add/remove) | Dalgos (Claude) | PR #30 open; self-review applied; awaiting Codex review on plan+tasks |

**Roadmap-tracking issues** (all OPEN on `main`, with the `roadmap` label):

| Issue | Title | Owner label | Spec state |
|---|---|---|---|
| #4 | Roadmap P1: Transport MVP Spec | `owner:codex` | Draft (PR #29) |
| #2 | Roadmap P2: Channel Policy and Presence Spec | `owner:claude` | Draft parked |
| #1 | Roadmap P3: Workspace and Session Binding Spec | `owner:unassigned` | Not started |
| #3 | Roadmap P4: Operations and Rollout Spec | `owner:unassigned` | Not started |

**Historical (closed) issues:** #5–#28 were per-task issues filed from the pre-chunking broad-scope 001 spec. Closed when 001 was narrowed. Preserved in git history via `archive/specs/001-transport-mvp-broad-scope.md`.

**Constitution state:** `.specify/memory/constitution.md` v1.3.0. Roadmap embedded in the `Specification Workflow and Roadmap` section as a 4-item list (P1–P4).

### Section 2 — Gap Analysis

Mapping every concept from the original scratchpad (archived at `archive/ideas/peer-coordination.md`) to its current home:

| Scratchpad concept | Current home | Status |
|---|---|---|
| **5 Design Goals** (interesting bot-to-bot convos, no ack-loops, low friction, safe by default, operator as arbiter) | Nowhere | **GAP** |
| **3 Channel Activation Modes** (mention-only, thread-initiator, open-floor) | 002 draft (parked) | Draft exists; not merged |
| **7 Coordination Heuristics** (claim, yield, build, react-don't-ack, silence-OK, tangents-OK, escalate-to-scratchpad) | Nowhere — trimmed from constitution in v1.1.1 | **GAP** |
| **Emoji Palette** (✅👀🤔🚫⏸️) | Nowhere | **GAP** |
| **Safe Word `!stop`/`!resume`** | 001 (Vigil) | Covered |
| **Tool Use & Human Approval** | Constitution Principle IV (abstract) + 004 planned (specific) | Constitutional + future spec |
| **Transport vs Agent Separation** | Constitution Principle II | Constitutional |
| **Pilot Profile** (first live test config: which bots, which channel, approval rules) | Nowhere — lives only in scratchpad archive | **GAP** |
| **MVP item 1** (`!stop`/`!resume`) | 001 (Vigil) | Covered |
| **MVP item 2** (open-floor + no-self-loop) | 001 (Vigil) | Covered |
| **MVP item 3** (reactions) | 003 (Dalgos, PR #30) | Covered |
| **MVP item 4** (approval-via-react) | Planned 004 (Dalgos) | Not drafted |
| **MVP item 5** (pinned-rules ingestion) | Planned 005 (Dalgos) | Not drafted; earmarked second pass |
| **"Out of MVP" per-channel allowlist + verbosity + mode** | 002 draft | Draft exists |
| **"Out of MVP" per-bot role config** | Nowhere | Deferred |
| **"Out of MVP" cross-channel policy inheritance** | Nowhere | Deferred |
| **"Out of MVP" transport-enforced thread-initiator ownership** | 002 draft (partial) | Partial coverage |

**Summary of gaps** (things without a home):

1. **7 Coordination Heuristics** — primary gap; flagged in previous Discord exchange.
2. **Emoji Palette** — operational convention; naturally pairs with heuristics.
3. **Pilot Profile** — operator's config for the first live test; referenced in 001/003 but not captured as a spec artifact.
4. **5 Design Goals** — meta-level; could be constitutional principles or a companion vision doc.
5. **Roadmap entry drift** — P1 "Transport MVP Spec" no longer reflects the chunking (it covers items 1+2; items 3/4/5 are separate specs).

### Section 3 — Proposal A: Move the roadmap out of the constitution

**Current**: constitution v1.3.0, `Specification Workflow and Roadmap` section, embeds the 4-item list directly.

**Proposed**: 
1. New file at repo root: **`ROADMAP.md`**. Maintains the current spec list + MVP-item mapping + status + ownership + dependencies. Evolves freely without constitution amendments.
2. Constitution `Specification Workflow and Roadmap` section is reduced to the *workflow* only (the 5 numbered steps from explore-in-scratchpad to feed-results-back). The *list* is replaced with a one-line pointer: `The current roadmap of follow-on specs is maintained in` [`ROADMAP.md`](../../ROADMAP.md)`. See that file for priority-ordered spec status, ownership, and dependencies.`
3. Version bump: v1.3.0 → **v1.4.0** (MINOR — materially changed section, removed a specific list, kept the workflow).

**Why**:
- Roadmap is project-state tracking, not governance.
- Each addition/split/rename currently requires a v-bump on the constitution. That friction discourages keeping the roadmap accurate.
- Moving it out doesn't weaken governance — the constitution still mandates the workflow and the promotion path.

**Alternative locations considered**:
- `docs/roadmap.md` — more structured but less discoverable.
- `specs/roadmap.md` — lives next to specs but conflates tracking with specs themselves.
- **Lean**: `ROADMAP.md` at repo root (most discoverable, follows common OSS convention).

### Section 4 — Proposal B: Gap-fill specs

**P5: Coordination Heuristics Spec** (proposed new spec)

Owns:
- The 7 coordination heuristics.
- The emoji palette (✅👀🤔🚫⏸️).
- The "react-driven loop prevention" rule.
- The "transport must not block inter-agent replies" rule.

Intended composition:
- P5 *defines* the heuristics.
- Operator *pins* the relevant subset to each open-floor channel.
- MVP item 5 / spec 005 (pinned-rules ingestion) provides the runtime mechanism to get the pinned rules into agent context.

Thus three concerns compose cleanly: **P5 defines → operator pins → 005 ingests**. The constitution's v1.1.1 follow-up TODO (which pointed the heuristics at the Transport MVP Spec, but was orphaned by the chunking) gets a correct home.

**Pilot Profile: fold into 001 or create P6?**

Two defensible options:
- Fold into Vigil's 001 (Transport MVP Spec) as a concrete "Pilot Configuration" section. Keeps pilot-specific state with the transport that runs it.
- New spec P6 "Pilot Operations" for the pilot-specific config, graduation path, rollback plan. Might be redundant with P4 Operations and Rollout.

**Lean**: fold into 001 OR eventual P4. Don't create P6.

**Design Goals: companion doc, not spec**

The 5 design goals are operator-level intent. Not a spec (no user stories, no FRs). Options:
- Promote to constitutional principles. MAJOR bump. Heavy; goals aren't quite principles.
- Create `docs/design-goals.md` as a vision companion. Lightweight; references constitution.
- Leave in archived scratchpad. Status quo; loses visibility.

**Lean**: `docs/design-goals.md` companion doc.

### Summary of gap-filling actions

| Gap | Proposed home | Action |
|---|---|---|
| 7 Coordination Heuristics | New P5 Coordination Heuristics Spec | Scope + draft |
| Emoji Palette | P5 | Include in P5 |
| Pilot Profile | 001 (Vigil) or P4 | Vigil's call; likely 001 |
| Design Goals | `docs/design-goals.md` | New companion doc (not a spec) |
| Roadmap entry drift | `ROADMAP.md` | Proposal A above |

## Resolved Questions *(edit in place)*

*(None yet — all questions below are open.)*

## Open Questions *(edit in place)*

- **Q1: Does the roadmap move out of the constitution?** If yes, to `ROADMAP.md` at repo root — owner: Zoe; blocks Proposal A; affects constitution version.
- **Q2: Is `ROADMAP.md` at repo root the right location?** Alternative: `docs/roadmap.md`. Owner: Zoe; non-blocking for Proposal A substance.
- **Q3: Is P5 the right home for the 7 heuristics + emoji palette?** Alternative: fold into 005 pinned-rules as default pinnable content. Owner: Claude + Codex; blocks Proposal B substance.
- **Q4: Where does the Pilot Profile live?** 001 (Vigil) or new P6, or P4 once drafted. Owner: Vigil first, then Zoe arbitrates.
- **Q5: How are the 5 Design Goals surfaced?** Companion doc `docs/design-goals.md` vs constitutional principles vs staying in archive. Owner: Zoe; non-blocking.
- **Q6: Should the roadmap-tracking issues (#1–#4) be updated to reflect the chunking, or closed and refiled?** Owner: Zoe + Claude; procedural.
- **Q7: Who drafts P5?** Natural owner is whoever authored the scratchpad text (me/Claude) since the heuristics came from our brainstorm — but Vigil's rigor on abstraction boundary is valuable. Could be co-authored or split (Claude drafts, Vigil reviews).

## Next Actions *(edit in place)*

1. Codex reviews this scratchpad and responds in Discussion Log.
2. Zoe arbitrates on Q1–Q7 once both agents have weighed in.
3. On Zoe's explicit "promote" call:
   - If Q1 yes → create `ROADMAP.md`, amend constitution to v1.4.0 (remove embedded list, add pointer).
   - If Q3 P5 approved → scope + draft P5 spec (scratchpad-first per Principle III).
   - If Q5 companion doc approved → create `docs/design-goals.md` lifting from `archive/ideas/peer-coordination.md`.
4. Update roadmap-tracking issues per Q6 resolution.
5. This scratchpad promotes/archives when Open Questions is empty and the operator signals ready.

---

## Discussion Log *(APPEND ONLY — never rewrite prior turns)*

### Claude (Opus 4.7, via Station) — 2026-04-18 ~12:00 UTC (kickoff: audit + proposal seed)

Zoe asked via voice message: look at the state of the art, map it to GitHub issues, identify gaps between the existing roadmap and the original scratchpad, and draft a proposal + scratchpad for Codex discussion. This scratchpad is that proposal + discussion surface.

The audit and gap analysis are in the Policy Body above. Two proposals:

- **Proposal A** — move the roadmap out of the constitution into `ROADMAP.md`, bump constitution to v1.4.0.
- **Proposal B** — gap-fill specs: P5 Coordination Heuristics, fold Pilot Profile into 001 or P4, companion `docs/design-goals.md`.

Five gaps identified, five mapped proposed homes. Seven open questions for Codex/Zoe to work through.

**What this scratchpad deliberately doesn't do**: apply any changes. Per the promotion-boundary rule (constitution v1.2.0), scratchpad convergence alone doesn't modify durable artifacts. I'm not editing the constitution, not creating `ROADMAP.md`, not drafting P5 — just staging the proposal for review.

**On the "silent drop" bug from earlier** (twice in 15 minutes today): noted. For this turn I'm committing the scratchpad first and then following with a Discord reply, as a practice pattern to make the send-step explicit.

→ over to Codex (Vigil) for review of the audit, gap analysis, and the two proposals; → over to Zoe for arbitration on Q1–Q7 once Codex has responded
