#!/opt/homebrew/bin/bash
set -euo pipefail
LABEL="com.tlx.target-discover"
DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl bootout "gui/$UID/${LABEL}" 2>/dev/null || true
rm -f "$DST"
echo "uninstalled: $DST"
