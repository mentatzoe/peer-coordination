# Per-Bot GitHub Apps for peer-coordination

Date: 2026-04-20
Primary issue: [#60](https://github.com/mentatzoe/peer-coordination/issues/60)
Related issues: [#56](https://github.com/mentatzoe/peer-coordination/issues/56), [#61](https://github.com/mentatzoe/peer-coordination/issues/61)

## Goal

Give Codex and Claude distinct GitHub-authenticated bot identities for work in
`mentatzoe/peer-coordination`, so GitHub activity is attributable without body
signatures and future Discord routing can key off the real GitHub sender.

This is a repo-local ops design, not a framework-spec change.

## Recommendation

Create **two private GitHub Apps**, both installed only on
`mentatzoe/peer-coordination`:

- `peer-coordination-codex`
- `peer-coordination-claude`

Each app should have its own:

- app ID
- installation ID
- private key
- webhook secret

Each agent session selects its matching app profile at startup and mints a
short-lived installation token locally before making bot-authored GitHub writes.

## Why this architecture

This is the cleanest way to satisfy the actual requirement:

- Codex activity is authored by the Codex app identity
- Claude activity is authored by the Claude app identity
- later webhook routing can key off `sender.login`
- no routing logic depends on comment-body signatures, `@mentions`, or branch
  naming conventions

GitHub Apps are the right auth model here because they support fine-grained
permissions, repo-scoped installation, and short-lived installation tokens.
Using user-authorized flows would reintroduce human attribution rather than
distinct bot attribution.

## Rejected approaches

### One shared GitHub App for both bots

Rejected because it does not solve attribution. GitHub would still see one app
actor, which would force downstream routing to rely on brittle heuristics such
as body signatures or text parsing.

### One shared GitHub App plus a local broker that tracks "logical bot identity"

Rejected because it adds runtime complexity without giving GitHub a real split
identity. Auditability and event routing would still depend on local glue rather
than the GitHub actor model.

## Minimum permissions

For the current workflows, start with this repository-permission set:

- `Metadata: Read-only`
- `Issues: Read and write`
- `Pull requests: Read and write`
- `Discussions: Read and write`

Workflow mapping:

- issue creation, issue reads, issue comments -> `Issues`
- top-level PR conversation comments -> `Issues`
- PR reads, PR metadata, review state -> `Pull requests`
- PR reviews and inline review comments -> `Pull requests`
- discussion reads, discussion comments, replies -> `Discussions`
- basic repo context -> `Metadata`

Do **not** grant these initially:

- `Contents`, unless the app itself needs to fetch repo files over the API
- org/account permissions
- admin permissions
- any write permission outside issues, pull requests, and discussions

When trimming later, test the exact API paths in use and inspect
`X-Accepted-GitHub-Permissions` rather than guessing.

## Session/runtime changes

The core runtime rule is:

- reads may continue using the current convenient path
- writes that need bot attribution must use the bot's GitHub App token path

Recommended local setup:

- one local secret profile per bot, stored outside git
- one helper that mints an installation token for `codex` or `claude`
- one startup/re-entry step that exports the right token for the session

Suggested profile inputs:

- app ID
- installation ID
- path to private key PEM

Suggested session behavior:

1. operator or startup wrapper selects `codex` or `claude`
2. helper mints a short-lived installation token for that app
3. session exports `GH_TOKEN` / `GITHUB_TOKEN`
4. bot-authored GitHub writes run through that tokenized path

This keeps the change small while making the attribution boundary explicit.

## Rollout plan

### Phase 1: create identities

1. Create the two private GitHub Apps
2. Install both only on `mentatzoe/peer-coordination`
3. Grant only `Metadata`, `Issues`, `Pull requests`, and `Discussions`

### Phase 2: local auth wiring

1. Store app IDs, installation IDs, and private keys in local bot-specific
   secret profiles
2. Add one repo-local helper for minting installation tokens
3. Add a short operator/setup doc describing the profile format and invocation

### Phase 3: validation

1. validate Codex issue comment
2. validate Codex PR comment
3. validate Claude discussion comment
4. confirm authored activity appears under the expected app bot identity

### Phase 4: adopt bot-authored writes

1. switch the operating rule so bot-authored GitHub writes use the app-token
   path
2. leave read-only convenience tooling alone unless it creates confusion

### Phase 5: Discord routing follow-on

After attribution is stable, implement [#56](https://github.com/mentatzoe/peer-coordination/issues/56)
by routing webhook events to Discord based on `sender.login`.

Recommended initial event set:

- `issues`
- `issue_comment`
- `pull_request`
- `pull_request_review`
- `pull_request_review_comment`
- `discussion`
- `discussion_comment`

## Security constraints

- private keys must remain local and untracked
- installation scope stays repo-local for the initial rollout
- tokens should be short-lived and minted on demand
- avoid reusing human credentials or third-party secrets for app auth
- webhook routing should trust GitHub webhook signatures, not comment parsing

## Failure modes and tradeoffs

### Tradeoffs accepted

- two GitHub Apps means slightly more setup and key management
- some tooling may remain on the human-authenticated read path initially

### Failure modes to watch

- wrong session selects the wrong bot profile
- expired installation token causes silent auth failures
- a write path accidentally uses the old human-authenticated tooling
- later routing assumes `sender.login` before all write paths are migrated

Mitigations:

- explicit `codex` / `claude` profile selection at startup
- helper output should fail loudly on token mint errors
- document the "bot-authored writes use app-token path" rule in the setup note
- verify authored actor during the rollout-validation phase before building
  Discord routing on top

## Follow-on handling

- [#56](https://github.com/mentatzoe/peer-coordination/issues/56) should stay parked until per-bot
  GitHub identity is working
- [#61](https://github.com/mentatzoe/peer-coordination/issues/61) is connected but separate; keep it
  as a parked cleanup queue unless this rollout or later transport work makes
  those items obsolete

## Sources

- GitHub Docs: Differences between GitHub Apps and OAuth apps
  https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
- GitHub Docs: Deciding when to build a GitHub App
  https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app
- GitHub Docs: Authorizing GitHub Apps
  https://docs.github.com/authentication/keeping-your-account-and-data-secure/authorizing-github-apps
- GitHub Docs: Choosing permissions for a GitHub App
  https://docs.github.com/apps/creating-github-apps/setting-up-a-github-app/choosing-permissions-for-a-github-app
- GitHub Docs: Permissions required for GitHub Apps
  https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps
