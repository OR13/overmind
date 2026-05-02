---
name: post-content
description: Curate trending content matching the user's topic preferences and post hot takes to Bluesky and X.com. Searches web and platform feeds, drafts commentary in the user's configured voice, and publishes after explicit approval. Use when the user wants to post social media content.
---

## Content Curation & Posting

Discover content matching the user's `topicKeywords` from preferences, draft a hot take in their configured `voice`, and post it with a link to the original source.

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `memory/playbooks/social-media/README.md`.

## User Input

```text
$ARGUMENTS
```

If `$ARGUMENTS` is provided, use it as the topic for this session instead of the default keywords from preferences.

## Execution

Follow these steps in order. Do NOT skip any step. Do NOT publish without explicit user approval.

### Step 1: Check platform credentials

Check which platform credentials are available by reading environment variables via Bash:

```bash
echo "BLUESKY_HANDLE=${BLUESKY_HANDLE:-(not set)}"
echo "BLUESKY_APP_PASSWORD=${BLUESKY_APP_PASSWORD:+set}"
echo "X_ACCESS_TOKEN=${X_ACCESS_TOKEN:+set}"
echo "X_BEARER_TOKEN=${X_BEARER_TOKEN:+set}"
```

- If both Bluesky vars are set: Bluesky is available
- If `X_ACCESS_TOKEN` is set: X.com posting is available
- If `X_BEARER_TOKEN` is set: X.com reading is available
- If NO credentials are set for either platform: STOP and report an error. Tell the user to set environment variables per the quickstart guide. List the required variables: `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, `X_ACCESS_TOKEN`, `X_BEARER_TOKEN`.

Report which platforms are available before continuing.

### Step 2: Load preferences and post log

Ensure the data directory exists:

```bash
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see memory/playbooks/social-media/README.md}/.git-ignored/social-media"
```

Read preferences:

```bash
cat $OVERMIND_ROOT/.git-ignored/social-media/preferences.json 2>/dev/null
```

If the file doesn't exist, STOP and tell the user to run `/social-config` first to seed preferences and add at least one topic keyword. Do not proceed.

If the file exists but `topicKeywords` is empty AND `$ARGUMENTS` is also empty, STOP and tell the user to add keywords via `/social-config add keyword "..."` or pass a topic as an argument. Do not proceed.

Read the post log for deduplication:

```bash
cat $OVERMIND_ROOT/.git-ignored/social-media/post-log.json 2>/dev/null
```

If the file doesn't exist, treat it as an empty array `[]`.

Extract the topic keywords from preferences. If `$ARGUMENTS` was provided, use that as the search topic instead.

### Step 3: Check posting limits

Read `maxPostsPerDay` from preferences. Count how many entries in post-log.json have a `postedAt` date matching today (in the configured timezone).

- If today's count >= maxPostsPerDay: Warn the user that the daily limit has been reached. Ask if they want to proceed anyway or stop. If they stop, end here.
- If current time is outside the `preferredTimes` windows (more than 1 hour away from any preferred time): Inform the user and note the next preferred window. Offer to proceed anyway.

### Step 4: Discover content via web search

Use the WebSearch tool to find recent, high-quality content. Run 2-3 searches with different query angles:

1. Search for the primary topic keyword(s) from preferences + current year (e.g., `<keyword> 2026`)
2. Search for a variation that pairs a keyword with `best practices`, `analysis`, or `critique`
3. If a specific topic was provided in `$ARGUMENTS`, search for that directly

Collect the top results from each search. For each result, note the title, URL, and snippet.

### Step 5: Discover content via platform feeds (if credentials available)

**Bluesky** (if credentials are set):

Authenticate:

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.server.createSession \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$BLUESKY_HANDLE\", \"password\": \"$BLUESKY_APP_PASSWORD\"}"
```

Extract `accessJwt` and `did` from the response. Then fetch timeline:

```bash
curl -s -X GET "https://bsky.social/xrpc/app.bsky.feed.getTimeline?limit=30" \
  -H "Authorization: Bearer <ACCESS_JWT>"
```

Scan the timeline posts for content related to the topic keywords. Extract any shared links/URLs.

**X.com** (if bearer token or access token is set):

Fetch the authenticated user's ID:

```bash
curl -s -X GET "https://api.x.com/2/users/me" \
  -H "Authorization: Bearer $X_ACCESS_TOKEN"
```

Then fetch recent timeline:

```bash
curl -s -X GET "https://api.x.com/2/users/<USER_ID>/tweets?max_results=30&tweet.fields=created_at,entities" \
  -H "Authorization: Bearer ${X_BEARER_TOKEN:-$X_ACCESS_TOKEN}"
```

Scan for content related to the topic keywords. Extract shared URLs.

If authentication fails for either platform, report the error clearly and continue with the other platform. Do not stop entirely.

### Step 6: Rank, deduplicate, and filter candidates

Combine all discovered content (web search + platform feeds). For each candidate:

1. Check if the URL already exists in post-log.json — if so, exclude it (already posted)
2. Assess relevance to the topic keywords (score 0-1)
3. Prefer recent content (last 7 days)
4. Prefer content with substantive analysis over announcements or listicles

