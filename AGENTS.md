# Agent Guide

Static entry contract for any agent working in this repository. Follows
the [AGENTS.md](https://agents.md) open standard. This file does not
change between sessions; evolutionary content lives in `memory/*.md`
and (privately) in `memory/private/*.md`.

## What this repo is

A personal coordination workspace. Most files are markdown. The "code" is the
structure: where things live and what gets committed.

## Navigation

- `.agents/skills/` — vendor-neutral [Agent Skills](https://agentskills.io)
  in the open-standard format (`<name>/SKILL.md` per skill).
  Auto-discovered by Gemini CLI. Claude Code finds them via a single
  directory symlink: `.claude/skills` → `../.agents/skills` (Claude Code
  natively reads `.claude/skills/<name>/SKILL.md`, which matches the
  open-standard layout exactly).
- `memory/` — evolutionary context.
  - Top-level `memory/*.md` is **public** and concatenated into the
    system prompt on every session (active conventions worth surfacing
    on every turn).
  - Nested `memory/<topic>/...` (e.g. `playbooks/`) is **public**
    on-demand reference — navigate here for the user's preferences,
    prior decisions, playbooks, or domain context.
  - `memory/private/` is the documented mount point for a clone of the
    separate `overmind-private-memory` git repo. Gitignored in this
    repo. When mounted, its top-level `*.md` files are also concatenated
    into the system prompt (identity, role, customers, in-flight work),
    and its nested `<topic>/...` is private on-demand reference. Never
    committed to overmind.
- `projects/` — active project work. Each subdirectory may be an external
  clone, a git submodule, or in-tree code. Defer to the project's own
  `AGENTS.md` (or equivalent) when present; this repo's conventions do
  not transitively apply. Memory repos do *not* live here.
- `.git-ignored/` — local-only scratch. Safe for large, transient, or
  experimental artifacts. Nothing here is ever committed.

## Skills

Committed at `.agents/skills/<name>/SKILL.md`. Per-skill state lives in
`.git-ignored/` or in private memory.

| Skill | Purpose |
|-------|---------|
| `post-content` | Draft and publish hot takes to Bluesky and X.com. |
| `discover-accounts` | Find candidate accounts to follow via seed crawl + platform search. |
| `filter-follows` | Audit followed accounts and recommend unfollows for off-topic content. |
| `memory-reflect` | Review recent conversation, persist durable items into public or private memory. |
| `memory-defrag` | Audit and consolidate the context repository toward 15–25 focused files per tier. |

## Operators

Long-lived agents (not skills) registered in this workspace. Industry
vocabulary calls these **subagents**; "operator" here means the
long-lived variant — registered once, invoked across many sessions.

- **somnabulist**: an agent that uses local AI models within VS Code to
  perform tasks autonomously while the user is inactive or asleep.

## Conventions

- Prefer editing existing markdown over creating new files.
- Place new files under the directory whose lifetime matches their purpose:
  always-loaded → top-level `memory/`, on-demand reference →
  `memory/<topic>/`, transient → `.git-ignored/`, project-scoped →
  `projects/<name>/`.
- Never force-add files inside `.git-ignored/`. If something is worth
  committing, it belongs elsewhere.
- Don't introduce vendor-specific tooling at the repo root. If a tool needs
  its own config file, symlink it to `AGENTS.md` rather than duplicating
  content.

## Git worktrees

Work in any `projects/<name>/` repo SHOULD be done in a git worktree, not
directly in the checked-out clone. This keeps the primary checkout on a
clean branch and lets concurrent agents work on different branches without
stomping on each other.

- **Location:** all worktrees go in `$OVERMIND_ROOT/.git-worktrees/`,
  which is gitignored. Create the directory if it doesn't exist.
- **Fetch first:** before creating a worktree, fetch the latest remote
  state so the new branch starts from an up-to-date base —
  `git -C projects/<name> fetch origin`.
- **Create:**
  `git -C projects/<name> worktree add $OVERMIND_ROOT/.git-worktrees/<slug> -b <feature-branch> origin/<base-branch>`
- **Feature branches only:** never check a worktree out directly on
  `main` (or whatever the project's default branch is).
- **Cleanup:** when the work is merged, abandoned, or no longer needed,
  remove the worktree and prune stale references —
  `git -C projects/<name> worktree remove $OVERMIND_ROOT/.git-worktrees/<slug>`
  then `git -C projects/<name> worktree prune`.

### Worktrees and pull requests (private repos)

When the worktree is on a private repo, pair it 1:1 with a **draft** pull
request so GitHub's PR list mirrors `.git-worktrees/` and a future review
surfaces the original motivation. (Public repos already follow the
"PRs only, no direct push to main" rule; this adds the draft + naming
alignment on top.)

- **One identifier, three places.** Pick one kebab-case slug and reuse
  it as the worktree directory name, the feature branch name, and the
  PR title. `gh pr list` and `ls $OVERMIND_ROOT/.git-worktrees/` then
  read as the same list — easy to spot drift in either direction.
- **Open the PR as a draft on first push.** Immediately after the
  initial commit + `git push -u origin <slug>`, run
  `gh pr create --draft --title "<slug>" --body "Why: <one-line motivation>"`.
  Use the same "Why:" line in the worktree's first commit message —
  that one line is what GitHub will remember when the PR resurfaces
  weeks later.
- **Stay draft until the work is actually done.** Never open a non-draft
  PR for in-progress work; flip with `gh pr ready <slug>` only when the
  branch is review-ready. GitHub blocks merging draft PRs through the
  UI, which is the safety net against shipping WIP.
- **Cleanup checks the PR first.** Before `git worktree remove`,
  confirm the PR is merged or explicitly closed. An open draft with no
  worktree on disk means cleanup ran too early — recreate the worktree
  or close the PR before pruning, so the GitHub view stays truthful.

## Dynamic system prompt

The launcher (`scripts/overmind`) concatenates this file plus top-level
`memory/*.md` plus (when mounted) top-level `memory/private/*.md` via
`scripts/build-system-prompt.sh`, and feeds the result to either Claude Code or
Gemini CLI. Backend selection is `overmind [claude|gemini]` (positional)
or `OVERMIND_BACKEND` env; default is `claude`.

- Claude path: `claude --append-system-prompt "$(scripts/build-system-prompt.sh)"`.
- Gemini path: the assembled prompt is written to `GEMINI.md` at the
  workspace root (gitignored, regenerated each launch) so Gemini CLI
  auto-loads it from cwd. `GEMINI.md` is *not* a hand-edited file —
  treat it as a build artifact.

Nested directories under `memory/` other than `private/` (e.g.
`memory/playbooks/`) are *not* auto-loaded — agents navigate to them on
demand. Likewise for nested directories under `memory/private/`.

See `memory/context-repository.md` for the full convention and the
`/memory-reflect` and `/memory-defrag` skills that evolve it.

## Commits

- Keep commits small and topical.
- Reference the directory in the subject when useful:
  `memory: add note on X`, `projects: add submodule Y`.

