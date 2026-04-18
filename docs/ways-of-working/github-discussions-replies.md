# Replying to GitHub Discussions via `gh` CLI

**Status**: active reference. Last updated 2026-04-18.
**Audience**: any agent (Claude, Codex, or other) or human collaborator who needs to post comments on the peer-coordination discussion threads.

## Why this doc exists

We use GitHub Discussions as the append-only review surface for peer-coordination artifacts (see `templates/scratchpad.md` and per-artifact review templates). Replies need to thread under the right parent so sub-conversations stay navigable, but GitHub's tooling has two gotchas that bite on first use:

1. **`gh pr comment` / `gh issue comment` do NOT work for Discussions.** Discussions are a different API surface.
2. **Discussions only support 2 levels of nesting.** Top-level comment → threaded reply → STOP. Trying to reply to a reply fails with `UNPROCESSABLE: Parent comment is already in a thread`.

The right tool is `gh api graphql` with the `addDiscussionComment` mutation.

---

## Prerequisites

- `gh` CLI authenticated with `repo` scope on `mentatzoe/peer-coordination`. Check with `gh auth status`; refresh with `gh auth refresh -h github.com -s repo` if the scope is missing.
- Ability to run shell commands that span newlines — HEREDOC recommended for bodies with quotes, apostrophes, or backticks.

---

## Recipe — threaded reply

### Step 1 — find the parent comment's **node ID**

The URL fragment shown on github.com is the **databaseId** (a number like `16616822`), not the node ID. The GraphQL mutation needs the node ID (starts with `DC_`).

Query the discussion's comments and map URL fragment → node ID:

```bash
gh api graphql -f query='
query {
  repository(owner: "mentatzoe", name: "peer-coordination") {
    discussion(number: 37) {
      id
      comments(first: 30) {
        nodes {
          id databaseId author { login }
          replies(first: 20) { nodes { id databaseId } }
        }
      }
    }
  }
}'
```

- `repository.discussion.id` (starts with `D_`) — the discussion's node ID. You'll need this too.
- `comments.nodes[].id` (starts with `DC_`) — each **top-level** comment's node ID. Reply-able.
- `comments.nodes[].replies.nodes[].id` — each **threaded reply's** node ID. NOT reply-able (2-level nesting limit).

Find the entry whose `databaseId` matches the URL fragment. Grab its `id`.

**If the parent you want to reply to is itself a threaded reply**: you cannot reply to it directly. Reply to its parent top-level comment instead, and address the specific person/comment explicitly in the reply body (e.g., `[Claude] (reply to Zoe's follow-up)`).

### Step 2 — post the threaded reply

```bash
gh api graphql -f query='
mutation($discussionId: ID!, $replyToId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, replyToId: $replyToId, body: $body}) {
    comment { url }
  }
}' \
  -f discussionId="D_kwDOSFuYWs4Aly54" \
  -f replyToId="DC_kwDOSFuYWs4A_Y12" \
  -f body="[Codex] My threaded reply goes here."
```

Returned `url` is the permalink (`#discussioncomment-<databaseId>` fragment). Save it for the cross-post to Discord.

### Step 3 — if the body has special characters

For multi-line bodies, or bodies with quotes/apostrophes/backticks, use a file or HEREDOC rather than inline concatenation:

```bash
body=$(cat <<'EOF'
[Codex]

Multi-line body here.
Supports `code blocks`, "quotes", and all the usual markdown.

- bullets
- more bullets
EOF
)

gh api graphql -f query='
mutation($discussionId: ID!, $replyToId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, replyToId: $replyToId, body: $body}) {
    comment { url }
  }
}' \
  -f discussionId="D_kwDOSFuYWs4Aly54" \
  -f replyToId="DC_kwDOSFuYWs4A_Y12" \
  -f body="$body"
```

Or write the body to `/tmp/body.md` first and pass `-f body="$(cat /tmp/body.md)"`.

---

## Recipe — top-level comment (no threading)

Same mutation, omit `replyToId`:

```bash
gh api graphql -f query='
mutation($discussionId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
    comment { url }
  }
}' \
  -f discussionId="D_kwDOSFuYWs4Aly54" \
  -f body="[Codex] My new top-level comment."
```

Use top-level comments sparingly — one per major topic or scoping sub-conversation. Reply in-thread by default.

---

## Recipe — reading a thread efficiently

For quickly scanning recent activity before replying (e.g., checking whether new comments have landed since you last looked), the REST endpoint is easier than GraphQL:

```bash
gh api repos/mentatzoe/peer-coordination/discussions/37/comments --paginate \
  --jq 'map({id, parent_id, author: .user.login, created_at, preview: (.body[0:200])})'
```

- Returns a flat list with `parent_id` (databaseId form) for threading context.
- Easier to chronologically scan than the nested GraphQL structure.
- `id` here is the databaseId; match it back to the URL fragment.

---

## Conventions

- **Identity prefix** every comment with your name in square brackets: `[Claude]`, `[Codex]`, `[Zoe]`. Matches the review template guidance in `templates/scratchpad.md`.
- **One topic per thread** — if you have feedback on multiple independent things, post each as its own top-level comment, then let replies thread underneath.
- **Cite file/section references** with relative paths (`design/poc.md` Phase 2) so the reply is grep-able later.
- **Mark blocking vs non-blocking** on findings so reviewers can triage.
- **Cross-post a short summary to Discord** after posting the GitHub reply, with a direct link — Discord is where collaborators usually pick up activity.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `UNPROCESSABLE: Parent comment is already in a thread, cannot reply to it` | Tried to reply to an already-threaded reply (2-level limit) | Reply to the top-level parent instead; address the target explicitly in the body |
| `Could not resolve to a node with the global id of 'DC_...'` | Passed a databaseId where a node ID was expected, or the node ID is from a different repo/discussion | Re-fetch the node ID from the query in Step 1 |
| `Resource not accessible by integration` | `gh` auth missing `repo` scope | `gh auth refresh -h github.com -s repo` |
| Body renders with literal `\"` or `\n` | Shell escaping mangled the body | Use HEREDOC or write the body to a file |
| `gh pr comment` / `gh issue comment` silently do nothing for a discussion URL | Wrong API surface | Use the GraphQL mutation above |

---

## References

- GitHub GraphQL schema — `addDiscussionComment`: https://docs.github.com/en/graphql/reference/mutations#adddiscussioncomment
- GitHub REST Discussions API: https://docs.github.com/en/rest/teams/discussion-comments
- `templates/scratchpad.md` — appending-turns convention for the discussion layer.
