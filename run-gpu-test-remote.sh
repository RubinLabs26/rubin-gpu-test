#!/usr/bin/env bash
set -Eeuo pipefail

RAW_SCRIPT="https://gist.githubusercontent.com/itzlalpekhlua/d3f580ddf4b5aaa677e77a2f7abda3ba/raw/gpu_test.py"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python 3 is required. Install it with your distribution package manager." >&2
  exit 1
fi

curl --fail --location --silent --show-error "$RAW_SCRIPT" | "$PYTHON" - "$@"
