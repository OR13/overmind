# .git-ignored/

Local-only scratch space. Everything in this directory is gitignored except
this README.

Use it for:

- Agent scratchpads and intermediate reasoning artifacts
- Downloaded papers, datasets, model outputs
- Transient logs, traces, partial runs
- Anything you'd otherwise be tempted to delete in five minutes

This directory exists per-machine. A fresh clone gives you only this README.
If something should survive across machines or sessions, promote it to
`memory/` (or `memory/private/`) or to a project under `projects/`.
