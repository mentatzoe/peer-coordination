# Implementation Plan: Session Bundle Init CLI

**Branch**: `007-session-bundle-init-cli` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-session-bundle-init-cli/spec.md`

## Summary

Add a repo-owned `peer-session init` CLI at the governance-repo root that
copies `observations/sessions/_template/` into a new session directory and
fills only the metadata that is mechanically knowable at session-open time.
The slice keeps session-bundle ownership outside `cc-connect`, uses a local
defaults file plus explicit override flags for repeated operator inputs, and
records pinned-rules provenance truthfully without forcing pre-session artifacts
to pretend the session is already complete.

## Technical Context

**Language/Version**: Python 3.14.x with standard-library-only implementation  
**Primary Dependencies**: `argparse`, `datetime`, `json`, `pathlib`, `shutil`, `subprocess`, `tomllib`, `unittest`  
**Storage**: Repo filesystem artifacts under `observations/sessions/`, JSON/Markdown bundle files, TOML defaults file  
**Testing**: `python3 -m unittest` targeted to the new repo-owned CLI modules  
**Target Platform**: Local operator / agent workstations running from the repository root  
**Project Type**: Repo-owned filesystem-first CLI utility  
**Performance Goals**: Initialize a bundle in well under 1 second on a typical local checkout; zero network or daemon dependency  
**Constraints**: Must not import `cc-connect`, must fail clearly on existing bundle directories, must preserve the `specs/001-session-bundle-skeleton` file contract, must omit `meta.json.transcript_source` until later completion steps, and must keep `pinned_rules_ref` truthful when git state is dirty  
**Scale/Scope**: One `init` command, one local defaults-file pattern, and bounded repo-root tests/documentation for the Phase 1 session-bundle workflow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I — Constitution Is Canonical**: Pass. The slice adds operator
  tooling around canonical repo artifacts; it does not relocate governance into
  transport code.
- **Principle II — Transport Is Plumbing, Not Governance**: Pass. The CLI is
  intentionally repo-owned and avoids `cc-connect` imports so Layer 1 plumbing
  stays separate from Layer 3 artifact authoring.
- **Principle III — Scratchpad First, Then Promotion**: Pass. The work is
  proceeding through the spec/plan artifact chain under `specs/007-*`.
- **Principle IV — Human Arbitration and Explicit Consent**: Pass. Operators
  still choose session IDs, defaults content, and any per-session overrides; the
  tool only removes mechanical copying/filling.
- **Principle V — Parallel Work Requires Explicit Ownership**: Pass. This is a
  bounded Codex-owned repo-utility slice with no overlapping implementation
  surface inside `cc-connect`.
- **Principle VI — Coordination Is Human-Legible, Not Over-Protocolized**:
  Pass. The CLI creates clearer artifacts and avoids hidden state or daemon-only
  behavior.

**Post-design check**: Still passes. The chosen design keeps bundle-init
mechanics in repo-local tooling, treats pinned-rules provenance honestly, and
does not redefine the session-bundle schema beyond the already-approved
pre-session omission of `transcript_source`.

## Project Structure

### Documentation (this feature)

```text
specs/007-session-bundle-init-cli/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── init-cli-behavior.md
└── tasks.md
```

### Source Code (repository root)

```text
peer-session                         # executable wrapper for the repo-owned CLI
tools/
└── peer_session/
    ├── __init__.py
    ├── cli.py
    ├── defaults.py
    ├── bundle_init.py
    └── git_refs.py

tests/
└── peer_session/
    ├── test_cli.py
    └── test_bundle_init.py

observations/
└── sessions/
    ├── _template/
    ├── README.md
    ├── defaults.example.toml
    └── defaults.toml               # local operator file, ignored from git
```

**Structure Decision**: Use a thin repo-root executable plus a small Python
package under `tools/peer_session/` so the CLI remains obviously repo-owned and
easy to extend with later artifact-first commands such as `validate`. Keep the
defaults artifacts next to the session-bundle surface they configure.

## Phase 0: Research Decisions

See [research.md](./research.md) for the decisions that harden this plan:

1. Implement `peer-session` as a repo-root Python CLI using only the standard
   library rather than adding another Go module or leaning on `cc-connect`.
2. Store repeated operator defaults in a local
   `observations/sessions/defaults.toml` file backed by a committed
   `defaults.example.toml` template.
3. Build new bundles by copying `_template/`, replacing only mechanically known
   values, preserving unresolved placeholders, and explicitly removing
   `transcript_source` from initialized `meta.json`.
4. Resolve `pinned_rules_ref` to a commit hash only when `pinned-rules/current.md`
   is cleanly represented by `HEAD`; otherwise fall back to an inline snapshot
   so provenance stays truthful.
5. Use isolated temp-directory tests around the Python library layer and the
   CLI wrapper to verify bundle creation, defaults overlays, provenance
   behavior, and rerun failures.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines the defaults overlay, init request,
  initialized bundle, and pinned-rules provenance entities.
- [contracts/init-cli-behavior.md](./contracts/init-cli-behavior.md) defines the
  operator-visible CLI contract for success, failure, and metadata population.
- [quickstart.md](./quickstart.md) captures the operator flow for preparing a
  defaults file and creating a pre-session bundle.

## Implementation Strategy

1. Add the repo-root `peer-session` wrapper and Python package under
   `tools/peer_session/`.
2. Introduce a committed defaults template plus a gitignored local
   `defaults.toml` path under `observations/sessions/`.
3. Implement deterministic bundle-copy and `meta.json` transformation logic that
   fills only session-open mechanical values and leaves later-session fields
   visibly pending.
4. Implement pinned-rules provenance resolution with commit-hash preference and
   inline fallback when the rules file is dirty or otherwise not safely
   referenceable by commit.
5. Add targeted `unittest` coverage around defaults loading, session-id
   validation, metadata rendering, and existing-directory failure cases.
6. Update operator documentation so bundle-init becomes the preferred path over
   manual `_template/` copying.

## Complexity Tracking

No constitutional violations or exceptional-complexity justifications are
currently required.
