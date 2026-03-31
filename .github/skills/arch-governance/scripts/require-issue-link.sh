#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
. "$ROOT_DIR/scripts/common.sh"

input_text=""

if [ $# -gt 0 ]; then
    input_text=$*
elif [ ! -t 0 ]; then
    input_text=$(cat)
fi

if has_issue_reference "$input_text"; then
    exit 0
fi

echo "Fant ingen issue-referanse i input, branch-navn eller kontekst." >&2
exit 1
