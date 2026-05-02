---
name: filter-follows
description: Audit and filter followed accounts on Bluesky and X.com. Classifies accounts by content topic and recommends unfollowing those posting off-topic content (politics, sexual content, sports). Use when the user wants to clean up their social media feed.
---

## Account Audit & Filter

Review the accounts you follow, classify them by content topic, and recommend unfollowing accounts that predominantly post off-topic content.

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `memory/playbooks/social-media/README.md`.

## User Input

```text
$ARGUMENTS
```

If `$ARGUMENTS` specifies a platform ("bluesky" or "xcom"), audit only that platform. If empty, audit both.

## Execution

Follow these steps in order. Do NOT unfollow any account without explicit user approval.

### Step 1: Determine target platform(s)

Parse `$ARGUMENTS`:
- "bluesky" or "bsky" → audit Bluesky only
- "xcom" or "x" or "twitter" → audit X.com only
- Empty or "both" → audit both platforms

### Step 2: Check platform credentials

Check environment variables via Bash:

```bash
echo "BLUESKY_HANDLE=${BLUESKY_HANDLE:-(not set)}"
echo "BLUESKY_APP_PASSWORD=${BLUESKY_APP_PASSWORD:+set}"
echo "X_ACCESS_TOKEN=${X_ACCESS_TOKEN:+set}"
echo "X_BEARER_TOKEN=${X_BEARER_TOKEN:+set}"
```

If the user requested a specific platform and credentials are missing for it, STOP and report the error with the required variable names.

If auditing both and only one platform has credentials, report which platform will be skipped and continue with the available one.

### Step 3: Load keep list

```bash
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see memory/playbooks/social-media/README.md}/.git-ignored/social-media"
cat "$OVERMIND_ROOT/.git-ignored/social-media/keep-list.json" 2>/dev/null
```

If the file doesn't exist, treat it as an empty array `[]`. Parse the keep list — these accounts will be excluded from unfollow recommendations.

### Step 4: Fetch followed accounts

**Bluesky** (if auditing):

Authenticate:

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.server.createSession \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$BLUESKY_HANDLE\", \"password\": \"$BLUESKY_APP_PASSWORD\"}"
```

Extract `accessJwt` and `did`. Then paginate through all follows:

```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.graph.getFollows?actor=<HANDLE>&limit=100" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Use the `cursor` field from each response to fetch the next page until all follows are retrieved. Collect handle, displayName, and did for each account.

**X.com** (if auditing):

Get authenticated user ID:

```bash
curl -s -X GET "https://api.x.com/2/users/me" \
  -H "Authorization: Bearer $X_ACCESS_TOKEN"
```

Then paginate through follows:

```bash
curl -s -X GET "https://api.x.com/2/users/<USER_ID>/following?max_results=100&user.fields=name,username,description" \
  -H "Authorization: Bearer ${X_BEARER_TOKEN:-$X_ACCESS_TOKEN}"
```

Use `pagination_token` from `meta.next_token` to fetch subsequent pages.

Report total count of followed accounts per platform before proceeding.

### Step 5: Classify accounts

For each followed account that is NOT in the keep list:

**Fetch recent posts** (last 50):

Bluesky:
```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor=<HANDLE>&limit=50" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

X.com:
```bash
curl -s -X GET "https://api.x.com/2/users/<USER_ID>/tweets?max_results=50&tweet.fields=text,created_at" \
  -H "Authorization: Bearer ${X_BEARER_TOKEN:-$X_ACCESS_TOKEN}"
