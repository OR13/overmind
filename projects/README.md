# projects/

Active workspaces. Contents are gitignored by default, which lets you clone
external repos, experiment freely, or attach git submodules without polluting
this repo's history.

## Adding work here

Three patterns, in order of preference:

1. **External clone** — `git clone <url> projects/<name>`. The clone keeps its
   own `.git`, and this repo's gitignore keeps it out of view. Use this for
   anything that already lives elsewhere.

2. **Git submodule** — `git submodule add <url> projects/<name>`. Submodules
   are recorded in `.gitmodules` and pinned to a specific commit. Use this
   when you want this repo's history to capture the dependency.

3. **In-tree work** — write code directly under `projects/<name>/` and either
   `git add -f` the files you want to track, or add a per-path exception to
   `.gitignore` (e.g. `!projects/my-thing/`). Use sparingly; if the work
   grows, promote it to its own repo.

## What goes here vs. elsewhere

- `projects/` is for code with its own lifecycle.
- `knowledge/` is for curated notes that outlive any single project.
- `.git-ignored/` is for transient artifacts that shouldn't survive at all.
