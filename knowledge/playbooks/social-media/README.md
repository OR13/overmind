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

The recommended setup is a shell alias that exports `OVERMIND_ROOT`,
sources your secrets, and launches Claude Code from the workspace
root. Add to `~/.zshrc` (or your shell's equivalent):

```bash
alias overmind='export OVERMIND_ROOT="$HOME/overmind" && cd "$OVERMIND_ROOT" && source "$OVERMIND_ROOT/.git-ignored/secrets.env" && claude --permission-mode auto --append-system-prompt "$(cat "$OVERMIND_ROOT/AGENTS.md")"'
```

Then start every session with `overmind`. If you prefer to launch
Claude Code directly without the alias, export the variable yourself
in your shell profile:

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
with neutral defaults (empty topic keywords, neutral voice, UTC timezone).
You must add at least one keyword before `/post-content` or
`/discover-accounts` will run:

```text
/social-config add keyword "topic you want to post about"
/social-config set timezone "America/New_York"
/social-config set voice "deadpan observer; understated wit; never preachy"
```

The `voice` field controls how `/post-content` drafts hot takes — keep
it short and specific. Examples: `"analytical contrarian"`,
`"earnest enthusiast"`, `"deadpan observer"`.

## State files

All under `$OVERMIND_ROOT/.git-ignored/social-media/`:

| File | Contents |
|------|----------|
| `preferences.json` | Topic keywords, voice, default platforms, posting cadence, timezone. |
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

## Known limitations

- `/filter-follows` hardcodes its off-topic taxonomy as `politics`,
  `sports`, and `sexual content`, with `business_tech` as the default
  on-topic category. If you want to follow political or sports accounts
  on purpose, add them to `keep-list.json` — or fork the skill and
  rewrite the classifier prompt. The categories are not yet
  configurable via `preferences.json`.
- X.com posting requires copy-paste; the free API tier doesn't permit
  programmatic tweets at sustainable volumes.
