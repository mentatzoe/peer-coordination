# Feature Specification: cc-connect Peer System Notice Isolation

**Feature Branch**: `codex-014-cc-connect-peer-system-notice-isolation`  
**Created**: 2026-05-12  
**Status**: Implemented  
**Input**: PC-76 / PC-7 follow-up after the failed Castor/Vigil smoke test.

## User Scenarios & Testing

### User Story 1 - Peer agents receive peer content, not bridge notices (Priority: P1)

During a parent-channel peer smoke, an allowlisted peer bot's final agent output must remain conversational input for the other runtime, but cc-connect's own operational notices must not enter that runtime as peer content.

**Why this priority**: PC-7 is blocked because queue/rate-limit/previous-processing notices authored by bot accounts were ingested by peer runtimes and created a feedback loop.

**Independent Test**: A Discord adapter test can simulate an allowlisted peer bot message whose message ID is recorded as a bridge system notice and verify that it is ignored, while a normal allowlisted peer bot message still dispatches.

**Acceptance Scenarios**:

1. **Given** an allowlisted peer bot message that is not a bridge system notice, **When** it arrives in the bound parent channel, **Then** it dispatches to the peer runtime without requiring a bot mention.
2. **Given** an allowlisted peer bot message whose ID was recorded as a bridge system notice, **When** it arrives in the bound parent channel, **Then** it is ignored before runtime dispatch.

---

### User Story 2 - Peer-bot pressure is silent and bounded (Priority: P2)

When an allowlisted peer bot posts while the target runtime is busy or rate-limited, cc-connect must not send queue/rate-limit/previous-processing replies back into the shared channel.

**Why this priority**: The live failure amplified because every guardrail reply became another allowlisted bot-authored inbound message.

**Independent Test**: Core engine tests can create busy/rate-limited peer-bot messages and verify that no platform reply is emitted for peer-bot guardrails.

**Acceptance Scenarios**:

1. **Given** an allowlisted peer bot message arrives while the session is busy and queue space exists, **When** the message is queued, **Then** no queued-message reply is sent.
2. **Given** an allowlisted peer bot message is rate-limited, **When** the engine handles it, **Then** no rate-limit reply is sent.
3. **Given** an allowlisted peer bot message arrives while the queue is full, **When** the engine rejects it, **Then** no previous-processing reply is sent.

---

### User Story 3 - Human/operator feedback remains intact (Priority: P3)

Human/operator users should continue to receive existing queue, rate-limit, and previous-processing feedback.

**Why this priority**: The fix must isolate peer-bot feedback loops without regressing normal operator usability.

**Independent Test**: Existing queue/rate-limit tests continue to assert human-visible replies.

**Acceptance Scenarios**:

1. **Given** a human/operator message arrives while the runtime is busy and queue space exists, **When** it is queued, **Then** the existing queued-message reply is sent.
2. **Given** a human/operator message is rate-limited, **When** the engine handles it, **Then** the existing rate-limit reply is sent.

## Edge Cases

- Discord sends the adapter's own bot message back through the gateway: existing self-bot filtering still wins.
- A peer bot's final response is chunked into multiple Discord messages: only message IDs recorded as bridge system notices are ignored.
- cc-connect restarts before old bridge notices are observed: old Discord messages remain subject to existing old-message filtering; this feature does not require cross-restart cache persistence.
- Future deployment splits peer bots across separate daemons: the in-process cache is sufficient for the PC-7 pilot daemon; cross-daemon notice isolation is a follow-up if deployment topology changes.

## Requirements

### Functional Requirements

- **FR-001**: Incoming core messages MUST carry enough provenance to identify whether the author is a platform bot.
- **FR-002**: Incoming core messages MUST carry enough provenance to identify whether the author is an explicitly allowlisted peer bot.
- **FR-003**: Discord MUST still dispatch normal allowlisted peer-bot messages without requiring mention text.
- **FR-004**: Discord MUST ignore messages whose platform message IDs are recorded as bridge system notices before peer-bot dispatch.
- **FR-005**: cc-connect MUST record Discord message IDs for system/guardrail notices it emits through the Discord adapter.
- **FR-006**: Core busy-queue handling MUST avoid sending queued-message notices for allowlisted peer-bot input.
- **FR-007**: Core rate-limit handling MUST avoid sending rate-limit notices for allowlisted peer-bot input.
- **FR-008**: Core queue-overflow handling MUST avoid sending previous-processing notices for allowlisted peer-bot input.
- **FR-009**: Core human/operator busy, rate-limit, and queue-overflow feedback MUST retain existing behavior.
- **FR-010**: The implementation MUST NOT use localized content-prefix filtering as the primary bridge-notice isolation mechanism.

### Key Entities

- **Inbound Message Provenance**: Metadata on `core.Message` describing platform bot authorship and allowlisted peer-bot authorship.
- **Bridge System Notice**: cc-connect-authored operational text such as queued-message, rate-limit, or previous-processing feedback.
- **System Notice ID Cache**: A bounded, time-limited Discord-side record of message IDs emitted as bridge system notices by any project in the daemon.
- **Interactive Session Queue**: Existing core queue used when an agent session is busy.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Focused core tests prove peer-bot busy/rate-limit/overflow paths emit zero platform replies.
- **SC-002**: Focused core tests prove human/operator busy/rate-limit feedback still emits platform replies.
- **SC-003**: Focused Discord tests prove recorded bridge system notice IDs are ignored even when authored by allowlisted peer bots.
- **SC-004**: Focused Discord tests prove normal allowlisted peer-bot final output still dispatches.
- **SC-005**: After rebuild and daemon restart, the PC-7 parent-channel smoke can be retried with zero bridge/system notices delivered into peer runtimes.

## Assumptions

- PC-7 pilot projects run in the same cc-connect daemon, so a process-wide Discord notice ID cache covers the immediate failure mode.
- The live smoke remains parent-channel-only; thread-mode repair is outside this slice.
- The first implementation can scope system notice marking to queue, rate-limit, and previous-processing notices, then migrate additional guardrails later if needed.
