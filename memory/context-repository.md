---
name: context-repository
description: How overmind composes its system prompt — Letta-style context-repository conventions, public/private split, and how memory skills evolve the prompt over time.
---

# Context repository conventions

Overmind treats the repo itself as a Letta-style context repository
([blog post](https://www.letta.com/blog/context-repositories)) with two
tiers that compose at session start.

## Tiers

1. **Public, evolutionary** — `overmind/memory/`, this directory.
   Generic enough to be public. Workspace conventions worth surfacing on
   every turn. (Skill and operator registries live in `AGENTS.md` at the
   repo root, not here, so they stay alongside the static contract.)
2. **Private, evolutionary** — `memory/private/` when the private memory
   repo is cloned there. The directory is a clone of the separate
   `overmind-private-memory` git repo and is gitignored in overmind.
   Personal: identity, role, customer/org names, in-flight projects,
   sensitive feedback. Tracked in the private repo, never in overmind.

Within each tier:

- **Top-level `memory/*.md`** is auto-loaded into the system prompt every
  session.
- **Nested `memory/<topic>/...`** (e.g. `memory/playbooks/social-media/`)
  is on-demand reference — agents navigate there when the topic is
  relevant; it is *not* concatenated into the prompt.

`AGENTS.md` at the repo root is the **static** entry contract — it does
not change between sessions. Everything dynamic lives under `memory/`.

## How the system prompt is built

`scripts/build-system-prompt.sh` concatenates, in order:

1. `AGENTS.md`
2. `memory/*.md` (top-level only, sorted alphabetically)
3. `memory/private/*.md` (top-level only) if `memory/private/` exists

`scripts/overmind` is the unified launcher and dispatches to either backend,
feeding the *same* assembled prompt through whichever ingestion surface
the CLI exposes:

- **claude**: `claude --append-system-prompt "$(scripts/build-system-prompt.sh)"`
- **gemini**: writes the assembled prompt to `GEMINI.md` at the
  workspace root (gitignored, regenerated on each launch). Gemini CLI
  auto-loads `GEMINI.md` from cwd; it has no `--append-system-prompt`
  flag, so this is the native mechanism.

Backend selection: positional arg (`overmind gemini`), env
(`OVERMIND_BACKEND=gemini`), or default (`claude`). Files missing on
disk are silently skipped — a fresh clone with no private repo still
works.

## File conventions

- Every `*.md` under `memory/` carries YAML frontmatter with `name` and
  `description` fields. The description tells future agents (and the
  defrag pass) what the file is for in one line.
- Prefer ~15–25 focused top-level files per tier. Anything larger should
  be split; near-duplicate small files should be merged. `/memory-defrag`
  does this on demand.
- Top-level `memory/*.md` is for content that should load on every turn.
  Nested `memory/<topic>/...` is for on-demand reference the agent
  navigates to. When in doubt, put it in a nested topic directory first
  — promote to top-level only when it's worth always-loaded context cost.

## Evolutionary skills

- `/memory-reflect` — reviews the current session, identifies durable
  items (feedback, project facts, references, user preferences), routes
  each to public or private memory based on a sensitivity gate, then
  asks before committing.
- `/memory-defrag` — audits both tiers for size and duplication,
  proposes splits/merges/renames, asks before applying.
