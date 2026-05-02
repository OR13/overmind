---
name: memory-defrag
description: Audit overmind's memory tiers (public top-level + nested, private top-level + nested if mounted), recommend splits / merges / renames toward Letta's 15–25 focused-files-per-tier target, and apply changes only with explicit approval.
---

## Memory defragmentation

Audit the memory tiers, identify drift (oversized files, near-duplicate
small files, stale frontmatter, unreferenced files), propose changes, and
apply only the user-approved subset.

## Execution

### Step 1: Inventory

Walk each tier and list every `*.md` file with:
- path
- line count
- frontmatter `name` and `description` (or "MISSING" if no frontmatter)
- last-modified date (`git log -1 --format=%cI -- <path>` for tracked files)

Tiers, in order:

1. `overmind/memory/*.md` (public, top-level — auto-loaded)
2. `overmind/memory/<topic>/...` (public, nested — on-demand; skip
   `memory/private/` here, it's the private tier)
3. `overmind/memory/private/*.md` (private, top-level; skip if path missing)
4. `overmind/memory/private/<topic>/...` (private, nested; skip if path missing)

Print one summary table per tier:

```
| File | Lines | Last modified | Frontmatter |
```

Then per-tier counts vs. the 15–25 target.

### Step 2: Detect issues

For each file, flag any of:

- **OVERSIZED** — body > 200 lines. Candidate for split.
- **TINY** — body < 10 lines. Candidate for merge into a sibling.
- **NO_FRONTMATTER** — missing `name`/`description`.
- **STALE_DESCRIPTION** — description doesn't match the body content
  (skim body, compare to the description field).
- **DUPLICATE** — two or more files in the same tier whose `description`
  fields are >70% similar by content. Candidates for merge.
- **MISPLACED** — content reads as on-demand reference but lives at
  top-level `memory/` (auto-loaded), or vice versa. (Heuristic:
  top-level files should describe conventions, registries, or active
  state; nested files describe playbooks, references, or domain notes.)

### Step 3: Propose actions

For each issue, propose a concrete action:

- **Split**: list proposed new file names with one-line descriptions of
  what each will contain.
- **Merge**: list source files and the proposed merged file.
- **Rename / move**: source → destination.
- **Frontmatter fix**: show old and new frontmatter.

Group proposals by tier. Show a per-tier summary (current file count →
projected file count after defrag).

### Step 4: Approval

Use AskUserQuestion (multi-select) to let the user pick which proposals
to apply. Default to "review individually" rather than "approve all" —
defrag is destructive enough to be worth eyeballing.

### Step 5: Apply

For each approved action:
- Write / edit / move files via Write, Edit, or `git mv`.
- Preserve git history when renaming (`git mv`, not delete + write).
- After each tier is done, stage and commit with one commit per tier:
  - `memory: defrag — split foo.md into a.md + b.md`
  - `memory: defrag — merge x.md and y.md`
  - private commits use the same convention but in the private repo.

Do not push.

### Step 6: Verify

Re-run the inventory step and print the post-defrag table. Confirm each
tier is now within the 15–25 file target (or report which tiers are
still over and why — sometimes the right call is to keep more).
