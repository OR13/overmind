---
name: discover-accounts
description: Discover and follow high-value accounts on Bluesky and X.com that post about the user's configured topic keywords. Use when the user wants to find new accounts to follow.
---

## Account Discovery

Find and suggest high-value accounts posting content related to the user's `topicKeywords` from preferences.

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `memory/playbooks/social-media/README.md`.

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
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see memory/playbooks/social-media/README.md}/.git-ignored/social-media"
cat "$OVERMIND_ROOT/.git-ignored/social-media/preferences.json" 2>/dev/null
```

Extract `topicKeywords` for search queries. If preferences don't exist OR `topicKeywords` is empty, STOP and tell the user to run `/social-config add keyword "..."` first. Do not proceed.

### Step 3.5: Load (or create) seeds.md

Seeds for follow-graph crawling are stored in a markdown file the user maintains directly:

```bash
SEEDS_FILE="$OVERMIND_ROOT/.git-ignored/social-media/seeds.md"
```

If `seeds.md` does not exist, create it with this default template (using the Write tool) and tell the user where it lives so they can edit it:

```markdown
# /discover-accounts seeds

Curated high-signal handles per platform. `/discover-accounts` crawls each
seed's follow list to surface candidates in the same topic space.

A good seed: a personal voice (not a publication or aggregator) whose own
followings are themselves a curated list of people in your topic. After
running `/discover-accounts` and approving follows, the strongest of those
new follows make excellent seeds — append them here.

## bluesky

<!-- One handle per bullet. Examples below; replace with your own. -->
<!-- - alice.bsky.social -->
<!-- - bob.example.com -->

## xcom

<!-- One handle per bullet. Examples below; replace with your own. -->
<!-- - alice -->
<!-- - bob -->
```

To parse `seeds.md` for a given platform, find the `## <platform>` heading (case-insensitive) and collect every line that starts with `- ` (or `* `), stripping leading `@` and surrounding whitespace. Lines starting with `<!--`, `#`, or blank lines are ignored. Stop at the next `## ` heading.

The result is two arrays: `bluesky_seeds` and `xcom_seeds`.

### Step 4: Search for candidate accounts

Use **WebSearch** to find prominent accounts/authors in the target topics:

Search queries to try (substitute `[platform]` with bluesky/x.com and `[keyword]` with each entry from `topicKeywords`):
- "best [platform] accounts to follow [keyword]"
- "top [platform] accounts [keyword] 2026"
- "influential [platform] voices [keyword]"
- "[keyword] experts on [platform]"

Use 3-4 searches with different angles. Collect account handles, names, and any context about why they're recommended.

### Step 5: Build candidate set (seed-driven, with platform-search fallback)

The strategy is platform-specific. Always also fetch the user's current follows so already-followed accounts can be filtered out at ranking time.

**Bluesky**:

Authenticate via `com.atproto.server.createSession` (keep the JWT in-process — never write it to `/tmp` or any shared path). Then fetch the user's full follow list via `app.bsky.graph.getFollows` (paginated) and build a `did` set of already-followed accounts.

Now choose the candidate-discovery path based on `bluesky_seeds` (parsed from `seeds.md` in Step 3.5):

**Path A (preferred): seed-driven follow-of-follow.** When `bluesky_seeds` is non-empty, use those handles as the seeds. For each seed:

```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.graph.getFollows?actor=<SEED_HANDLE>&limit=100" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Aggregate all returned follows into a Counter keyed by DID. Drop anyone in the user's already-followed set. Candidates appearing in multiple seeds' follow-lists are higher-confidence.

**Path B (fallback): platform search.** When `bluesky_seeds` is empty, query Bluesky directly for posts and profiles matching `topicKeywords`:

```bash
# For each topicKeyword and reasonable variants:
curl -s -X GET "https://bsky.social/xrpc/app.bsky.feed.searchPosts?q=<KEYWORD>&limit=25" \
  -H "Authorization: Bearer <ACCESS_JWT>"

curl -s -X GET "https://bsky.social/xrpc/app.bsky.actor.searchActors?q=<KEYWORD>&limit=15" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Collect distinct authors / actors, drop already-followed accounts. Rank by the number of distinct queries an author appears in (cross-query frequency = topic centrality signal).

**Anti-pattern (do NOT do this):** Picking seeds by substring-matching `topicKeywords` against the user's existing follows' bios/handles. Topic words like "agent" / "develop" / "product" match too many generic accounts and the resulting follow-of-follow set degrades to mainstream celebrities. Either use explicit `seedAccounts` (Path A) or platform search (Path B) — never auto-derive seeds from the follow graph.

**X.com**:

For X.com, the equivalent paths are:
- Path A: For each handle in `xcom_seeds`, resolve to user_id via `GET /2/users/by/username/<HANDLE>`, then `GET /2/users/<USER_ID>/following?max_results=100`. Aggregate.
- Path B: `GET /2/tweets/search/recent?query=<KEYWORD>&max_results=25` (requires elevated access — fall back to web search via Step 4 if not available).

**IMPORTANT**: Be mindful of API rate limits. For Path A, cap at 8 seeds. For Path B, cap at 8 keyword queries.

After this step, mention to the user that any accounts they end up following (Step 9) make excellent candidates for next-run seeds — they can append the handles to the appropriate `## bluesky` or `## xcom` section of `seeds.md`.

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

For each candidate, assess topic relevance by calling Ollama's local API with the `gemma4:latest` model. Substitute the user's `topicKeywords` (joined as a comma-separated list) into the prompt:

```bash
curl -s http://localhost:11434/api/generate -d '{
  "model": "gemma4:latest",
  "prompt": "What percentage of these posts are about any of: <TOPIC_KEYWORDS>? Return ONLY a number 0-100.\n\nPosts:\n1. <POST_1>\n2. <POST_2>\n...\n\nPercentage:",
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
