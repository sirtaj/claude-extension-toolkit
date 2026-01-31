#!/bin/bash
# Quick update check for SessionStart hook
# Outputs a brief message if extensions may need updates
#
# Usage: Called by SessionStart hook, receives JSON via stdin
# Output: Brief status message or empty for no issues

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$TOOLKIT_ROOT/data/version-manifest.json"

# Read stdin (hook input) but we don't need it for this check
cat > /dev/null

# Check if manifest exists
if [[ ! -f "$MANIFEST" ]]; then
    exit 0
fi

# Check last sync date
last_sync=$(jq -r '.last_docs_sync // empty' "$MANIFEST" 2>/dev/null)
if [[ -z "$last_sync" ]]; then
    echo "[extension-toolkit] Docs have never been synced. Run /extension-sync to update."
    exit 0
fi

# Check if sync is older than 7 days
if command -v python3 &> /dev/null; then
    days_old=$(python3 -c "
from datetime import datetime, timezone
try:
    last = datetime.fromisoformat('$last_sync'.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    print((now - last).days)
except:
    print(-1)
")
    if [[ "$days_old" -ge 7 ]]; then
        echo "[extension-toolkit] Docs cache is ${days_old} days old. Consider running /extension-sync."
    fi
fi

# Quick check for deprecated patterns in recently modified files
# Only check files modified in last 24 hours to keep it fast
if command -v find &> /dev/null && command -v grep &> /dev/null; then
    deprecated_found=0

    # Check for old env var patterns in shell scripts
    while IFS= read -r -d '' file; do
        if grep -qE '\$TOOL_INPUT|\$TOOL_OUTPUT|\$TOOL_NAME' "$file" 2>/dev/null; then
            deprecated_found=1
            break
        fi
    done < <(find ~/.claude -name "*.sh" -mtime -1 -print0 2>/dev/null)

    if [[ "$deprecated_found" -eq 1 ]]; then
        echo "[extension-toolkit] Deprecated patterns detected in hook scripts. Run /extension-optimizer to check."
    fi
fi

exit 0
