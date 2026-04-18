# Data Model: Transport MVP

## DesignatedPilotChannel

- **Purpose**: Identifies the channel where open-floor transport behavior is
  enabled for the pilot.
- **Fields**:
  - `channel_id`
  - `admitted_agents` — set of peer agent identities eligible for fanout
  - `is_active` — whether this designation currently applies to new routing
    decisions

## InterruptState

- **Purpose**: Represents whether outbound activity is currently permitted in
  the designated pilot channel.
- **Fields**:
  - `channel_id`
  - `state` — `active` or `stopped`
  - `set_by` — operator or allowlisted delegate identity
  - `set_at`
  - `resume_required` — whether explicit `!resume` is still outstanding

## EligibleAgent

- **Purpose**: Captures a peer agent that may receive open-floor fanout in the
  designated pilot channel.
- **Fields**:
  - `agent_id`
  - `channel_id`
  - `admitted` — whether the agent is currently admitted to the pilot channel
  - `last_outbound_message_id` — most recent outbound message used for
    self-loop suppression checks

## OutboundTransportEffect

- **Purpose**: Represents a transport-mediated side effect that may need
  suppression under `!stop`.
- **Fields**:
  - `channel_id`
  - `effect_type` — e.g. message send or other transport-mediated side effect;
    this is the cross-spec union point for additional suppressed effect types
    such as reactions
  - `state` — `pending`, `sent`, `suppressed`
  - `origin_agent`

## Relationships

- A **DesignatedPilotChannel** contains one or more **EligibleAgent** entries.
- An **InterruptState** belongs to a **DesignatedPilotChannel**.
- An **EligibleAgent** may attempt one or more **OutboundTransportEffect**
  actions while the pilot channel is active.
- **InterruptState** governs whether pending **OutboundTransportEffect** entries
  are allowed to proceed or must be suppressed.
