# Social Media Skills

Slash commands for posting hot takes and curating your follow graph on
Bluesky and X.com from inside Claude Code. Skill prompts are committed
to `overmind/.claude/commands/`. Per-user state — preferences, post
history, keep list — lives in `overmind/.git-ignored/social-media/` and
is never committed.

## Commands

| Command | What it does |
|---------|--------------|
| `/post-content` | Discovers trending content via web + platform feeds, drafts a hot take, posts to Bluesky via API, gives you copy-paste text for X.com. |
| `/filter-follows [bluesky\|xcom]` | Audits accounts you follow, classifies recent posts (business/tech, politics, sports, sexual, other) using a local Ollama model, recommends unfollows for ≥70% off-topic accounts. |
| `/discover-accounts [bluesky\|xcom]` | Finds candidate accounts to follow via web search + follow-of-follow analysis, verifies topic relevance via Ollama, follows after approval. |
| `/social-config` | View or modify the preferences file. |

## One-time setup

### 1. Set `OVERMIND_ROOT`

The skills read and write state under `$OVERMIND_ROOT/.git-ignored/social-media/`.
Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export OVERMIND_ROOT="$HOME/overmind"   # or wherever you cloned overmind
```

### 2. Bluesky credentials

1. Generate an app password at <https://bsky.app/settings/app-passwords>.
2. Export:

   ```bash
   export BLUESKY_HANDLE="your-handle.bsky.social"
   export BLUESKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
   ```

### 3. X.com credentials (optional)

The free tier supports posting via copy-paste only — no direct API post.
If you want timeline-reading and follow-management features, you'll need
all five OAuth 1.0a values from <https://developer.x.com/en/portal/dashboard>:

```bash
export X_API_KEY="..."
export X_API_KEY_SECRET="..."
export X_BEARER_TOKEN="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_TOKEN_SECRET="..."
```

Skip this section entirely if you only want Bluesky.

### 4. Ollama (for `/filter-follows` and `/discover-accounts`)

Account classification runs locally to avoid burning Claude tokens. Pull
a small model:

```bash
ollama pull gemma2:2b
```

The skills will warn and offer keyword-fallback if Ollama is not running.

### 5. First run

```text
/social-config
```

This creates `$OVERMIND_ROOT/.git-ignored/social-media/preferences.json`
with defaults. Then:

```text
/social-config add keyword "topic you want to post about"
/social-config set frequency 2
```

## State files

All under `$OVERMIND_ROOT/.git-ignored/social-media/`:

| File | Contents |
|------|----------|
| `preferences.json` | Topic keywords, default platforms, posting cadence, timezone. |
| `post-log.json` | Append-only record of posts (URL, platforms, timestamp, post IDs). Used for dedup. |
| `keep-list.json` | Accounts excluded from `/filter-follows` recommendations. |

These are local-only — `.git-ignored/` is in the repo's `.gitignore`,
so nothing here ever gets committed or pushed.

## Privacy boundary

- **Committed (public):** the four skill prompts under `.claude/commands/`,
  this README. Generic — no handles, no personal topics.
- **Local-only (private):** everything under `.git-ignored/social-media/`.
  Your handles, your topics, your post history, your keep list.
- **Environment:** credentials live only in your shell profile; never in
  any committed file.
