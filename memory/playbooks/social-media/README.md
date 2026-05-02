# Social Media Skills

Skills for posting hot takes and curating your follow graph on Bluesky
and X.com. Committed at `overmind/.agents/skills/<name>/SKILL.md` in
the open-standard Agent Skills format — auto-discovered by Gemini CLI,
exposed as `/<name>` slash commands in Claude Code via
`.claude/commands/` symlinks. Per-user state — preferences, post
history, keep list — lives in `memory/private/social-media/`
and is never committed to overmind.

## Commands

| Command | What it does |
|---------|--------------|
| `/post-content` | Discovers trending content via web + platform feeds, drafts a hot take, posts to Bluesky via API, gives you copy-paste text for X.com. |
| `/filter-follows [bluesky\|xcom]` | Audits accounts you follow, classifies recent posts (business/tech, politics, sports, sexual, other) using a local Ollama model, recommends unfollows for ≥70% off-topic accounts. |
| `/discover-accounts [bluesky\|xcom]` | Finds candidate accounts to follow via web search + follow-of-follow analysis, verifies topic relevance via Ollama, follows after approval. |

## Configuration

Social media preferences and state are managed directly in your private memory tier at `memory/private/social-media/`.

- **`preferences.md`**: ALL settings and configuration, including topic keywords, voice, seeds, and the keep list.
- **`posts/`**: A directory containing individual `.md` files for each post, named by a slug. Each file contains metadata (URL, platforms, text, engagement).

You can view or modify these files directly, or use the specialized tool:

```bash
uv run tools/overmind_social_skills_memory.py config get
uv run tools/overmind_social_skills_memory.py config set topic_keywords "agentic dev,ai product"
```

## One-time setup

### 1. Set `OVERMIND_ROOT`

The skills read and write state under `$OVERMIND_ROOT/memory/private/social-media/`.
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

Ensure `memory/private/social-media/preferences.md` is initialized. You can
initialize it with defaults using:

```bash
uv run tools/overmind_social_skills_memory.py config get
```

You must add at least one keyword before `/post-content` or
`/discover-accounts` will run:

```bash
uv run tools/overmind_social_skills_memory.py config set topic_keywords "agentic software development,AI product methodology"
uv run tools/overmind_social_skills_memory.py config set timezone "America/Chicago"
uv run tools/overmind_social_skills_memory.py config set voice "analytical contrarian; novel angle; insightful but opinionated"
```

The `voice` field controls how `/post-content` drafts hot takes — keep
it short and specific. Examples: `"analytical contrarian"`,
`"earnest enthusiast"`, `"deadpan observer"`.

### Seeding `/discover-accounts`

`/discover-accounts` finds candidate accounts to follow by crawling
the follow lists of a small set of high-signal seed accounts. Seeds
live in the private memory file:

```bash
$OVERMIND_ROOT/memory/private/social-media/seeds.md
```

The file is managed via `uv run tools/overmind_social_skills_memory.py seeds`.

When the seed list for a platform is empty, the skill falls back to
platform search (`searchPosts` + `searchActors` on Bluesky) — useful
for cold-starting on a new topic, but noisier than seed-driven
discovery.

A good seed is an account whose followings list is itself a curated
list of people in the topic — typically a personal voice, not a
publication or aggregator account. After running `/discover-accounts`
once and approving some follows, the strongest of those new follows
make excellent seeds for the next run.

## State files

All under `$OVERMIND_ROOT/memory/private/social-media/`:

| File / Dir | Contents |
|------|----------|
| `preferences.md` | Topic keywords, voice, default platforms, posting cadence, timezone, seeds, and keep list. |
| `posts/` | Individual post files containing URLs, text content, and engagement metrics. |

These are local-only and kept in your private memory repository.

## Privacy boundary

- **Committed (public):** the skill prompts under `.agents/skills/` and
  this README. Generic — no handles, no personal topics.
- **Private memory:** everything under `memory/private/social-media/`.
  Your handles, your topics, your post history, your keep list.
- **Environment:** credentials live only in your shell profile; never in
  any committed file.

## Known limitations

- `/filter-follows` hardcodes its off-topic taxonomy as `politics`,
  `sports`, and `sexual content`, with `business_tech` as the default
  on-topic category. If you want to follow political or sports accounts
  on purpose, add them to `keep_list.md` — or fork the skill and
  rewrite the classifier prompt. The categories are not yet
  configurable via `preferences.md`.
- X.com posting requires copy-paste; the free API tier doesn't permit
  programmatic tweets at sustainable volumes.
