# Feature Specification: Discord Session Controls

**Feature Branch**: `004-discord-session-controls`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "Implement Discord session controls for the Phase 1 peer-coordination POC: explicit channel binding, session lifecycle boundaries, and operator !stop / !resume handling in the contained cc-connect workspace, aligned with design/poc.md and the session bundle contract."

## Context

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) Session Definition and Phase 1 baseline substrate requirements
  - [`design/architecture.md`](../../design/architecture.md) Layer 1 transport responsibilities
  - [`ROADMAP.md`](../../ROADMAP.md) Baseline substrate build workstream
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) for the eventual `channel_id` session-bundle consumer contract
- **Implementation surface**: contained [`cc-connect/`](../../cc-connect/) workspace, primarily the Discord platform adapter
- **Roadmap workstream**: `Baseline substrate build` (Codex-owned transport / substrate slice)
- **Out of scope for this slice**: transcript export, pinned-rules synchronization, session-bundle authoring, Gemini harness work

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bound Open-Floor Channel (Priority: P1)

As the operator, I need the Discord bot to bind to the intended Phase 1 channel so messages in other channels do not accidentally enter the peer-coordination runtime.

**Why this priority**: the Phase 1 dry run is not credible if the runtime can be triggered from the wrong Discord surface. Channel binding is the minimum guardrail that keeps the probe scoped to the agreed open-floor surface.

**Independent Test**: configure a bound Discord channel, mention the bot in both the bound and an unbound channel, and verify only the bound-channel message reaches the runtime.

**Acceptance Scenarios**:

1. **Given** the Discord platform is configured with a target channel binding, **When** an authorized user mentions the bot in that bound channel, **Then** the runtime accepts and routes the message normally.
2. **Given** the Discord platform is configured with a target channel binding, **When** an authorized user mentions the bot in a different channel, **Then** the runtime does not dispatch the message into the active peer-coordination session.

---

### User Story 2 - Safe Operator Stop/Resume (Priority: P1)

As the operator, I need `!stop`, `!resume`, and operator-first-post session opening to behave in line with the ratified session model so I can halt a live session safely and explicitly open a new one afterward.

**Why this priority**: unsafe interrupt behavior is an explicit harness-credibility failure in the POC. This is the safety-critical control surface for the first dry runs.

**Independent Test**: start a live Discord session, issue `!stop`, verify further peer messages do not continue or reopen the closed session, then issue `!resume` or post a new operator seed and verify a new session is opened.

**Acceptance Scenarios**:

1. **Given** a live session is active in the bound Discord channel, **When** the operator issues `!stop`, **Then** the current session closes and later peer messages do not continue that closed session.
2. **Given** the prior session was closed by `!stop`, **When** the operator issues `!resume` or posts the first operator seed for the next session, **Then** the runtime opens a new session rather than reviving the closed one.

---

### User Story 3 - Coherent Runtime Session Boundaries (Priority: P2)

As a reviewer or operator, I need the Discord transport to expose stable session-boundary behavior so later artifacts can explain which channel and logical session each exchange belonged to.

**Why this priority**: the POC depends on Layer 1 preserving a reviewable episode record. Even before transcript export lands, the runtime must stop blurring one Discord exchange into another.

**Independent Test**: run a dry sequence of bound-channel messages across one active session, one stopped session, and one resumed session, then inspect runtime-visible state/logs and confirm the channel/session boundary behavior is unambiguous.

**Acceptance Scenarios**:

1. **Given** a session is closed in the bound channel, **When** a non-operator posts again before `!resume`, **Then** that post is not treated as continuation of the closed session.
2. **Given** the runtime creates or resolves a session key for a bound Discord exchange, **When** that exchange is later reviewed by Phase 1 operators, **Then** the channel component of the runtime state is recoverable and consistent with the bound channel.

### Edge Cases

- Operator issues `!resume` when no prior `!stop` occurred.
- A peer posts in the bound channel after `!stop` but before `!resume`.
- The bot is mentioned in an unbound Discord channel by an otherwise authorized user.
- `thread_isolation` is enabled and a message arrives inside a thread rooted in the bound channel.
- The configured binding references a channel the bot can no longer resolve or access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Discord platform MUST support explicit binding to the intended Phase 1 channel surface so the peer-coordination runtime can be scoped to a known Discord channel.
- **FR-002**: When a Discord channel binding is configured, the platform MUST reject or ignore inbound messages from other channels rather than dispatching them into the active peer-coordination session.
- **FR-003**: The channel-binding behavior MUST compose with existing authorization checks; a user being authorized is not sufficient to bypass channel binding.
- **FR-004**: The Discord runtime MUST treat `!stop` from the operator as a session-closing control, aligned with `design/poc.md`.
- **FR-005**: After `!stop`, the runtime MUST prevent later peer messages from being interpreted as continuation of the closed session.
- **FR-006**: The Discord runtime MUST treat `!resume` from the operator as opening a new session after a stop, not as reviving the prior closed session.
- **FR-007**: The Discord runtime MUST preserve the operator-only session-opening rule from `design/poc.md`: a peer message in a closed or not-yet-open session MUST NOT implicitly open the session.
- **FR-008**: The implementation MUST preserve a stable channel identifier in runtime-visible state so downstream artifacts can populate the `channel_id` field expected by `specs/001-session-bundle-skeleton/spec.md`.
- **FR-009**: The implementation MUST keep session-boundary behavior coherent when Discord thread isolation is enabled; if thread-specific behavior differs from channel-level behavior, that difference MUST be explicit and reviewable.
- **FR-010**: If the configured Discord channel binding cannot be resolved or is no longer accessible, the runtime MUST fail safely rather than silently widening scope to other channels.
- **FR-011**: The slice MUST remain limited to Discord session controls. It MUST NOT introduce transcript export, pinned-rules pin synchronization, or session-bundle file generation.

### Key Entities *(include if feature involves data)*

- **Bound Discord Channel**: the configured Discord channel (or explicitly supported equivalent surface) that is allowed to participate in the Phase 1 runtime.
- **Session Control Command**: an operator-issued runtime command that changes session state, specifically `!stop` and `!resume` in this slice.
- **Runtime Session Boundary**: the Layer 1 distinction between an active session, a closed session, and a newly resumed session for the same bound Discord surface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a dry run, 100% of authorized mentions posted outside the configured bound Discord channel are blocked from entering the active peer-coordination runtime.
- **SC-002**: In a dry run, `!stop` always prevents continuation of the prior session, with no peer post after stop being routed into the closed session.
- **SC-003**: In a dry run, `!resume` always creates a new session boundary rather than attaching to the pre-stop session.
- **SC-004**: A reviewer inspecting runtime state or logs after a dry run can identify the bound channel used for the exchange without inferring it from off-record context.

## Assumptions

- Operator identity / authorization continues to use the existing cc-connect authorization surface; this slice does not redesign operator auth.
- Discord remains the only substrate in scope for this slice.
- Transcript export will be handled by a follow-on slice; this slice only has to preserve coherent runtime behavior that transcript export can later consume.
- Pinned rules remain operator-maintained and manually pinned for Phase 1; this slice does not automate those artifacts.
- Existing Discord thread-isolation support should be preserved or tightened, not removed.
