# overmind — shell integration. Source this from your ~/.zshrc or
# ~/.bashrc to expose the `overmind` command in interactive shells:
#
#   source ~/overmind/scripts/overmind.sh
#
# If you cloned overmind somewhere other than ~/overmind, set
# OVERMIND_ROOT before sourcing:
#
#   export OVERMIND_ROOT=/path/to/overmind
#   source "$OVERMIND_ROOT/scripts/overmind.sh"
#
# Then in any shell:
#
#   overmind            # default backend (claude)
#   overmind gemini     # explicit gemini
#   overmind claude     # explicit claude
#   OVERMIND_BACKEND=gemini overmind
#
# Plain POSIX-ish — works in both bash and zsh.

: "${OVERMIND_ROOT:=$HOME/overmind}"
export OVERMIND_ROOT

overmind() {
  "$OVERMIND_ROOT/scripts/overmind" "$@"
}
