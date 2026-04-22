# Feature Specification: Local TTS + Affect-Aware STT MCP for Operator ↔ Agent Voice

**Feature Branch**: `900-tts-local-mcp`
**Created**: 2026-04-20
**Status**: Draft
**Input**: A local, Apple-Silicon-hosted MCP surface that gives operator-directed Claude (and other peer agents reachable via this operator's harness) two capabilities they currently lack: (a) **outbound** text-to-speech so agent replies can ship as Discord voice-style attachments when voice-mode is on, and (b) **inbound** affect-aware transcription so voice messages from the operator arrive as per-chunk transcripts with combined text+prosody emotion labels instead of flat text. Scope is the operator's personal agentic-comms infrastructure (`9xx` reserved block per the convergence recorded in `ideas/tts-infra.md`); the cc-connect adapter path for peer bots (Dalgos / Vigil) and agent-to-agent voice are explicit follow-on non-goals.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`ideas/tts-infra.md`](../../ideas/tts-infra.md) — scratchpad capturing the 2026-04-19 convergence: outbound-first direction, opt-in voice-mode toggle, `reply.files = [audio.ogg]` wiring pattern, `9xx` reserved-block numbering convention, v1 scope and non-goals.
  - [`CLAUDE.md`](../../CLAUDE.md) — Collaborators & Harnesses section: Station (Claude, terminal-only cross-project), Dalgos/Vigil (peer bots running in cc-connect under this repo), operator = Zoe Lopez-Latorre.
