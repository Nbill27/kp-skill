#!/bin/sh
# Install the Bina Insani KP skill into an agent skills directory.
#
# Usage: ./install.sh [--claude | --opencode | --codex | --hermes | --codebuddy | --all]
# With no flag the target is Hermes (~/.hermes/skills).
set -eu

SKILL="kerja-praktek-bina-insani"
SOURCE="skills/$SKILL"

usage() {
  cat <<'EOF'
Usage: ./install.sh [option]

  --claude      Claude Code   ~/.claude/skills
  --opencode    OpenCode      ~/.config/opencode/skills
  --codex       Codex         ~/.agents/skills
  --hermes      Hermes        ~/.hermes/skills   (default)
  --codebuddy   CodeBuddy     ~/.codebuddy/skills
  --all         Install into every agent above
  --uninstall   Remove the installed skill instead of copying it
  --dry-run     Print what would happen, write nothing
  -h, --help    Show this message

Run this script from the repository root. For project scope, copy
skills/kerja-praktek-bina-insani into the agent's project directory
(.claude/skills, .opencode/skills, .agents/skills, .codebuddy/skills)
inside your repository instead.

On Windows, use install.ps1 from PowerShell.
EOF
}

# Each entry is "agent|target|verify hint".
targets() {
  printf '%s\n' \
    "Claude Code|$HOME/.claude/skills|run /skills inside claude" \
    "OpenCode|${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills|mention @$SKILL in a prompt" \
    "Codex|$HOME/.agents/skills|run /skills in the Codex CLI" \
    "Hermes|$HOME/.hermes/skills|hermes skills list" \
    "CodeBuddy|$HOME/.codebuddy/skills|check the CodeBuddy skills list"
}

SELECTED=""
UNINSTALL=0
DRY_RUN=0

add() {
  case "
$SELECTED
" in
    *"
$1
"*) : ;;
    *) SELECTED="${SELECTED}${SELECTED:+
}$1" ;;
  esac
}

for arg in "$@"; do
  case "$arg" in
    --claude) add "Claude Code" ;;
    --opencode) add "OpenCode" ;;
    --codex) add "Codex" ;;
    --hermes) add "Hermes" ;;
    --codebuddy) add "CodeBuddy" ;;
    --all) add "Claude Code"; add "OpenCode"; add "Codex"; add "Hermes"; add "CodeBuddy" ;;
    --uninstall) UNINSTALL=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$SELECTED" ]; then
  SELECTED="Hermes"
fi

if [ ! -d "$SOURCE" ]; then
  echo "Run this script from the repo root: $SOURCE not found." >&2
  exit 1
fi

TARGETS="$(targets)"
HINTS=""

while IFS= read -r agent; do
  [ -n "$agent" ] || continue
  line="$(printf '%s\n' "$TARGETS" | grep "^$agent|" || true)"
  if [ -z "$line" ]; then
    echo "Unknown agent: $agent" >&2
    exit 1
  fi

  target="$(printf '%s' "$line" | cut -d'|' -f2)"
  hint="$(printf '%s' "$line" | cut -d'|' -f3)"
  destination="$target/$SKILL"

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -d "$destination" ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        echo "would remove  $destination"
      else
        rm -rf "$destination"
        echo "removed       $destination"
      fi
    else
      echo "not installed $destination"
    fi
    continue
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "would install $SOURCE -> $destination"
    continue
  fi

  mkdir -p "$target"
  # Remove first so a reinstall cannot leave a file that no longer ships.
  rm -rf "$destination"
  cp -R "$SOURCE" "$target/"
  echo "installed     $destination ($agent)"

  HINTS="${HINTS}${HINTS:+
}  $agent - $hint"
done <<EOF
$SELECTED
EOF

if [ "$DRY_RUN" -eq 1 ]; then
  echo ""
  echo "Dry run: nothing was written."
elif [ "$UNINSTALL" -eq 0 ] && [ -n "$HINTS" ]; then
  printf '\nVerify:\n%s\n' "$HINTS"
fi
