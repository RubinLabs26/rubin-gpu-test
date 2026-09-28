#!/usr/bin/env bash
set -Eeuo pipefail

RAW_SCRIPT="https://gist.githubusercontent.com/itzlalpekhlua/d3f580ddf4b5aaa677e77a2f7abda3ba/raw/gpu_test.py"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  if [ -n "${TERMUX_VERSION:-}" ]; then
    echo "Python 3 is required in Termux. Install it with: pkg update && pkg install python" >&2
  else
    echo "Python 3 is required. Install it with your distribution package manager." >&2
  fi
  exit 1
fi

TEMP_SCRIPT="$(mktemp -t rubin-gpu-test.XXXXXX.py)"
cleanup() { rm -f "$TEMP_SCRIPT"; }
trap cleanup EXIT
curl --fail --location --silent --show-error "$RAW_SCRIPT" -o "$TEMP_SCRIPT"

if [ -t 1 ] && [ -r /dev/tty ]; then
  "$PYTHON" "$TEMP_SCRIPT" "$@" </dev/tty
else
  "$PYTHON" "$TEMP_SCRIPT" "$@"
fi
