#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
. "$ROOT_DIR/scripts/common.sh"

repo_name=$(current_repo_name)
layer="informasjon"
title=""
scope=""
execute=0
change_class=$(sh "$ROOT_DIR/scripts/arch-policy.sh" classify-change)

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
        --scope)
            scope=$2
            shift 2
            ;;
        --title)
            title=$2
            shift 2
            ;;
        --execute)
            execute=1
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [ "$change_class" = "C" ]; then
    echo "Class C change should not go directly to PR. Create an issue first." >&2
    exit 1
fi

branch="agent/${repo_name}/${layer}/${scope:-proposal}"

command=$(cat <<EOF
git checkout -b "$branch"
gh pr create \
  --repo myorg/arch \
  --title "[$layer] ${title:-Proposal from $repo_name}" \
  --label "arch-proposal,auto-agent,lag-$layer"
EOF
)

if [ "$execute" -eq 1 ]; then
    eval "$command"
    exit 0
fi

printf '%s\n' "$command"
