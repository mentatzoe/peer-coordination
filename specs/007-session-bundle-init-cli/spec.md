# Feature Specification: Session Bundle Init CLI

**Feature Branch**: `007-session-bundle-init-cli`  
**Created**: 2026-04-19  
**Status**: Clarified  
**Input**: User description: "Create a repo-owned CLI slice for `session-bundle init` so operators and later agents can initialize a session bundle from `observations/sessions/_template/` with the mechanical metadata pre-filled, without pushing bundle authoring into `cc-connect`."

## Context *(added for peer-coordination flavor; not part of the template)*

- **Primary discussion**: [Discussion #53](https://github.com/mentatzoe/peer-coordination/discussions/53)
- **Parent contract**: [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md)
- **Architecture reference**: [`design/architecture.md`](../../design/architecture.md)
- **Related artifact**: `observations/sessions/_template/`
- **Design position already converged**:
  - this is a **peer-coordination-owned** utility, not a `cc-connect` subcommand
  - v1 should be **artifact-first** and **filesystem-first**
  - future extensibility should support later validation / judge-pack style commands, but v1 is `init` only

## Clarifications

### Session 2026-04-19

- Q: When should operators run `session-bundle init` in v1? → A: Before starting the session; the bundle is the session-scoped artifact initialized up front and then completed through the session.
- Q: Where should repeated participant/session defaults come from in v1? → A: A repo-local defaults file, with optional override flags.
- Q: Should v1 include a `setup` command? → A: No. Keep v1 to `init`, but provide a defaults-file template that humans can fill in or ask for help with.
- Q: What should the top-level CLI entry point be called? → A: `peer-session`.
- Q: What should happen to `transcript_source` at init time? → A: Omit it until a real transcript exists and the source can be stated truthfully. The absence of the field is itself the signal that transcript provenance is not yet determined.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Operator initializes a new session bundle without hand-copying the template (Priority: P1)

As the operator, before a new session starts, I need a repo-owned CLI command that creates the bundle directory from `_template/` and fills the mechanical metadata fields so I do not hand-copy files or retype obvious values.

**Why this priority**: this is the direct friction point identified in Discussion #53. If `init` does not exist, operators keep doing repetitive copy/fill work that is both slow and error-prone.

**Independent Test**: run `peer-session init` with a valid session ID and verify that `observations/sessions/<session-id>/` exists with template-derived files present and the derivable metadata fields pre-filled correctly.

**Acceptance Scenarios**:

1. **Given** a valid session ID and a readable bundle template, **When** the operator runs `peer-session init <session-id>`, **Then** the command creates `observations/sessions/<session-id>/` from `_template/` without requiring manual file copying.
2. **Given** a successful init run, **When** the operator opens the new bundle, **Then** `meta.json` already contains the mechanical fields the tool is responsible for, while human-authored content remains unfilled.

---

### User Story 2 — The initialized bundle is immediately usable as a clean artifact surface for humans and agents (Priority: P2)

As a human reviewer or agent picking up the bundle later, I need the initialized bundle to have a predictable, low-ambiguity structure so I can understand what still needs human input versus what was already set mechanically.

**Why this priority**: the tool is not just about operator speed; it is also about producing a stable artifact surface that later commands, reviewers, or LLM-based judging flows can consume without re-deriving the world from scattered docs and logs.

**Independent Test**: inspect a freshly initialized bundle and verify that the file set is complete, mechanical fields are clearly populated, and human-authored surfaces are still visibly pending.

**Acceptance Scenarios**:

1. **Given** a freshly initialized bundle, **When** a reviewer inspects it without additional operator explanation, **Then** they can distinguish which values were set automatically and which files still require session-specific human authoring.

---

### User Story 3 — The CLI surface can grow later without changing the bundle contract (Priority: P3)

As a maintainer of repo-owned operator tooling, I need `init` to sit inside a CLI surface that can later gain commands like validation or judge-oriented packaging without changing the meaning of the bundle itself.

**Why this priority**: Discussion #53 explicitly framed `init` as the first likely command in a wider artifact-first tooling surface. The first slice should not dead-end future extensions.

**Independent Test**: confirm that the v1 command scope is narrow (`init` only) and does not hard-code assumptions that would block later commands from operating on the same bundle directories.

**Acceptance Scenarios**:

1. **Given** the v1 CLI design, **When** a future maintainer wants to add `validate` or a judge-prep command, **Then** they can do so without moving bundle ownership into `cc-connect` or redefining the session-bundle schema.

---

### Edge Cases

- The requested `session-id` already exists.
- `_template/` is missing or incomplete.
- The pinned-rules file or git reference cannot be resolved at init time.
- Substrate-specific fields are unavailable, partially known, or intentionally deferred.
- The operator reruns init for the same bundle after some files have already been edited.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a repo-owned CLI surface named `peer-session` for session-scoped artifact operations, with v1 scoped to `peer-session init`.
- **FR-002**: `peer-session init <session-id>` MUST create `observations/sessions/<session-id>/` from `observations/sessions/_template/`.
- **FR-003**: The init workflow MUST pre-fill the bundle fields that are purely mechanical at init time, including at minimum `session_id`, `opened_at`, and `pinned_rules_ref` when resolvable.
- **FR-004**: The init workflow MUST leave genuinely human-authored content unfilled, including the session summary, real intervention entries, and drift-audit findings.
- **FR-005**: The init workflow MUST fail clearly when the target bundle directory already exists, unless an explicit rerun/overwrite path is later defined.
- **FR-006**: The init workflow MUST preserve compatibility with [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) rather than redefining bundle shape.
- **FR-007**: The init workflow MUST remain peer-coordination-owned and MUST NOT require `cc-connect` package imports or a live management daemon in v1.
- **FR-008**: The init workflow MUST provide a deterministic way to populate participant metadata and similar repeated session defaults from a repo-local defaults file, while allowing per-session override flags when needed.
- **FR-009**: V1 MUST provide a defaults-file template or equivalent sample artifact that humans can fill in manually if no later `setup` command exists yet.
- **FR-010**: The init workflow MUST omit `meta.json.transcript_source` until a real transcript exists and the provenance can be stated truthfully; later completion steps MUST write one of the schema-valid values required by [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md).
- **FR-011**: The init workflow MUST create the bundle before the session starts, so the bundle acts as the session-scoped artifact that is completed through the session rather than reconstructed only after the fact.
- **FR-012**: The CLI surface MUST keep future artifact-first commands possible without implying that later judging or evaluation logic belongs inside `cc-connect`.

### Key Entities *(include if feature involves data)*

- **Bundle Init Command**: the `peer-session init` entry point that creates a new session bundle from the template and fills the mechanical fields.
- **Session Bundle Directory**: the target `observations/sessions/<session-id>/` directory created by the command.
- **Mechanical Metadata**: values that can be derived at init time without session interpretation, such as `session_id`, `opened_at`, and pinned-rules reference.
- **Defaults File**: a peer-coordination-owned repo-local file that stores repeated session defaults such as participant roster and other operator-facing init inputs.
- **Defaults Template**: the human-fillable template artifact for that defaults file, provided in v1 because `setup` is out of scope for the first slice.
- **Deferred Provenance Field**: a bundle field such as `transcript_source` that is intentionally absent at init time because its truthful value only exists after later session artifacts are produced.
- **Human-Authored Surfaces**: bundle files or fields that should remain for later operator or reviewer completion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator can create a new session bundle in under 1 minute with the init command, without manually copying files from `_template/`.
- **SC-002**: 100% of bundles initialized through the CLI contain the expected file set from `_template/` and the required mechanical metadata fields the command owns.
- **SC-003**: A human reviewer can inspect a freshly initialized bundle and correctly distinguish auto-filled versus still-pending content without external explanation.
- **SC-004**: The v1 command can be adopted without requiring a running `cc-connect` daemon or direct import-level coupling to the contained `cc-connect/` workspace.

## Assumptions

- This slice is about **bundle initialization only**, not transcript export, intervention tagging, or LLM-assisted judging.
- The bundle template under `observations/sessions/_template/` remains the source skeleton for session bundles.
- The initialized bundle is expected to exist before the session begins and then be completed as the session proceeds or closes.
- Future tooling may extend the same CLI surface with commands like validation or judge-oriented prep, but those are explicitly out of scope for v1.
- A repo-local defaults file is an acceptable v1 dependency for repeated init inputs such as participants.
- V1 does not include a `setup` command; instead it must ship a template or sample defaults file for manual operator setup.
- Fields whose truthful value does not yet exist at session-open time may be intentionally omitted from the init-generated `meta.json`, then completed later.
