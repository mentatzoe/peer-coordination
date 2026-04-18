# Archive: 001 Transport MVP Broad-Scope Draft

This note archives the earlier `001-transport-mvp` draft that was generated
before the scope/designation split was respected.

## Why Archived

The earlier draft incorrectly bundled several scopes that now belong in
different features:

- channel policy declaration belongs in `002-channel-policy-presence`
- agent-initiated emoji reaction emission belongs in
  `003-agent-initiated-reactions`
- approval-via-react and pinned-rules ingestion remain separate follow-on
  scopes rather than part of active `001`
- planning and task generation for `001` happened before review / clarify gates

## Archived Material

The superseded broad-scope work is preserved in git history on branch
`001-transport-mvp`:

- `87a6d34` `docs(spec): add Transport MVP feature specification`
- `257b7a4` `docs(plan): add Transport MVP planning artifacts`
- `a366545` `docs(tasks): add Transport MVP execution plan`

Those commits should be treated as reusable draft material only, not as the
authoritative active scope of `001`.

## Reuse Guidance

- Reuse open-floor, self-loop, and hard-interrupt wording from the archived
  draft when it still matches the narrowed `001` scope.
- Do not pull reaction emission, approval-via-react, pinned-rules ingestion,
  or channel policy declaration back into active `001`.
- If later planning resumes for `001`, restart from the narrowed spec and pass
  back through human review and `/speckit.clarify` before `/speckit.plan`.
