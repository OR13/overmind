#!/usr/bin/env bash
# Build the dynamic system prompt for overmind agents.
#
# Concatenates, in order:
#   1. AGENTS.md            (static entry contract)
#   2. memory/*.md          (public, evolutionary; top-level only)
#   3. memory/private/*.md  (private, if the private memory repo is cloned there)
#
# Top-level *.md only at each layer — nested directories (e.g.
# memory/playbooks/, memory/private/<topic>/) are on-demand reference and
# are not auto-loaded.
#
# Files missing on disk are silently skipped.
#
# Usage:
#   scripts/build-system-prompt.sh
#
# Typical use via the `overmind` alias:
#   claude --append-system-prompt "$($OVERMIND_ROOT/scripts/build-system-prompt.sh)"

set -euo pipefail

ROOT="${OVERMIND_ROOT:-}"
if [ -z "$ROOT" ]; then
  ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [ -z "$ROOT" ] || [ ! -f "$ROOT/AGENTS.md" ]; then
  echo "build-system-prompt.sh: cannot find overmind root (set OVERMIND_ROOT)" >&2
  exit 1
fi

emit_file() {
  local path="$1"
  local rel="${path#"$ROOT"/}"
  printf '\n<!-- begin: %s -->\n' "$rel"
  cat "$path"
  printf '\n<!-- end: %s -->\n' "$rel"
}

emit_dir() {
  local dir="$1"
  [ -d "$dir" ] || return 0
  # Top-level *.md only, sorted by filename.
  # README.md is a github-navigation file, not prompt content — skip it.
  local f base
  for f in "$dir"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    case "$base" in
      README.md) continue ;;
    esac
    emit_file "$f"
  done
}

emit_file "$ROOT/AGENTS.md"
emit_dir "$ROOT/memory"
emit_dir "$ROOT/memory/private"
