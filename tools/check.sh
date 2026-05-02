#!/usr/bin/env bash
# Run lint / format / type / test gates for every language present in
# the tree. Languages with no files are skipped (no-op, not failure).

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

exclude_args=(
  -not -path './node_modules/*'
  -not -path './.git-ignored/*'
  -not -path './projects/*'
  -not -path './.venv/*'
  -not -path './.git/*'
  -not -path './dist/*'
  -not -path './.specify/*'
)

count_files() {
  find . -type f "$@" "${exclude_args[@]}" 2>/dev/null | wc -l | tr -d ' '
}

list_files() {
  find . -type f "$@" "${exclude_args[@]}" 2>/dev/null
}

step() {
  printf '\n== %s\n' "$1"
}

skip() {
  printf -- '-- %s\n' "$1"
}

# --- TypeScript / JavaScript ---
ts_count=$(count_files \( -name '*.ts' -o -name '*.tsx' \))
if [ "$ts_count" -gt 0 ]; then
  step "bun: $ts_count TS file(s)"
  bunx --bun biome lint .
  bunx --bun biome format --check .
  bunx --bun tsc --noEmit
  ts_test_count=$(count_files \( -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' \))
  if [ "$ts_test_count" -gt 0 ]; then
    bun test
  else
    skip "bun test: no test files"
  fi
else
  skip "bun: no TS files"
fi

# --- Python ---
py_count=$(count_files -name '*.py')
if [ "$py_count" -gt 0 ]; then
  step "python: $py_count file(s)"
  uv run ruff check .
  uv run ruff format --check .
  uv run pyright
  py_test_count=$(count_files \( -name 'test_*.py' -o -name '*_test.py' \))
  if [ "$py_test_count" -gt 0 ]; then
    uv run pytest
  else
    skip "pytest: no test files"
  fi
else
  skip "python: no .py files"
fi

# --- Shell ---
mapfile -t sh_files < <(list_files -name '*.sh')
if [ "${#sh_files[@]}" -gt 0 ]; then
  step "shell: ${#sh_files[@]} file(s)"
  shellcheck "${sh_files[@]}"
  shfmt -d -i 2 -ci "${sh_files[@]}"
else
  skip "shell: no .sh files"
fi

printf '\n== all gates passed\n'