Sort by relevance score. Select the top 3 candidates.

### Step 7: Present candidates to user

Present the top 3 candidates in a numbered list. For each candidate show:

- **Title**: The article/post title
- **URL**: Link to original content
- **Summary**: 2-3 sentence summary of the key points
- **Source**: Where it was discovered (web search / Bluesky feed / X.com feed)
- **Published**: When the content was published (if known)

Then ask the user to select a candidate using AskUserQuestion:
- Option 1: Candidate 1
- Option 2: Candidate 2
- Option 3: Candidate 3

If no qualifying candidates were found, report that no strong candidates were found for the current topics. Suggest the user try different keywords or broaden the search, then end.

### Step 8: Generate hot take drafts

For the selected candidate, generate a hot take in the voice configured in preferences (`voice` field). Apply the voice description to the draft — it specifies the tone and stance to use.

Universal rules regardless of voice:
- Include a link to the original content
- Avoid bland summaries — the post should add a perspective, not just describe
- Stay within character limits (see below)

Generate TWO versions:

**Bluesky version** (max 300 characters total including the URL):
- URLs count toward the character limit
- Show the exact character count

**X.com version** (max 280 characters total including the URL):
- URLs are shortened to 23 characters by X.com (t.co)
- Show the exact character count

If a version exceeds the character limit, shorten it. Do NOT truncate mid-word or mid-thought.

### Step 9: User review and approval

Present both drafts to the user with character counts. Use AskUserQuestion with these options:

- **Approve**: Post as-is to the default platforms
- **Edit**: User provides revised text (regenerate character counts after edit)
- **Reject**: Discard and end

If the user chooses Edit, accept their revised text, verify character limits, and present for approval again.

NEVER proceed to publishing without explicit "Approve" from the user.

### Step 10: Confirm target platforms

Ask the user which platform(s) to post to using AskUserQuestion:

- **Both** (Bluesky auto-publish + X.com copy-paste)
- **Bluesky only** (auto-publish via API)
- **X.com only** (copy-paste text provided)

Default to the `defaultPlatforms` from preferences, but always confirm.

### Step 11: Publish to Bluesky

If Bluesky is selected and credentials are available:

Authenticate (if not already done in Step 5):

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.server.createSession \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$BLUESKY_HANDLE\", \"password\": \"$BLUESKY_APP_PASSWORD\"}"
```

Create the post with an external link embed:

```bash
curl -s -X POST https://bsky.social/xrpc/com.atproto.repo.createRecord \
  -H "Authorization: Bearer <ACCESS_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "<DID>",
    "collection": "app.bsky.feed.post",
    "record": {
      "text": "<BLUESKY_POST_TEXT>",
      "createdAt": "<ISO_8601_TIMESTAMP>",
      "embed": {
        "$type": "app.bsky.embed.external",
        "external": {
          "uri": "<ORIGINAL_CONTENT_URL>",
          "title": "<CONTENT_TITLE>",
          "description": "<BRIEF_DESCRIPTION>"
        }
      }
    }
  }'
```

Capture the response `uri` and `cid`. If the request fails with 401, re-authenticate and retry once. If it fails with 429 (rate limit), wait 30 seconds and retry once. Report any other errors to the user.

### Step 12: X.com — Copy-Paste Output

X.com does not support direct API posting on the free tier. Instead of publishing via API, present the X.com draft text in a ready-to-copy format:

```
────────────────────────────────────
📋 X.com Post (copy & paste)
────────────────────────────────────
<XCOM_POST_TEXT>
────────────────────────────────────
Characters: <COUNT>/280
────────────────────────────────────
```

Then provide a direct link to open X.com's compose screen:

```
Post it here: https://x.com/compose/post
```

Tell the user: "Copy the text above and paste it at the link. The URL in the post will automatically generate a link card preview on X.com."

Do NOT attempt to call the X.com tweets API. The X.com post is manual — the user copies and pastes.

### Step 13: Update post log

After Bluesky publishes successfully (and/or user confirms they posted to X.com), read the current post-log.json, append a new entry, and write it back:

```json
{
  "url": "<ORIGINAL_CONTENT_URL>",
  "contentId": "<SHA256_OF_URL>",
  "platforms": ["bluesky", "xcom"],
  "postedAt": "<ISO_8601_TIMESTAMP>",
  "textHash": "<SHA256_OF_POST_TEXT>",
  "blueskyUri": "<AT_URI_OR_NULL>",
  "xcomTweetId": null
}
```

For platforms: include "bluesky" if auto-published, include "xcom" if the user confirmed they pasted it. Ask the user: "Did you post the X.com version? (yes/no)" to determine whether to log it.

Write the updated array to `$OVERMIND_ROOT/.git-ignored/social-media/post-log.json` using the Write tool.

### Step 14: Report completion

Summarize what was posted:
- Bluesky: auto-published (show post URI)
- X.com: copy-paste text provided (show compose link)
- Link to original content
- Today's post count vs. daily limit
