#!/bin/bash
# Double-click to run AI Pre-Scan. macOS.
#
# Sets itself up on first run and starts straight away on every run after. Picks demo mode
# automatically when no API keys are present, so this works for someone who has just cloned the
# repository and configured nothing.

set -uo pipefail
cd "$(dirname "$0")" || exit 1

RED=$'\033[31m'; GRN=$'\033[32m'; DIM=$'\033[2m'; OFF=$'\033[0m'
KEY_STORE="$HOME/.config/ironhack/.env.local"
PORT=8000

pause_and_exit() {
  echo
  echo "${DIM}Press any key to close this window.${OFF}"
  read -n 1 -s
  exit "${1:-1}"
}

echo "AI Pre-Scan"
echo "${DIM}$(pwd)${OFF}"
echo

# ── Python ───────────────────────────────────────────────────────────────────
PY=""
for c in python3.12 python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)' 2>/dev/null; then
      PY="$c"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "${RED}Python 3.12 or newer is required and was not found.${OFF}"
  echo "Install it from https://www.python.org/downloads/ and double-click this file again."
  pause_and_exit 1
fi

# ── Environment ──────────────────────────────────────────────────────────────
if [ ! -d .venv ]; then
  echo "First run — setting up. This takes a couple of minutes and only happens once."
  "$PY" -m venv .venv || { echo "${RED}Could not create the environment.${OFF}"; pause_and_exit 1; }
fi

echo "Checking dependencies…"
if ! ./.venv/bin/pip install -q -e . 2>/tmp/ai-prescan-install.log; then
  echo "${RED}Install failed.${OFF} Details:"
  tail -15 /tmp/ai-prescan-install.log
  pause_and_exit 1
fi

# Only needed for live scans, and only downloaded once.
if [ -f "$KEY_STORE" ] && ! ./.venv/bin/python -c 'import playwright' 2>/dev/null; then
  ./.venv/bin/python -m playwright install chromium >/dev/null 2>&1 || true
fi

# ── Live or demo ─────────────────────────────────────────────────────────────
MODE_ARG="--demo"
MODE_TEXT="demo mode ${DIM}(sample data — no API keys found)${OFF}"
if [ -f "$KEY_STORE" ] \
   && grep -q '^OPENAI_API_KEY=' "$KEY_STORE" 2>/dev/null \
   && grep -q '^PINECONE_API_KEY=' "$KEY_STORE" 2>/dev/null; then
  MODE_ARG=""
  MODE_TEXT="live research ${DIM}(API keys found)${OFF}"
fi

echo
echo "${GRN}Starting in ${MODE_TEXT}"
echo "${GRN}Opening http://127.0.0.1:${PORT}${OFF}"
echo "${DIM}Close this window, or press Control-C, to stop.${OFF}"
echo

( sleep 3; open "http://127.0.0.1:${PORT}" >/dev/null 2>&1 ) &

# shellcheck disable=SC2086
./.venv/bin/ai-prescan-web $MODE_ARG --port "$PORT"
STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo
  echo "${RED}AI Pre-Scan stopped unexpectedly (exit $STATUS).${OFF}"
  echo "If the port is already in use, close the other window and try again."
  pause_and_exit $STATUS
fi
