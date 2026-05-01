# tools/

Executable scripts for this workspace. Three languages are wired into CI
here: TypeScript (via Bun), Python (via uv), and Bash. Files in any of
those languages dropped into this directory are validated by
`tools/check.sh` and the GitHub Actions workflow at
`.github/workflows/ci.yml`.

## What gets validated

| Language | Lint / format     | Types   | Tests    |
|----------|-------------------|---------|----------|
| TS / JS  | Biome             | tsc     | bun test |
| Python   | ruff (check+fmt)  | pyright | pytest   |
| Bash     | shellcheck, shfmt | —       | —        |

If a language has no files in the tree, its gates are skipped — the
check is a no-op rather than a failure.

## Local check

```sh
tools/check.sh
```

Runs the same gates CI runs. Use it before pushing.

## Adding a script

1. Drop the file under `tools/` (or anywhere outside `projects/` and
   `.git-ignored/`).
2. Run `tools/check.sh` locally.
3. Commit when green.

## Bootstrap on a fresh checkout

```sh
bun install   # installs Biome, TypeScript, @types/bun
uv sync       # creates .venv with ruff, pyright, pytest
```

Both `node_modules/` and `.venv/` are gitignored. The lockfiles
(`bun.lock`, `uv.lock`) are tracked.

## Tooling versions

Pinned in `package.json` (Biome, TypeScript), `pyproject.toml` (ruff,
pyright, pytest), and resolved against `bun.lock` / `uv.lock`. CI
installs the lockfile-pinned versions; bumping is a deliberate edit.
