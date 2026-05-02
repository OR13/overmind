---
description: Discover and follow high-value accounts on Bluesky and X.com that post about AI product methodologies and agentic software development. Use when the user wants to find new accounts to follow for technical content.
---

## Account Discovery

Find and suggest high-value accounts posting quality content about AI, agentic development, and related business/technical topics.

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `knowledge/playbooks/social-media/README.md`.

## User Input

```text
$ARGUMENTS
```

If `$ARGUMENTS` specifies a platform ("bluesky" or "xcom"), discover on that platform only. If empty, discover on both.

## Execution

### Step 1: Determine target platform(s)

Parse `$ARGUMENTS`:
- "bluesky" or "bsky" → discover on Bluesky only
- "xcom" or "x" or "twitter" → discover on X.com only
- Empty or "both" → discover on both platforms

### Step 2: Check platform credentials

```bash
echo "BLUESKY_HANDLE=${BLUESKY_HANDLE:-(not set)}"
echo "BLUESKY_APP_PASSWORD=${BLUESKY_APP_PASSWORD:+set}"
echo "X_ACCESS_TOKEN=${X_ACCESS_TOKEN:+set}"
echo "X_BEARER_TOKEN=${X_BEARER_TOKEN:+set}"
```

If the requested platform's credentials are missing, STOP and report the error.

### Step 3: Load preferences

```bash
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see knowledge/playbooks/social-media/README.md}/.git-ignored/social-media"
cat "$OVERMIND_ROOT/.git-ignored/social-media/preferences.json" 2>/dev/null
```

Extract `topicKeywords` for search queries. If preferences don't exist, use the defaults:
- "agentic software development"
- "AI product methodology"
- "human-agent collaboration"
- "LLM tooling"

### Step 4: Search for candidate accounts

Use **WebSearch** to find prominent accounts/authors in the target topics:

Search queries to try:
- "best [platform] accounts to follow agentic software development"
- "top [platform] accounts AI product methodology 2026"
- "influential [platform] voices artificial intelligence engineering"
- "[topic keyword] experts on [platform]"

Use 3-4 searches with different angles. Collect account handles, names, and any context about why they're recommended.

### Step 5: Analyze the user's follow graph (if credentials available)

**Bluesky**:

Authenticate and fetch the user's current follows (Step 4 of filter-follows has the curl commands). For the user's top follows (accounts that post the most relevant content), check who THEY follow:

```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.graph.getFollows?actor=<FOLLOWED_HANDLE>&limit=50" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Look for accounts that appear in multiple "follows of follows" lists — these are likely high-value accounts in the same topic space.

**X.com**:

Similarly, for the user's existing follows, check their following lists:

```bash
curl -s -X GET "https://api.x.com/2/users/<FOLLOWED_USER_ID>/following?max_results=100" \
  -H "Authorization: Bearer ${X_BEARER_TOKEN:-$X_ACCESS_TOKEN}"
```

Look for accounts that appear frequently across multiple follow lists.

**IMPORTANT**: Be mindful of API rate limits. Limit to checking 5-10 of the user's top follows, not all of them.

### Step 6: Verify candidate quality

For each candidate account discovered in Steps 4-5, fetch their recent posts to verify content quality:

**Bluesky**:
```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor=<HANDLE>&limit=10" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

**X.com**:
```bash
curl -s -X GET "https://api.x.com/2/users/<USER_ID>/tweets?max_results=10&tweet.fields=text,created_at,public_metrics" \
  -H "Authorization: Bearer ${X_BEARER_TOKEN:-$X_ACCESS_TOKEN}"
```

**Use Ollama (local LLM) for content verification to avoid consuming Claude tokens.**

For each candidate, assess topic relevance by calling Ollama's local API with the `gemma2:2b` model:

```bash
curl -s http://localhost:11434/api/generate -d '{
  "model": "gemma2:2b",
  "prompt": "What percentage of these posts are about technology, AI, software, or engineering? Return ONLY a number 0-100.\n\nPosts:\n1. <POST_1>\n2. <POST_2>\n...\n\nPercentage:",
  "stream": false
}'
```

Write the entire verification loop as a single Python script executed via Bash, processing all candidates in one tool call.

For each candidate, also assess:
- Is the content original analysis or mostly retweets/reposts?
- How active is the account (posts per week)?
- Engagement levels (likes, reposts) as a signal of quality

Filter out candidates that:
- Already followed by the user
- Post less than once per week
- Have less than 50% topic-relevant content (per Ollama classification)

**IMPORTANT**: If Ollama is not running (`curl http://localhost:11434/api/tags` fails), warn the user and offer to fall back to keyword-based relevance scoring instead. Do NOT fall back to using Claude for classification — use either Ollama or keyword matching.

### Step 7: Present suggestions

Present up to 10 candidate accounts, ranked by relevance. For each:

```
### [N]. @handle — Display Name

**Platform**: Bluesky / X.com
**Bio**: [Account bio/description]
**Topic relevance**: [X]% of recent posts about target topics
**Activity**: ~[N] posts/week

**Sample posts**:
1. "[Excerpt of a relevant recent post]"
2. "[Excerpt of another relevant post]"
3. "[Excerpt of a third post]"
```

### Step 8: User selection

Use AskUserQuestion to let the user select which accounts to follow:

- Present a numbered list of all suggestions
- Allow the user to select multiple (e.g., "1, 3, 5, 7")
- Include an "All" option and a "None" option

### Step 9: Execute follows

For each selected account:

**Bluesky**:

First resolve the handle to a DID if needed:

```bash
curl -s -X GET "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=<HANDLE>"
```

Then create the follow record:

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.repo.createRecord \
  -H "Authorization: Bearer <ACCESS_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "<YOUR_DID>",
    "collection": "app.bsky.graph.follow",
    "record": {
      "subject": "<TARGET_DID>",
      "createdAt": "<ISO_8601_TIMESTAMP>"
    }
  }'
```

**X.com**:

```bash
curl -s -X POST "https://api.x.com/2/users/<YOUR_USER_ID>/following" \
  -H "Authorization: Bearer $X_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target_user_id": "<TARGET_USER_ID>"}'
```

Report each successful follow. If any fails, report the error and continue with the rest.

### Step 10: Report completion

Summarize:
- Number of new accounts followed per platform
- List of newly followed accounts with handles
- Suggest running `/filter-follows` periodically to keep the feed clean
- Suggest running `/discover-accounts` again in a few weeks to find new voices
