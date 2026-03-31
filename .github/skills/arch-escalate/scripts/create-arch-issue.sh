#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
. "$ROOT_DIR/scripts/common.sh"

repo_name=$(current_repo_name)
layer="I"
title="Trenger avklaring"
body=""
execute=0

while [ $# -gt 0 ]; do
    case "$1" in
        --repo)
            repo_name=$2
            shift 2
            ;;
        --layer)
            layer=$2
            shift 2
            ;;
        --title)
            title=$2
            shift 2
            ;;
        --body)
            body=$2
            shift 2
            ;;
        --execute)
            execute=1
            shift
            ;;
        *)
            echo "Ukjent argument: $1" >&2
            exit 1
            ;;
    esac
done

command=$(cat <<EOF
gh issue create \
  --repo myorg/arch \
  --template arch-request.md \
  --title "[$layer] $title" \
  --label "arch-request,auto-agent" \
  --body "Repo: $repo_name

$body"
EOF
)

if [ "$execute" -eq 1 ]; then
    eval "$command"
    exit 0
fi

printf '%s\n' "$command"
