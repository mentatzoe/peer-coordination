# TTS infra scratchpad — "Claude talks back" via Voxtral + Discord voice attachments

**Status**: scratchpad capture, 2026-04-19, not yet a spec.
**Scope**: operator's personal setup — meta, not framework (sibling framing to issue #56 on per-agent notification routing).
**Authors**: Zoe (operator) + Claude (Station). Kept in `ideas/` — not an open discussion; Codex is intentionally *not* in scope for this line of work yet.

## Problem

Voice is asymmetric. Zoe speaks → Discord plugin auto-transcribes → agents see clean text. Agents reply with only text — zero affect signal. Zoe has adopted texture markers (`hah` / `T-T` / `😛` / self-corrections, and sometimes narrating affect explicitly, e.g. *"I am saying haha out loud so you can see I'm laughing"*) as a workaround. The outbound direction has the bigger gap; inbound is "good enough" today.

## Convergence from the 2026-04-19 thread

### Direction — **outbound first (TTS)**

Inbound (Whisper transcripts) carries ~80% of Zoe's affect signal already via texture markers + pattern-matching. Outbound carries 0%. Highest ROI from a single pipeline is `agent reply → audio`. Inbound upgrade (Whisper → SenseVoice for emotion-aware transcripts) is a deferred second slice.

### TTS engine — **Voxtral via Mistral API** (with local as Plan B)

- **Voxtral** (Mistral, March 2026, 4B, open weights, ~68% preference wins vs ElevenLabs). Zoe is specifically interested in seeing Mistral's work.
- API cost: ~$0.016 / 1k chars → ~$3 / day at heavy use → ~$90 / month. Cheaper than ElevenLabs for better output. Reasonable tier.
- Self-host on the M4 is possible but tight (4B params, needs 4-bit quantisation to fit, inference likely 0.5–1× real-time). Don't fight the hardware when the API is this cheap.
- Alternatives if cost/privacy flips the calculus later: **Chatterbox** (~500M, emotion-exaggeration knob, fits comfortably on M4); **Kokoro** (~82M, minimum-footprint fallback); **Bark** for character voices / non-speech sounds.

### Wiring — **`reply.files = [audio.ogg]` via the native Discord plugin**

Zero plugin change for Station. The Claude Code Discord plugin's `reply` tool already supports `files: string[]`. Flow:

1. Agent composes the text reply.
2. If voice-mode is on, agent calls a local MCP tool: `synthesize_tts(text) -> /tmp/reply-<uuid>.ogg`.
3. Attach via `reply.files = [path]` alongside the text body.
4. Discord renders it as a voice-message-style attachment.

For Dalgos/Vigil (cc-connect), slightly more work: an outbound middleware hook that synthesizes and attaches before the message ships. Separable; v1 is Station-only.

### UX — **opt-in voice-mode toggle**

Voice-mode off by default so existing text flows aren't slowed. Operator sets `voice-mode on` once; sticky until `voice-mode off`. Per-user state in the MCP.

## v1 spec scope (when we run `/speckit.specify`)

**Slice name**: let speckit assign. Note: slot `008` is already owned by Dalgos's `drift-audit-workflow` per `ACTIVE-SLICES.md` — the TTS slice will land at `009-*` or later depending on what's claimed by then.

**Surface**: small MCP server (`tts-local` working name) exposing:
- `synthesize(text, voice?, emotion?) -> path`
- `set_voice_mode(on)` / `get_voice_mode() -> bool`

**Engine config**:
- Default: `mistral-voxtral` (needs `MISTRAL_API_KEY`).
- Fallback: `local-chatterbox` (pulls weights on first run, caches under `~/.cache/tts-local/`).

**Non-goals in v1**:
- Inbound SenseVoice upgrade (deferred to a second slice, e.g. `009-stt-with-emotion`).
- cc-connect adapter work for Dalgos/Vigil outbound audio — follow-on, not v1.
- Agent-to-agent voice (Dalgos talking to Vigil). Keep v1 scoped to operator ↔ agent.

**Guardrails**:
- **Latency budget**: <3s synth time for typical 1–2k char reply; enforce at MCP layer.
- **Cost budget**: soft per-day cap, refuse above it rather than silently overspend.
- **Privacy**: text is sent to Mistral's API — acceptable for the working channel but explicit deny-list for any secrets-bearing context.
- **Discord attachment cap**: 8 MB for non-Nitro, 25 MB Nitro. A ~2-minute mono 32 kbps `.ogg` is ~480 KB, well under. Still enforce at synth time.

## Open questions (flagged but not blocking)

- Agent-initiated voice vs operator-controlled toggle: should the agent *decide* per-reply whether voice adds value (e.g., only for substantive / non-procedural content), or is it strictly a sticky operator toggle? Current lean: sticky operator toggle for v1, revisit once we feel the friction.
- Voice cloning: Voxtral can clone from 3s of audio. Do we want a cloned-voice option, or ship with default Mistral voices first? v1 default voice, cloning as follow-on if Zoe wants it.
- Error surfacing: if synth fails (API outage, budget hit), does the reply ship text-only with a small "(voice unavailable)" note, or fail loudly? Lean: ship text-only with a subtle note — graceful degradation.

## Next action

Pick up tomorrow with `/speckit.specify` in the peer-coord repo to graduate this into a formal spec. Until then, iterate in `#1488717251212476569` Discord thread between Zoe + Claude (Station). Not looping Codex in for this line — it's personal-setup infrastructure, not coordination-standard work.
