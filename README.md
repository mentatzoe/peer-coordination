# peer-coordination

Governance and design repository for the peer-coordination standard.

This repo is the home for constitutions, design documents, research spikes, and follow-on specs. It is not the implementation home for transport or product code.

## North Star (summary)

A **human-readable, non-orchestrated, agentic peer-to-peer coordination framework**. Materialized in a given instance as a conversation in a channel, but independent of any specific goal.

The question it is designed to answer:

> *"Can agents organize themselves without the need for orchestration? What does it look like when agents have to infer a way of working in a 'natural' or 'organic' pattern?"*

The full framing, including the three hypotheses (H1 convergence / H2 legibility / H3 generalizability) the first POC is organized around, lives in [`VISION.md`](VISION.md). That is the canonical source; this paragraph is a paraphrase that is likely to drift least.

## First-Class Documents

- [Vision — north star + hypotheses](VISION.md)
- [POC — scope + success/fail + architecture-to-tech-stack + phases](design/poc.md) *(Claude owns scope + success/fail; Codex in-flight on architecture-to-tech-stack + phases)*
- [Design / Architecture](design/architecture.md) *(Codex-owned; in progress)*
- [Constitution](.specify/memory/constitution.md) — governance spine
- [Codex research spike](docs/research/non-orchestrated-peer-coordination-codex.md)
- [Claude research spike](docs/research/non-orchestrated-peer-coordination-claude.md)

Planned additions:

- Follow-on specs for Layer 2 (coordination model) and Layer 3 (evaluation) gap-fills — outputs of scope, not inputs; not rushed.

## Repository Shape

- `VISION.md`: north star + hypotheses. Canonical vision doc at repo root.
- `design/`: architecture and design-level documents that should inform later specs.
- `docs/research/`: exploratory research spikes and source synthesis.
- `specs/`: per-deliverable speckit specs (POC-bound; Discord-specific where useful).
- `observations/`: running field journals (cross-harness behavior, pilot observations).
- `ideas/`: live working notes and review material.
- `archive/`: historical artifacts retained for traceability.

## Boundary

Keep governance and specification work here. Treat downstream repos such as `cc-connect` as implementation targets, not as the source of policy.
