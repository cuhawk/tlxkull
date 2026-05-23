#!/opt/homebrew/bin/bash
# Install + load the target-discover launchd job. Idempotent.
set -euo pipefail

cd "$(dirname "$0")/../../.."   # repo root
REPO_ROOT="$(pwd)"
LABEL="com.tlx.target-discover"
SRC="routines/target-discover/launchd/${LABEL}.plist"
DST="$HOME/Library/LaunchAgents/${LABEL}.plist"

# render plist with absolute repo path
mkdir -p "$HOME/Library/LaunchAgents"
sed "s|__REPO_ROOT__|${REPO_ROOT}|g" "$SRC" > "$DST"
chmod 644 "$DST"

# reload (idempotent: bootout missing is non-fatal)
launchctl bootout "gui/$UID/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$UID" "$DST"
launchctl enable "gui/$UID/${LABEL}"

echo "installed: $DST"
echo "next fire: 07:00 local"
echo "verify  : launchctl print gui/$UID/${LABEL}"
echo "run-now : launchctl kickstart -k gui/$UID/${LABEL}"
