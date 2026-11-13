#!/bin/sh
# Install the Bina Insani KP skill into an agent skills directory.
#
# Usage: ./install.sh [--hermes | --claude | --opencode | --codex | --codebuddy]
# With no flag the target is Hermes (~/.hermes/skills).
set -e

usage() {
  cat <<'EOF'
Usage: ./install.sh [option]

  --claude      Claude Code   ~/.claude/skills
  --opencode    OpenCode      ~/.config/opencode/skills
  --codex       Codex         ~/.agents/skills
  --hermes      Hermes        ~/.hermes/skills   (default)
  --codebuddy   CodeBuddy     ~/.codebuddy/skills
  -h, --help    Show this message

For project scope, copy skills/kerja-praktek-bina-insani into the
agent's project directory (.claude/skills, .opencode/skills,
.agents/skills, .codebuddy/skills) inside your repository instead.
EOF
}

TARGET="$HOME/.hermes/skills"
AGENT="Hermes"
VERIFY="hermes skills list"

case "$1" in
  "" | --hermes)
    ;;
  --claude)
    TARGET="$HOME/.claude/skills"
    AGENT="Claude Code"
    VERIFY="run /skills inside claude"
    ;;
  --opencode)
    TARGET="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"
    AGENT="OpenCode"
    VERIFY="mention @kerja-praktek-bina-insani in a prompt"
    ;;
  --codex)
    TARGET="$HOME/.agents/skills"
    AGENT="Codex"
    VERIFY="run /skills in the Codex CLI"
    ;;
  --codebuddy)
    TARGET="$HOME/.codebuddy/skills"
    AGENT="CodeBuddy"
    VERIFY="check the CodeBuddy skills list"
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    usage >&2
    exit 1
    ;;
esac

if [ ! -d "skills/kerja-praktek-bina-insani" ]; then
  echo "Run this script from the repo root." >&2
  exit 1
fi

mkdir -p "$TARGET"
cp -r skills/kerja-praktek-bina-insani "$TARGET/"

echo "Installed $AGENT skill into $TARGET:"
ls "$TARGET"
echo "Verify: $VERIFY"