```

**Classify the posts using Ollama (local LLM) to avoid consuming Claude tokens.**

For each account, collect post texts and classify them by calling Ollama's local API with the `gemma2:2b` model. Use a single Bash/Python script that processes all accounts in a loop:

```bash
# Example: classify posts for one account using Ollama
curl -s http://localhost:11434/api/generate -d '{
  "model": "gemma2:2b",
  "prompt": "Classify these social media posts into ONE category: business_tech, politics, sports, sexual, or other.\n\nRules:\n- business_tech: software, AI/ML, engineering, startups, product management, technology, security, crypto, cloud\n- politics: elections, government, legislation, political parties, partisan debate, activism, policy\n- sports: teams, players, scores, athletic events\n- sexual: adult/NSFW content\n- other: does not fit above\n\nPosts:\n1. <POST_TEXT_1>\n2. <POST_TEXT_2>\n...\n\nReturn ONLY one word: business_tech, politics, sports, sexual, or other",
  "stream": false
}'
```

Process posts in batches of 5 per Ollama call for speed. For each account, make multiple calls to classify all posts, then compute the percentage breakdown.

Categories:
- **business/technical**: Software development, AI/ML, product management, engineering, business strategy, startups, technology industry
- **politics**: Political parties, elections, legislation, political commentary, government policy, partisan debate
- **sexual content**: Adult content, sexually explicit material, NSFW content
- **sports**: Athletic events, teams, players, scores, sports commentary
- **other**: Content that doesn't clearly fit the above categories

Compute the percentage breakdown for each account. For example: 70% business/technical, 20% politics, 10% other.

**Apply the 70% threshold**:
- If combined off-topic (politics + sexual content + sports) >= 70%: recommend **unfollow**
- If combined off-topic is 50-69%: mark as **mixed** (user decides)
- If combined off-topic < 50%: mark as **keep**

Write the entire classification loop as a single Python script executed via Bash, so all accounts are processed in one tool call. Report progress as you classify (e.g., "Classified 25/150 accounts...").

**IMPORTANT**: If Ollama is not running (`curl http://localhost:11434/api/tags` fails), warn the user and offer to fall back to keyword-based classification instead. Do NOT fall back to using Claude for classification — use either Ollama or keyword matching.

**IMPORTANT**: Process accounts in batches to manage API rate limits. If you hit a Bluesky rate limit, wait for the reset window before continuing. For large follow lists (500+), this may take several minutes — keep the user informed of progress.

### Step 6: Present results

Present a summary table:

```
## Audit Results — [Platform]

| Category          | Count |
|-------------------|-------|
| Business/Tech     | XX    |
| Politics          | XX    |
| Sexual Content    | XX    |
| Sports            | XX    |
| Other             | XX    |
| Mixed (50-69%)    | XX    |
| Keep list (exempt) | XX   |

### Recommended Unfollows (>=70% off-topic)

| # | Handle | Dominant Category | Off-Topic % |
|---|--------|-------------------|-------------|
| 1 | @example | Politics | 85% |
| 2 | @example2 | Sports | 72% |

### Mixed Accounts (50-69% off-topic — your call)

| # | Handle | Breakdown | Off-Topic % |
|---|--------|-----------|-------------|
| 1 | @mixed1 | 55% politics, 45% tech | 55% |
```

### Step 7: User approval for unfollows

Use AskUserQuestion to ask the user how to proceed:

- **Approve all**: Unfollow all recommended accounts
- **Review individually**: Go through each recommended account one by one
- **Skip**: Do not unfollow anyone

If "Review individually": For each recommended account, ask: Unfollow / Keep (add to keep list) / Skip.

For mixed accounts, present each and ask: Unfollow / Keep (add to keep list) / Skip.

### Step 8: Execute unfollows

For each approved unfollow:

**Bluesky**: First find the follow record. The follow record rkey can be derived. Delete it:

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.repo.deleteRecord \
  -H "Authorization: Bearer <ACCESS_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "<YOUR_DID>",
    "collection": "app.bsky.graph.follow",
    "rkey": "<FOLLOW_RECORD_RKEY>"
  }'
```

To find the rkey, you may need to list records:

```bash
curl -s -X GET "https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=<YOUR_DID>&collection=app.bsky.graph.follow&limit=100" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Search for the record where the subject matches the target account's DID.

**X.com**:

```bash
curl -s -X DELETE "https://api.x.com/2/users/<YOUR_USER_ID>/following/<TARGET_USER_ID>" \
  -H "Authorization: Bearer $X_ACCESS_TOKEN"
```

Report each successful unfollow. If any fails, report the error and continue with the rest.

### Step 9: Update keep list

For every account the user marked as "keep", append to keep-list.json:

```json
{
  "handle": "<ACCOUNT_HANDLE>",
  "platform": "bluesky",
  "addedAt": "<ISO_8601_TIMESTAMP>",
  "reason": null
}
```

Read the current keep-list.json, append new entries (avoid duplicates by checking handle + platform), and write it back using the Write tool.

### Step 10: Report completion

Summarize:
- Total accounts audited per platform
- Accounts unfollowed (count and list)
- Accounts added to keep list
- Accounts in mixed category (not actioned)
- Remaining follow count