- **Reserved-block scope**: `900-999` is reserved for **personal agentic-comms infrastructure** — slices that are operator ↔ agent ergonomics, not part of the peer-coordination standard itself, but plausibly **graduation-path** candidates (agent-to-agent voice is the forcing example: once operator ↔ agent voice is ergonomic, the peer-coord standard will want to say something about it). The `9xx` block is intentionally **not** a junk drawer; slices that would never graduate shouldn't land here. This slice is the anchor entry.
- **Tonight's validation evidence (2026-04-20)** — not speculation; load-bearing for the engine choices below:
  - **Outbound**: VoxCPM2-4bit served via `mlx-audio` (PR #641, `git+https://github.com/acul3/mlx-audio.git@feat/add-voxcpm2`) runs cleanly on this operator's Apple M4. Measured real-time factor ≈ 0.55, peak memory ≈ 3.6 GB during inference. Voice was designed via the engine's `--instruct` pure-positive prompt (**not** negative instructions — negative framing exhibited the Streisand effect and made outputs drift toward the things being negated). Voice "R3" is locked via a pinned instruct prompt. A known non-determinism channel — "content-influences-voice drift" — was observed on longer autoregressive generations and is codified as a guardrail in FR-007.
  - **Inbound**: A three-stage pipeline at the operator's local path (out-of-tree, not co-located with this repo): fsmn-vad chunks voice messages into utterances; SenseVoiceSmall produces a transcript plus a conservative categorical emotion per chunk; `iic/emotion2vec_plus_large` produces a dimensional affect vector (scores per chunk). A combiner pairs a per-chunk **text_valence** annotation with acoustic affect and emits one combined label per chunk from a fixed label space (see FR-011). Validated on two real clips from the operator: a compact three-register clip (~10 s per register) produced clean per-register labels (`aligned_negative`, `intense_aligned_positive`, `intense_aligned_negative`, `single_channel_neutral`); a longer clip fired `sarcasm_or_darkhumor` exactly where prosody said HAPPY@1.0 but the text said "kind of sarcastic."
  - **Known setup gotcha**: `iic/emotion2vec_plus_large`'s ModelScope cache ships a `requirements.txt` pinning `funasr==1.0.27`, which ModelScope auto-installs on every model load. `funasr 1.0.27` does **not** register `SenseVoiceSmall` as a model class (only `1.3.x` does), so loading SenseVoice breaks with `TypeError: 'NoneType' object is not callable`. Workarounds: overwrite the pinned `requirements.txt` in the ModelScope cache, or run SenseVoice and emotion2vec in **separate** Python environments (FR-017 codifies this).
- **Roadmap relationship**: this slice is **not** on [`ROADMAP.md`](../../ROADMAP.md) and does not block any roadmap workstream. ROADMAP.md tracks the peer-coordination standard and its baseline substrate / evaluation surface work; this slice lives in the reserved `9xx` block precisely because it's operator-personal infrastructure that may graduate later. Do not renumber into the 0xx sequence.
- **Staffing**: operator (Zoe) drives; Claude authors the spec and will author follow-on implementation slices; Codex is intentionally out of scope for this line of work per the `ideas/tts-infra.md` convergence.
- **Scope boundary (explicit)**:
  - **In scope (v1)**: the MCP surface (tools + voice-mode state), outbound synth path with a single local engine + pinned default voice, inbound transcript-with-affect handler with the per-chunk combined label taxonomy, guardrails (latency, attachment size, secrets deny-list, defensive cost cap), graceful-degradation behavior, known-gotcha setup documentation.
  - **Out of scope (v1, per scratchpad convergence)**: cc-connect outbound-audio adapter for Dalgos / Vigil (follow-on); agent-to-agent voice; cloned-voice options (default voices first); any VAD upgrade beyond fsmn-vad; cloud-TTS fallback (Mistral Voxtral / ElevenLabs) — deferred but the defensive cost-cap guardrail anticipates its eventual reintroduction; any evaluation or KPI-rollup layer for voice quality.
  - **Non-goals**: this slice does **not** modify the peer-coordination standard, does not alter `cc-connect/` transport semantics, and does not take any position on how peer bots should eventually speak. Those are graduation-path questions.

## User Scenarios & Testing *(mandatory)*

The "users" of this MCP are: the **operator** (sets voice-mode, sends inbound voice messages, receives outbound voice-style replies), and the **agent** (Station / Claude) calling the MCP tools as part of composing a reply or interpreting an inbound voice message. There are no other actors in v1 — peer bots (Dalgos, Vigil) and agent-to-agent voice are explicit follow-on non-goals.

### User Story 1 — Agent synthesizes a voice reply when voice-mode is on (Priority: P1)

As Station (the agent composing a reply to the operator on Discord), when voice-mode is on for this operator I call the MCP `synthesize` tool on my composed reply text and attach the resulting audio file to `reply.files` alongside the text body, so the operator receives the same substantive reply as both text and a voice-style attachment without any plugin change to the transport.

**Why this priority**: this is the core outbound loop the scratchpad identified as highest-ROI — agent replies currently carry zero affect signal, the operator has adopted texture markers as a workaround, and closing the outbound gap via a single local MCP call is the cheapest possible graduation path. Without this atom, nothing else in this spec matters.

**Independent Test**: with voice-mode on, have the agent call `synthesize("short reply text")`; verify (a) a file is produced at a deterministic path within the latency budget, (b) the file is a valid audio attachment playable by Discord, (c) the file size is under the 8 MB non-Nitro cap, and (d) attaching the file via the Discord plugin's `reply.files` parameter results in a voice-style attachment rendered to the operator.

**Acceptance Scenarios**:

1. **Given** voice-mode is on for this operator, **When** the agent calls `synthesize(text, voice="R3")` with a typical 1–2k character reply, **Then** the tool returns a filesystem path to a playable audio file within the latency budget from FR-006 and the file size is under the Discord non-Nitro attachment cap from FR-008.
2. **Given** the agent attaches the returned path to `reply.files = [path]` alongside the text body, **When** the reply ships via the Discord plugin, **Then** the operator receives both the text reply and a voice-style attachment rendered by Discord — no transport-side change required.
3. **Given** voice-mode is off for this operator, **When** the agent composes a reply, **Then** the agent does not call `synthesize` and the reply ships as text-only per the existing flow (voice-mode state is queryable via `get_voice_mode` and the agent respects it).

---

### User Story 2 — Operator toggles voice-mode on and off (Priority: P1)

As the operator, I call `set_voice_mode(on=True)` once from my agent session to opt into receiving voice replies, and `set_voice_mode(on=False)` to opt back out, so the mode is sticky across replies within a session without having to re-specify per-reply, and any agent in my harness can check the mode via `get_voice_mode()` before calling `synthesize`.

**Why this priority**: voice-mode is how the scratchpad's "default off, opt-in sticky" UX decision is expressed at the MCP layer. Without a queryable mode, either every reply carries voice (bad — slows non-substantive exchanges) or every reply is text (useless — defeats the feature). US1's acceptance depends on US2 being reliable.

**Independent Test**: call `set_voice_mode(True)`, then call `get_voice_mode()` and verify it returns `True`; call `set_voice_mode(False)`, then `get_voice_mode()` and verify `False`. Repeat across a simulated agent-process restart and verify persistence behavior matches FR-004.

**Acceptance Scenarios**:

1. **Given** voice-mode is off (default), **When** the operator calls `set_voice_mode(on=True)`, **Then** subsequent `get_voice_mode()` calls return `True` until the operator calls `set_voice_mode(on=False)`.
2. **Given** voice-mode is on, **When** the agent process restarts (the MCP server or the calling agent), **Then** the mode's persistence behavior is as specified in FR-004 — the operator does not have to discover the mode state empirically by observing whether replies arrive as voice.
3. **Given** voice-mode is on, **When** the agent checks `get_voice_mode()` before each reply and respects the result, **Then** the mode is consistently applied across replies in a session without per-reply operator intervention.

---

### User Story 3 — Operator sends a voice message and the agent receives transcript + per-chunk affect labels (Priority: P1)

As the operator, when I send a voice message to my agent on Discord, the plugin passes the audio file to the MCP's inbound transcript-with-affect handler, which chunks the audio, transcribes each chunk, computes dimensional acoustic affect per chunk, and emits per-chunk **combined text+prosody labels** from the taxonomy in FR-011, so the agent reads an emotion-annotated transcript instead of flat text and can respond with appropriate awareness of sarcasm, suppression, or aligned intensity.

**Why this priority**: the scratchpad flagged inbound as "good enough today" via texture markers, but tonight's validation showed the combined-label pipeline reliably detects cases that flat text cannot — specifically `sarcasm_or_darkhumor` where prosody is positive but text is negative (or vice versa). Shipping voice-mode outbound without also upgrading inbound leaves an asymmetry that the operator already corrects for manually. P1 alongside US1/US2 because without it, the feature is one-way and the operator still has to narrate affect in text.

**Independent Test**: hand the handler one of the validation clips from tonight (or an equivalent clip with a known register); verify the output contains (a) a transcript per chunk, (b) a dimensional-affect score per chunk, and (c) a combined label per chunk drawn from the FR-011 taxonomy. For the three-register validation clip, verify each register produces a label consistent with its intended register (intense-positive → `intense_aligned_positive`, intense-negative → `intense_aligned_negative`, neutral → `single_channel_neutral` or `aligned_*` of low-intensity polarity).

**Acceptance Scenarios**:

1. **Given** the operator sends a voice message with clearly-aligned prosody and text (e.g. audibly happy + text expresses happiness), **When** the inbound handler processes it, **Then** each chunk's combined label is one of `aligned_positive` / `aligned_negative` / `intense_aligned_positive` / `intense_aligned_negative` per the FR-011 taxonomy and the transcript is delivered alongside the labels.
2. **Given** the operator sends a voice message where prosody and text disagree (audibly happy + negative text, or audibly distressed + positive text), **When** the inbound handler processes it, **Then** the affected chunks are labeled `sarcasm_or_darkhumor` or `suppression_or_masking` respectively, per the validated behavior.
3. **Given** one channel is silent or uninformative (e.g. emotionally-flat text, no acoustic affect detectable), **When** the inbound handler processes it, **Then** the chunk is labeled `single_channel_<polarity>` or `ambiguous` per FR-011's fallback rules, and the handler does NOT invent an emotion it cannot evidence.

---

### User Story 4 — Synthesis fails and the reply degrades gracefully to text-only (Priority: P2)

As the operator, when outbound synth fails for any reason — the model is unavailable, the generated file would exceed the attachment cap, the text contains a deny-listed secrets marker, or the latency budget was blown — I still receive the agent's text reply with a small "(voice unavailable)" note appended, so conversation continuity is preserved and I'm informed that the voice channel dropped without the whole exchange failing.

**Why this priority**: P2 because US1/US2/US3 form the happy-path MVP. Graceful degradation is a correctness property on top of the MVP — if it's missing, the feature looks like an outage instead of a channel-drop, but it doesn't prevent the core loop from working on the happy path.

**Independent Test**: simulate each failure mode (model load error, oversized output, deny-listed text pattern, simulated timeout) and verify that (a) the agent receives a structured failure signal from `synthesize` rather than a silent hang, (b) the reply ships text-only with the "(voice unavailable)" note, and (c) no partial audio file is attached.

**Acceptance Scenarios**:

1. **Given** voice-mode is on and the synthesis engine fails to load (or the model process crashes mid-inference), **When** the agent calls `synthesize`, **Then** the tool returns a structured error (not a silent hang) within the latency budget, and the reply ships text-only with "(voice unavailable)" appended.
2. **Given** voice-mode is on and the composed reply matches a deny-listed secrets-bearing-context pattern per FR-009, **When** the agent calls `synthesize`, **Then** the tool refuses to synthesize, returns a structured "deny-listed context" error, and the reply ships text-only with "(voice unavailable)" — the audio is not produced and the secrets are not spoken.
3. **Given** voice-mode is on and the generated audio would exceed the 8 MB non-Nitro cap from FR-008, **When** the tool produces the file, **Then** it returns a structured "oversize" error rather than shipping an unplayable attachment, and the reply ships text-only with "(voice unavailable)."

---

### User Story 5 — Operator reproduces the known-gotcha setup without hitting the `funasr` pin trap (Priority: P3)

As the operator re-provisioning the inbound pipeline on a new machine (or re-initializing after a ModelScope cache wipe), I follow the spec's setup note about the `emotion2vec_plus_large` → `funasr==1.0.27` pin conflict and avoid the trap where loading SenseVoiceSmall breaks because `funasr 1.0.27` doesn't register it, so I don't re-discover the trap empirically each time.

**Why this priority**: P3 because it's a setup / reproducibility concern, not a runtime correctness concern. The feature still works once the trap is navigated; documenting it prevents hours lost on a first re-provision.

**Independent Test**: provision a fresh ModelScope cache, load `emotion2vec_plus_large` (which triggers the pinned-`funasr` auto-install), then attempt to load SenseVoiceSmall in the same environment; verify the failure mode matches FR-017's documentation (`TypeError: 'NoneType' object is not callable` on SenseVoice init). Apply one of the documented workarounds from FR-017 and verify the pipeline loads.

**Acceptance Scenarios**:

1. **Given** the operator is re-provisioning the inbound pipeline, **When** they read this spec's FR-017 and the corresponding setup note, **Then** they know before starting that running SenseVoice and emotion2vec in the same Python environment requires either overwriting the pinned `requirements.txt` in the ModelScope cache OR using separate environments, and they don't discover it by hitting the `TypeError`.
2. **Given** the operator chooses the separate-environments workaround, **When** they run the pipeline, **Then** the combiner step (which needs outputs from both models) still produces valid per-chunk combined labels per the FR-011 taxonomy because label combination operates on the emitted outputs, not on in-process model state.

---

### Edge Cases

- **Voice-mode on but input text is empty or whitespace-only**: `synthesize` MUST refuse to produce an empty audio file and MUST return a structured error rather than a zero-byte attachment.
- **Voice-mode on but input text is extremely long** (well past the typical 1–2k char reply): synthesis MUST either complete within the latency budget or return a structured "over-budget" error so the reply can degrade per US4; it MUST NOT stream a partial file that truncates mid-word. Long generations are also the regime where the "content-influences-voice drift" guardrail from FR-007 matters most.
- **Inbound voice message is silence or sub-VAD-threshold noise**: the handler MUST emit an empty transcript (or a clearly-marked "no speech detected" result) rather than fabricating content.
- **Inbound voice message contains multiple speakers**: v1 does NOT diarize; the handler treats all speech as the operator's. If the operator forwards audio from another source and expects speaker attribution, that's out of scope for v1.
- **Voice-mode is toggled mid-reply composition**: the mode that applies is the one observed at the `synthesize` call time, not at reply-composition start time. Agents SHOULD check `get_voice_mode()` close to the synth call.
- **Simultaneous synth calls from parallel agents**: v1 assumes a single operator / single harness; concurrent calls are acceptable as long as the MCP serializes access to the model (FR-006's latency budget is per-call, not per-user).
- **Deny-listed secrets pattern appears in only part of a long reply**: `synthesize` MUST refuse the whole reply rather than attempting partial synthesis; the graceful-degradation path from US4 covers operator communication.

## Requirements *(mandatory)*

### Functional Requirements

#### MCP surface

- **FR-001**: The MCP server MUST expose a `synthesize(text: string, voice?: string) -> path` tool that returns a filesystem path to a playable audio file suitable for attachment via the Discord plugin's `reply.files` parameter. `voice` is optional; if omitted, the server uses the pinned default voice (see FR-007). The returned path MUST be deterministic enough that a caller can attach it immediately without polling for file existence.
- **FR-002**: The MCP server MUST expose a `set_voice_mode(on: bool)` tool that sets the sticky voice-mode state for the operator.
- **FR-003**: The MCP server MUST expose a `get_voice_mode() -> bool` tool that returns the current sticky voice-mode state.
- **FR-004**: Voice-mode state MUST persist across MCP-server restarts and across calling-agent restarts for the same operator identity. State location is an implementation detail, but the persistence guarantee is a workflow-level invariant: the operator must not have to re-toggle after a process restart.
- **FR-005**: The MCP server MUST expose an inbound transcript-with-affect handler (surface shape — stdio MCP tool, MCP resource, or CLI callable from the Discord plugin adapter — is an implementation choice, but the behavior is required) that takes an audio file reference from the operator's Discord voice message and returns, per VAD chunk: `{chunk_index, start_time, end_time, transcript, sensevoice_emotion, acoustic_affect_scores, text_valence, combined_label}` where `combined_label` is drawn from the FR-011 taxonomy.

#### Outbound synth engine

- **FR-006**: The outbound synth path MUST complete within a **<3 s latency budget** for a typical 1–2k character reply on the operator's Apple M4. The budget is wall-clock from `synthesize` call entry to path return. Exceeding the budget triggers the US4 graceful-degradation path and MUST return a structured "over-budget" error rather than blocking the reply indefinitely.
- **FR-007**: The outbound synth path MUST use the VoxCPM2-4bit engine served via `mlx-audio` (validated tonight at RTF ≈ 0.55, peak memory ≈ 3.6 GB on this operator's M4). The default voice MUST be voice "R3", pinned via a `--instruct` **pure-positive** prompt — negative instructions MUST NOT be used (the Streisand effect was observed and codified as non-use). The content-influences-voice drift observed on longer autoregressive generations is a known non-determinism channel and MUST be surfaced as a guardrail: v1 does NOT attempt per-call voice consistency verification beyond pinning the instruct prompt, but the spec acknowledges the drift so consumers (and follow-on slices) do not treat the voice as byte-stable across arbitrary content. The "R3" pin and the pure-positive prompt convention MUST be documented in an implementation-adjacent note so they survive any re-provisioning.
- **FR-008**: The outbound synth path MUST enforce the Discord **non-Nitro 8 MB attachment cap** at synth time. If the generated file would exceed the cap, the tool MUST return a structured "oversize" error and MUST NOT return a path to an unplayable attachment. The check is pre-attachment, not post-hoc.
- **FR-009**: The outbound synth path MUST enforce a **secrets-bearing-context deny-list** on the input text before synthesis. If the text matches a deny-listed pattern (e.g. API keys, tokens, known secret-shaped strings), the tool MUST refuse to synthesize, return a structured "deny-listed context" error, and the reply MUST degrade to text-only per US4. The exact deny-list patterns are an implementation concern (follow-on slice may expand), but the gate MUST exist in v1.
- **FR-010**: The outbound synth path MUST apply a **defensive per-day cost cap** configurable by the operator. Local inference is free, so the cap is effectively inert in v1; however, the guardrail exists for the plausible graduation where a cloud-TTS fallback (e.g. Mistral Voxtral) is reintroduced via a follow-on slice. When the cap is hit, synth MUST refuse per US4's graceful-degradation path. The cap defaults to "effectively unlimited" in v1.

#### Inbound transcript-with-affect pipeline

- **FR-011**: The inbound handler's `combined_label` field MUST be drawn from the following fixed taxonomy (validated on two real operator clips tonight):
  - `aligned_positive` — text and prosody agree on positive valence.
  - `aligned_negative` — text and prosody agree on negative valence.
  - `intense_aligned_positive` — both channels agree on positive valence AND text explicitly names the emotion AND acoustic confidence is high.
  - `intense_aligned_negative` — same as above, negative polarity.
  - `sarcasm_or_darkhumor` — negative text + positive prosody.
  - `suppression_or_masking` — positive text + negative prosody.
  - `single_channel_<polarity>` — one channel is silent / uninformative; fall back to the other (`<polarity>` ∈ `{positive, negative, neutral}`).
  - `ambiguous` — catch-all for cases that don't match any of the above.

  The taxonomy is closed in v1: the handler MUST NOT emit labels outside this set. Extension to new labels is a follow-on slice.
- **FR-012**: The inbound handler MUST perform VAD chunking via **fsmn-vad** (v1-locked; no VAD upgrade per non-goals). Each chunk is labeled independently — multi-chunk aggregation (e.g. whole-message mood) is out of scope for v1.
- **FR-013**: The inbound handler MUST run **SenseVoiceSmall** for per-chunk transcript plus conservative categorical emotion, and **`iic/emotion2vec_plus_large`** for per-chunk dimensional acoustic affect scores. Both outputs MUST be available to the combiner step before a `combined_label` is emitted. If either model is unavailable, the handler MUST emit an explicit failure signal per FR-018 rather than emitting a partial record.
- **FR-014**: The combiner step MUST produce exactly one `combined_label` per chunk by pairing a **per-chunk `text_valence` annotation** (derived from the SenseVoice transcript via a lightweight valence classifier whose exact implementation is deferred to the follow-on plan) with the acoustic affect vector. The specific combination rules are an implementation detail of the follow-on plan, but the output space is locked to FR-011 and the two validated divergence cases (`sarcasm_or_darkhumor`, `suppression_or_masking`) MUST be producible by the combiner.
- **FR-015**: The inbound handler's output MUST include, for each chunk, enough raw signal for a downstream consumer to disagree with the `combined_label` and re-derive it: the transcript, the SenseVoice categorical emotion, the emotion2vec score vector, and the `text_valence` annotation MUST all be present on the chunk record.

#### Graceful degradation and observability

- **FR-016**: On any outbound-synth failure (model unavailable, latency budget exceeded per FR-006, attachment cap exceeded per FR-008, deny-listed context per FR-009, cost cap hit per FR-010), the agent MUST ship the reply as text-only with a small literal marker **"(voice unavailable)"** appended, so the operator is informed that the voice channel dropped without the exchange failing. The exact marker text is fixed in v1 (not parameterized) so the operator can recognize it at a glance.
- **FR-017**: The spec MUST document the **ModelScope `funasr` pin gotcha** so the operator (or any peer re-provisioning the inbound pipeline) does not re-discover it empirically: `iic/emotion2vec_plus_large`'s ModelScope cache ships a `requirements.txt` pinning `funasr==1.0.27`, which ModelScope auto-installs on every model load; `funasr 1.0.27` does not register `SenseVoiceSmall` as a model class (only `1.3.x` does), causing SenseVoice init to fail with `TypeError: 'NoneType' object is not callable`. Supported workarounds in v1: (a) overwrite the pinned `requirements.txt` in the ModelScope cache to allow `funasr>=1.3.0`, or (b) run SenseVoice and emotion2vec in separate Python environments and feed outputs to the combiner out-of-process. The implementation plan MUST choose one of these and document the choice; both are acceptable from a spec perspective.
- **FR-018**: Both outbound and inbound paths MUST surface non-silent failures. A caller MUST NOT observe the handler hang indefinitely, emit a partial record, or silently drop a chunk. Failure signals are structured (distinct from success returns) so the agent can distinguish them and degrade per FR-016.

### Key Entities

- **Voice-mode state** *(workflow-level; persistent per-operator)*: boolean, default `false`. Sticky across MCP-server and calling-agent restarts. Readable via `get_voice_mode`, writable via `set_voice_mode`.
- **Outbound synth engine** *(v1-locked)*: VoxCPM2-4bit via `mlx-audio` (PR #641 branch pinned). Default voice "R3" pinned via `--instruct` pure-positive prompt. Known non-determinism channel: content-influences-voice drift on long generations.
- **Inbound pipeline** *(v1-locked)*: fsmn-vad chunker → SenseVoiceSmall transcript+categorical → emotion2vec_plus_large dimensional affect → combiner. Per-chunk output carries transcript + raw signal + one `combined_label` from the FR-011 taxonomy.
- **Combined label taxonomy** *(closed set, FR-011)*: 8 labels (`aligned_positive`, `aligned_negative`, `intense_aligned_positive`, `intense_aligned_negative`, `sarcasm_or_darkhumor`, `suppression_or_masking`, `single_channel_<polarity>`, `ambiguous`). v1 does not extend.
- **Guardrail budgets** *(v1-locked numbers)*: <3 s outbound synth latency (FR-006); 8 MB Discord non-Nitro attachment cap (FR-008); secrets-bearing-context deny-list (FR-009); defensive per-day cost cap (FR-010, effectively inert in v1 because local inference is free).
- **Failure signal** *(structured return)*: distinct from success. Carries a reason code (model-unavailable, over-budget, oversize, deny-listed, cost-cap, empty-input). Triggers the FR-016 graceful-degradation path.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With voice-mode on, 95% of outbound replies to the operator arrive as both a text reply and a voice-style attachment in the same Discord message (the other 5% falls to the graceful-degradation path and arrives as text-only with the "(voice unavailable)" marker).
- **SC-002**: Outbound synth completes within the <3 s latency budget on 95% of typical (1–2k character) replies on the operator's Apple M4, measured over at least 20 representative replies.
- **SC-003**: Inbound voice messages produce a per-chunk `combined_label` from the FR-011 taxonomy for 100% of chunks emitted by fsmn-vad (no chunk is silently dropped; chunks with insufficient signal receive `ambiguous` or `single_channel_<polarity>` rather than no label).
- **SC-004**: On the three-register validation clip (intense-positive / intense-negative / neutral, ≈10 s each), the handler emits one label per register consistent with its intended register (intense-polarity registers receive `intense_aligned_*`; neutral receives `single_channel_neutral` or a low-intensity aligned label) on re-runs that reproduce tonight's validation result.
- **SC-005**: On a clip where prosody and text disagree (validated tonight), the handler emits `sarcasm_or_darkhumor` or `suppression_or_masking` on the divergent chunk(s), matching the pattern of tonight's long-clip validation.
- **SC-006**: No synth failure results in the operator receiving an empty, broken, or hung reply: 100% of failure scenarios from US4 result in a text-only reply with the "(voice unavailable)" marker within the FR-006 latency budget.
- **SC-007**: A peer re-provisioning the inbound pipeline from the spec alone (without hitting tonight's `TypeError` empirically) applies one of FR-017's documented workarounds and loads SenseVoice + emotion2vec successfully on first attempt — measured by whether the peer reports the `funasr` pin trap as "hit" or "avoided-via-spec-note" on the first provision.
- **SC-008**: The operator does not have to re-toggle voice-mode after an MCP-server restart or a calling-agent restart: voice-mode persistence is verifiable by toggling on, restarting, and observing that `get_voice_mode()` still returns `true` without re-toggling.

## Assumptions

- The operator's harness is the **Claude Code Discord plugin** (or equivalent) whose `reply` tool already accepts `files: string[]` — outbound synth is wired via `reply.files = [path]` without any plugin change. This assumption holds per the scratchpad; if the plugin contract changes, this assumption is re-visited in a follow-on slice.
- **Station** (terminal Claude / personal-agent surface) is the sole v1 consumer. Dalgos / Vigil (cc-connect peer bots) are explicit non-goals for v1 — the cc-connect outbound-audio adapter is a follow-on slice. This matches the scratchpad's convergence and the CLAUDE.md Collaborators & Harnesses mapping.
- The operator runs a single harness at a time; concurrent synth calls from parallel agents are rare in practice. The MCP MAY serialize access to the model rather than support true concurrency in v1.
- Local inference is free, so the FR-010 cost cap is effectively inert in v1. The guardrail is in place because a cloud-TTS fallback (Mistral Voxtral was the scratchpad's default-then-deprioritized choice) is a plausible follow-on and bolting cost controls on later is more error-prone than specifying them now.
- The operator's Apple M4 hardware is the reference substrate. VoxCPM2-4bit + `mlx-audio` performance characteristics (RTF ≈ 0.55, peak memory ≈ 3.6 GB, <3 s latency on typical replies) are validated on that specific hardware and do not generalize to other substrates without re-measurement. This is consistent with the slice's `9xx` reserved-block posture as operator-personal infrastructure.
- The `funasr` pin gotcha from FR-017 is assumed stable as of 2026-04-20. If ModelScope updates the pinned requirement upstream, the gotcha may resolve itself and FR-017's documentation becomes historical rather than load-bearing. The spec does not attempt to predict the upstream fix timeline.
- The combined-label taxonomy in FR-011 is assumed stable enough for v1 based on two real-clip validations. Taxonomy extension is a follow-on slice; v1 does not extend.
- The default voice "R3" is assumed acceptable by the operator (locked via pinned instruct prompt tonight). Voice cloning and alternative default voices are explicit non-goals for v1.
- The "content-influences-voice drift" observed in longer generations is assumed to be within acceptable bounds for typical 1–2k character replies; characterizing or mitigating the drift in longer generations is a follow-on concern.

## Dependencies

- **Upstream (landed / external)**:
  - `mlx-audio` (PR #641 branch): `pip install "git+https://github.com/acul3/mlx-audio.git@feat/add-voxcpm2"` — the VoxCPM2 integration path used tonight. Pinning to the PR branch (not mainline `mlx-audio`) is a deliberate v1 choice until the PR merges upstream.
  - `iic/SenseVoiceSmall` (ModelScope) — inbound transcript + categorical emotion.
  - `iic/emotion2vec_plus_large` (ModelScope) — inbound dimensional affect. Carries the `funasr` pin gotcha per FR-017.
  - `fsmn-vad` (ModelScope) — inbound VAD chunker. No upgrade in v1.
  - The operator's local pipeline scripts (at an out-of-tree path documented in the implementation plan) are the prototype that informed this spec — `affect_timeline.py` (chunk + transcribe + score), `citl_combine.py` (label combiner). The spec does not vendor those scripts into this repo; they are validation artifacts that motivate the v1 shape.
- **Downstream (follow-on, not blocked on this slice)**:
  - cc-connect outbound-audio adapter for Dalgos / Vigil (reserved-block sibling, not yet specced) — would consume the same MCP surface for peer-bot replies. Not in v1.
  - Cloud-TTS fallback (Mistral Voxtral or similar) — defensive cost-cap from FR-010 anticipates this; no slice filed yet.
  - Agent-to-agent voice — graduation-path candidate for the peer-coordination standard itself, intentionally downstream.
- **Constitutional / repo-governance**:
  - This slice is **not** a peer-coordination standard change. It does not amend the constitution, does not alter `cc-connect/` transport semantics, and does not appear on [`ROADMAP.md`](../../ROADMAP.md). It lives in the `9xx` reserved block precisely because it's operator-personal infrastructure with a plausible graduation path, and the 9xx posture is codified in `ideas/tts-infra.md` rather than in the constitution. Governance touchpoint: if agent-to-agent voice later becomes a peer-coord standard concern, that promotion goes through the normal scratchpad → constitution / spec path — it does not happen by extending this slice in place.
