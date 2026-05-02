---
name: memory-reflect
description: Review the current session for durable items worth persisting, route each to public or private memory based on a sensitivity gate, and ask before committing. Implements the "memory reflection" step of the Letta context-repository pattern.
---

## Memory reflection

Walk back through the current session, surface things worth remembering
beyond this conversation, decide where each belongs, and persist them with
explicit user approval.

## Execution

### Step 1: Pull the candidate set

Re-read recent assistant and user turns in this session. Look for:

- **User feedback** ("don't do X", "always do Y", "I prefer Z")
- **Project facts** ("we're freezing merges Thursday", "the auth rewrite
  is driven by compliance")
- **References** ("bugs go to project INGEST in Linear", "the latency
  dashboard is at grafana.internal/d/api-latency")
- **User profile** ("I'm a data scientist focused on observability")
- **Validated approaches** (the user accepted a non-obvious choice
  without pushback — preserve so you don't drift away from it next time)

Skip: ephemeral task state, code patterns derivable from the repo, debug
fixes that the commit message already explains, content already in
`AGENTS.md` or existing `memory/` files.

### Step 2: Sensitivity gate (per item)

For each candidate, decide tier:

- **PRIVATE** if it names or strongly implies any of: a specific person
  (coworkers, customers), an organization, a customer/account, an
  internal product or unreleased feature, a financial figure, a security
  detail, a credential or system path that's meaningful only at the
  user's workplace.
- **PUBLIC** otherwise — generic preferences, generic conventions,
  publicly-known references, abstract guidance.

When in doubt: PRIVATE. The cost of mis-routing public-bound content to
private is small (less reuse); the cost of mis-routing private content
to public is a leak.

### Step 3: Choose destination layer

For each item, choose between top-level `memory/` and a nested
`memory/<topic>/`:

- **Top-level `memory/<name>.md`** — needed on every turn. Active
  conventions, active agents, current workspace state. Auto-loaded into
  the system prompt. Keep tight (≤25 top-level files per tier).
- **Nested `memory/<topic>/<name>.md`** — looked up on demand. Curated
  reference, playbooks, domain notes. Not auto-loaded.

Combined with the tier decision, the four destinations are:

| Tier × Layer | Path |
|---|---|
| PUBLIC top-level | `overmind/memory/<name>.md` |
| PUBLIC nested | `overmind/memory/<topic>/<name>.md` |
| PRIVATE top-level | `overmind/memory/private/<name>.md` |
| PRIVATE nested | `overmind/memory/private/<topic>/<name>.md` |

If `memory/private/` does not exist (private repo not yet cloned), warn
the user and stage private items in a list — do not write them anywhere.
Public items can still be written.

### Step 4: Frontmatter and naming

Every new file gets YAML frontmatter:

```markdown
---
name: <short-kebab-name>
description: <one line — what's in here, when it's relevant>
---

<body>
```

For feedback and project memories, structure the body as:

```markdown
<the rule or fact>

**Why:** <reason / incident / motivation>
**How to apply:** <when this guidance kicks in>
```

Prefer **updating an existing file** over creating a new one. Re-read
the relevant `memory/` directory (top-level or nested) and look for an
existing file whose `description` covers the new item.

### Step 5: Present and confirm

Show the user a numbered list:

```
1. [PUBLIC top-level → overmind/memory/active-context.md] Append:
   <preview of new content>
2. [PRIVATE top-level → overmind/memory/private/identity.md] Create:
   <preview>
3. [PUBLIC nested → overmind/memory/playbooks/...] Update:
   <preview>
```

Use AskUserQuestion (multi-select) to let the user pick which to apply,
or "all", or "none". Show the diff for "update" entries before writing.

### Step 6: Apply and commit

For each approved item:
- Write the file with the Write or Edit tool.
- After all writes for a given repo are done, stage and commit them
  with `git -C <repo> add <paths> && git -C <repo> commit -m "<msg>"`.
  Use one commit per repo (public, private). Commit messages follow the
  `memory: ...` convention.

Do not push. The user pushes when they're ready.

### Step 7: Report

List what was written and committed per repo. If the private repo wasn't
mounted, list the private items as still-pending so the user can paste
them in once they mount the repo.
