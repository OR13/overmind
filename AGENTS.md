# Agent Guide

Entry contract for any agent working in this repository. Follows the
[AGENTS.md](https://agents.md) open standard.

## What this repo is

A personal coordination workspace. Most files are markdown. The "code" is the
structure: where things live and what gets committed.

## Navigation

- `knowledge/` — curated reference material. Read this before answering
  questions about the user's preferences, prior decisions, or domain context.
- `projects/` — active work. Each subdirectory may be an external clone, a
  git submodule, or in-tree code. Defer to the project's own `AGENTS.md` (or
  equivalent) when present; this repo's conventions do not transitively apply.
- `.git-ignored/` — local-only scratch. Safe for large, transient, or
  experimental artifacts. Nothing here is ever committed.

## Conventions

- Prefer editing existing markdown over creating new files.
- Place new files under the directory whose lifetime matches their purpose:
  curated → `knowledge/`, transient → `.git-ignored/`, project-scoped →
  `projects/<name>/`.
- Never force-add files inside `.git-ignored/`. If something is worth
  committing, it belongs elsewhere.
- Don't introduce vendor-specific tooling at the repo root. If a tool needs
  its own config file, symlink it to `AGENTS.md` rather than duplicating
  content.

## Commits

- Keep commits small and topical.
- Reference the directory in the subject when useful:
  `knowledge: add note on X`, `projects: add submodule Y`.

## What not to do

- Do not commit secrets, API keys, or personal credentials.
- Do not commit large binaries or model weights — use `.git-ignored/`.
- Do not check files into `projects/` without an explicit reason; the
  default is to keep them out of this repo's history.
