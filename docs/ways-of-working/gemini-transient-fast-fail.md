# Gemini Transient Fast-Fail Contract

**Status:** PC-60 implementation contract  
**Applies to:** Multica daemon runs using the direct Gemini runtime, plus OpenCode
runs whose terminal error stream exposes a Gemini transient failure.

## Problem

Gemini preview-tier capacity failures can arrive as normal-looking runtime
errors and then leave the task running until the broader agent timeout fires.
That turns a provider capacity blip into a long, silent run failure.

## Detection

The runtime treats the following Gemini-originating errors as
`gemini_transient`:

- `experiencing high demand`
- `model is currently overloaded`
- `[API Error: terminated]` / API-error `terminated`
- HTTP `503` or `529` from a Gemini / Google Generative Language context

For the direct Gemini runtime, the provider context is implicit. For OpenCode,
the status-code cases require a Gemini-looking model or message context so a
non-Gemini provider's 503/529 is not misclassified.

## On-Wire Behavior

Once the daemon sees the first transient pattern:

1. It forwards the upstream error text as the normal task error message.
2. It cancels the in-flight provider process immediately. The child process
   still gets the existing `WaitDelay` cleanup window, so the expected exit is
   within seconds and bounded by the current daemon process-kill behavior.
3. It reports the task through the existing failed-task path with:
   - `status = failed`
   - `error = <upstream Gemini message>`
   - `failure_reason = gemini_transient`
4. The existing server failure path posts the failure text to the issue or chat
   thread. It does not automatically flip the issue status; issue status remains
   governed by the agent/workspace workflow.
5. The failure is not eligible for Multica's same-agent auto-retry loop. A later
   rerun or fallback dispatch must be explicit at the issue/workflow layer.

This means "fast-fail" is a run-record transition plus the usual failure
comment, not an issue status flip.

## Fallback Boundary

If an OpenCode / oh-my-openagent layer handles a transient internally and
continues with a configured `fallback_models` chain, Multica should see the
eventual fallback output as the task result. If the transient escapes that layer
as a terminal OpenCode error, Multica classifies and fails it as
`gemini_transient` instead of letting the run sit until timeout.

For the current peer-coordination Castor runtime, the Multica agent is configured
as direct Gemini (`provider=gemini`, `model=gemini-3.1-pro-preview`), so the
daemon-side Gemini fast-fail path is the load-bearing path.
