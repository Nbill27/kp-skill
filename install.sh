#!/bin/sh
# Install the Bina Insani KP skill into an agent skills directory.
# Default target is Hermes (~/.hermes/skills). Pass --codebuddy for CodeBuddy.
set -e

TARGET="$HOME/.hermes/skills"
AGENT="Hermes"

if [ "$1" = "--codebuddy" ]; then
  TARGET="$HOME/.codebuddy/skills"
  AGENT="CodeBuddy"
fi

if [ ! -d "skills" ]; then
  echo "Run this script from the repo root." >&2
  exit 1
fi

mkdir -p "$TARGET"
cp -r skills/* "$TARGET/"

echo "Installed into $TARGET ($AGENT):"
ls "$TARGET" | grep -E "^kerja-praktek-bina-insani$"
echo "Verify with: hermes skills list"
