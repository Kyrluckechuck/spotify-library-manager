#!/usr/bin/env bash
set -euo pipefail

# Install repo-tracked git hooks from .githooks into .git/hooks
ROOT_DIR=$(git rev-parse --show-toplevel)
HOOKS_SRC="$ROOT_DIR/.githooks"
HOOKS_DST="$ROOT_DIR/.git/hooks"

if [ ! -d "$HOOKS_SRC" ]; then
  echo "❌ Hooks source directory not found: $HOOKS_SRC"
  exit 1
fi

mkdir -p "$HOOKS_DST"

for hook in pre-commit; do
  if [ -f "$HOOKS_SRC/$hook" ]; then
    echo "🔧 Installing $hook hook..."
    cp "$HOOKS_SRC/$hook" "$HOOKS_DST/$hook"
    chmod +x "$HOOKS_DST/$hook"
  fi
done

echo "✅ Git hooks installed."
