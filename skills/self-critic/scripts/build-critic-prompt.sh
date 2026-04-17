#!/usr/bin/env bash
# Build a critic prompt from the given harshness level and work sample.
# Usage: bash build-critic-prompt.sh [paranoid|reasonable|chill] [file-or-stdin]
set -euo pipefail

LEVEL="${1:-reasonable}"
INPUT="${2:-}"

# Read work sample from file or stdin
if [[ -n "$INPUT" && -f "$INPUT" ]]; then
  WORK=$(cat "$INPUT")
elif [[ ! -t 0 ]]; then
  WORK=$(cat)
else
  WORK="(no work sample provided)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/../references"

case "$LEVEL" in
  paranoid|reasonable|chill)
    SYSTEM=$(cat "$PROMPTS_DIR/$LEVEL.md")
    ;;
  *)
    echo "Unknown level: $LEVEL. Use: paranoid, reasonable, chill" >&2
    exit 1
    ;;
esac

cat <<EOF
$SYSTEM

---

## Work to Critique

$WORK

---

Respond with your critique using the standard format:
🔴 Wrong | 🟡 Risky | 🟠 Smelly | 🔵 Missing | 🟢 Better Way | Summary
EOF
