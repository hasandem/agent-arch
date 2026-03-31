#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)

sh "$ROOT_DIR/scripts/arch-policy.sh" session-start
