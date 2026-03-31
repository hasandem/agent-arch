#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
. "$ROOT_DIR/scripts/common.sh"

sanitize_python_env
files=$(changed_files || true)

if [ -z "$files" ]; then
    exit 0
fi

if ! printf '%s\n' "$files" | grep -Eq '^(motivasjon/|strategi/|forretning/|informasjon/|applikasjon/|teknologi/|fysisk/|sikkerhet/|impl-migrasjon/|adrs/|views/|registry/)'; then
    exit 0
fi

if ! sh "$ROOT_DIR/scripts/validate-docs.sh"; then
    emit_posttool_block "Dokumentkontrakt feilet"
    exit 0
fi

if [ -f "$ROOT_DIR/registry/services.yaml" ] && ! sh "$ROOT_DIR/scripts/find-affected-services.sh" --registry "$ROOT_DIR/registry/services.yaml" --validate-only; then
    emit_posttool_block "Registry-validering feilet"
    exit 0
fi

exit 0
