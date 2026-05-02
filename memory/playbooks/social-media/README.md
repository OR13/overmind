# Social Media Skills

Skills for posting hot takes and curating your follow graph on Bluesky
and X.com. Committed at `overmind/.agents/skills/<name>/SKILL.md` in
the open-standard Agent Skills format — auto-discovered by Gemini CLI,
exposed as `/<name>` slash commands in Claude Code via
`.claude/commands/` symlinks. Per-user state — preferences, post
history, keep list — lives in `overmind/.git-ignored/social-media/`
and is never committed.

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
Export it from `~/.zshenv` so every shell — interactive, login, and any
subshell Claude Code spawns — inherits it:

```bash
export OVERMIND_ROOT="$HOME/overmind"   # or wherever you cloned overmind
```

`~/.zshenv` is the right file because zsh sources it for *every*
invocation. `~/.zshrc` only runs for interactive shells, so vars set
there can be missing from subshells the Bash tool spawns mid-session.

#### Optional: convenience alias

For an ergonomic launcher that also sources secrets and applies the
workspace's `AGENTS.md` system prompt, add to `~/.zshrc`:

```bash
alias overmind='cd "$OVERMIND_ROOT" && source "$OVERMIND_ROOT/.git-ignored/secrets.env" && claude --permission-mode auto --append-system-prompt "$("$OVERMIND_ROOT/scripts/build-system-prompt.sh")"'
```

The alias relies on `OVERMIND_ROOT` already being exported by
`~/.zshenv`. Don't try to export it inside the alias — if your
`secrets.env` ever sets or unsets `OVERMIND_ROOT` (intentionally or
otherwise), the alias-side export gets clobbered and skills break with
a confusing "OVERMIND_ROOT must point at your overmind clone" error.

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
the model the skills are configured to use:

```bash
ollama pull gemma4:latest
```

The skills will warn and offer keyword-fallback if Ollama is not running.
The model name is hardcoded in the skill prompts (`gemma4:latest`) — if
you want to substitute a different Ollama model, edit the
`SKILL.md` files under `.agents/skills/` directly.

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

### Seeding `/discover-accounts`

`/discover-accounts` finds candidate accounts to follow by crawling
the follow lists of a small set of high-signal seed accounts. Seeds
live in a markdown file you edit directly:

```text
$OVERMIND_ROOT/.git-ignored/social-media/seeds.md
```

The file is created with a default template the first time
`/discover-accounts` runs. Edit it in place — one handle per bullet,
under the `## bluesky` and `## xcom` sections. No slash commands.

When the seed list for a platform is empty, the skill falls back to
platform search (`searchPosts` + `searchActors` on Bluesky) — useful
for cold-starting on a new topic, but noisier than seed-driven
discovery.

A good seed is an account whose followings list is itself a curated
list of people in the topic — typically a personal voice, not a
publication or aggregator account. After running `/discover-accounts`
once and approving some follows, the strongest of those new follows
make excellent seeds for the next run; append them to `seeds.md`.

## State files

All under `$OVERMIND_ROOT/.git-ignored/social-media/`:

| File | Contents |
|------|----------|
| `preferences.json` | Topic keywords, voice, default platforms, posting cadence, timezone. |
| `seeds.md` | Per-platform high-signal handles used by `/discover-accounts` as follow-graph seeds. Edit directly — one handle per bullet under `## bluesky` / `## xcom`. |
| `post-log.json` | Append-only record of posts (URL, platforms, timestamp, post IDs). Used for dedup. |
| `keep-list.json` | Accounts excluded from `/filter-follows` recommendations. |

These are local-only — `.git-ignored/` is in the repo's `.gitignore`,
so nothing here ever gets committed or pushed.

## Privacy boundary

- **Committed (public):** the skill prompts under `.agents/skills/` and
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
