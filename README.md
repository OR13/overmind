# overmind

A personal, file-based coordination system for agentic work — a long-lived
workspace that sits between you, your tools, and the projects you ship.

It is opinionated about structure but vendor-neutral: it uses [AGENTS.md][agents-md]
as the primary onboarding contract for any coding agent, and treats plain
markdown on disk as the durable substrate for memory, references, and active
work.

This repository is maintained by [@OR13](https://github.com/OR13) for personal
use, but the structure is intentionally generic. Fork it, strip it, and make
it yours.

## Layout

```
.
├── AGENTS.md       # how any agent should navigate this repo (open standard)
├── README.md       # this file
├── knowledge/      # curated, version-controlled notes — the "second brain"
├── projects/       # active work; gitignored by default
└── .git-ignored/   # local-only scratch, caches, transient state
```

## How it's used

- **knowledge/** is curated and committed. It's what survives across machines
  and sessions, and what agents are expected to read before acting.
- **projects/** is for active work. The directory is gitignored by default so
  you can clone external repositories, prototype freely, or attach git
  submodules without polluting this repo's history. Track specific work
  explicitly when it's ready.
- **.git-ignored/** is for transient state: agent scratchpads, downloaded
  artifacts, model outputs, partial logs. Nothing in here is ever pushed.

## Agent contract

Coding agents (Claude Code, Codex, Cursor, Aider, and others) should read
[`AGENTS.md`](AGENTS.md) on entry. If your tool expects a different filename,
symlink it so the contract stays in one place:

```sh
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md .cursorrules
```

## Setup for your own copy

```sh
git clone <your-fork> overmind
cd overmind
mkdir -p .git-ignored knowledge projects
```

The structure is the system. Grow it as you need it; prune it when you don't.

## References

- [paperclipai/paperclip][paperclip] — agentic workspace that inspired the
  long-lived, file-based coordination model.
- [How to Build an LLM Knowledge Base][dair-kb] — DAIR.AI's argument for
  curated, structured knowledge as the foundation of useful LLM workflows.
- [AGENTS.md][agents-md] — the open standard for agent onboarding files,
  used here as the primary agent contract.

[paperclip]: https://github.com/paperclipai/paperclip
[dair-kb]: https://academy.dair.ai/blog/how-to-build-an-llm-knowledge-base
[agents-md]: https://agents.md
