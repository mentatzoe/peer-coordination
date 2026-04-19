# cc-connect in peer-coordination

This directory is the contained implementation-facing transport workspace for
the current peer-coordination POC.

## What this is

- Source fork lineage: `mentatzoe/cc-connect`
- Upstream lineage: `chenhg5/cc-connect`
- Import mode: history-preserving subtree import into `cc-connect/`
- Role here: Layer 1 transport/session plumbing for the POC

## What this is not

- Not the source of governance or policy
- Not the canonical home of `VISION.md`, `design/architecture.md`,
  `design/poc.md`, or the constitution
- Not permission to redefine coordination policy by implementation drift alone

## Working boundary

Use this workspace for transport-side implementation work: Discord binding,
interrupt handling, transcript export, adapter work, and other runtime plumbing
owned by the POC transport slice.

Use the repo root for governance and design work: constitutions, canonical
design docs, specs, roadmap, and review discussions.

## Re-entry path

For the current relocation slice, the durable entry path is:

`ROADMAP.md` -> discussion `#41` -> discussion `#42` -> relocation commits
