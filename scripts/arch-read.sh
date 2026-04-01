#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

if [ ! -f "$ROOT_DIR/arch-read.sh" ]; then
    echo "Root script arch-read.sh not found" >&2
    exit 1
fi

exec bash "$ROOT_DIR/arch-read.sh" "$@"
