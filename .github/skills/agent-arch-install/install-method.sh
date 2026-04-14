#!/usr/bin/env sh
set -eu

REPO=${AGENT_ARCH_REPO:-}
REF=${AGENT_ARCH_REF:-main}
PROFILE=${AGENT_ARCH_PROFILE:-solution-standard}
TARGET_DIR=${AGENT_ARCH_TARGET_DIR:-}
SOURCE_ROOT=${AGENT_ARCH_SOURCE_ROOT:-}
DRY_RUN=0
FORCE=0

usage() {
    cat <<EOF
Usage: install-method.sh --repo <owner/repo> [options]

Bootstrap the agent-arch method into the current repository by downloading and
running the central installer.

Options:
  --repo <owner/repo>     Source GitHub repository for the method
  --ref <git-ref>         Git ref to install from (default: main)
  --profile <name>        Install profile (default: solution-standard)
  --target-dir <dir>      Target repository directory (default: detected repo root)
  --source-root <dir>     Read installer from a local checkout instead of GitHub
  --force                 Overwrite existing AGENTS.md or CLAUDE.md
  --dry-run               Forward dry-run to the installer
  -h, --help              Show this help
EOF
}

detect_target_dir() {
    script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
    candidate=$(CDPATH= cd -- "$script_dir/../../.." && pwd)

    if [ -d "$candidate/.git" ] || [ -d "$candidate/.github" ]; then
        printf '%s\n' "$candidate"
        return 0
    fi

    pwd
}

fetch_installer() {
    installer_destination=$1

    if [ -n "$SOURCE_ROOT" ]; then
        cp "$SOURCE_ROOT/scripts/agent-arch-install.sh" "$installer_destination"
        return 0
    fi

    curl -fsSL "https://raw.githubusercontent.com/$REPO/$REF/scripts/agent-arch-install.sh" -o "$installer_destination"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --repo)
            REPO=$2
            shift 2
            ;;
        --ref)
            REF=$2
            shift 2
            ;;
        --profile)
            PROFILE=$2
            shift 2
            ;;
        --target-dir)
            TARGET_DIR=$2
            shift 2
            ;;
        --source-root)
            SOURCE_ROOT=$2
            shift 2
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [ -z "$REPO" ] && [ -z "$SOURCE_ROOT" ]; then
    echo "You must provide --repo <owner/repo> unless --source-root is used" >&2
    exit 1
fi

if [ -z "$TARGET_DIR" ]; then
    TARGET_DIR=$(detect_target_dir)
fi

mkdir -p "$TARGET_DIR/scripts"
INSTALLER_PATH="$TARGET_DIR/scripts/agent-arch-install.sh"

fetch_installer "$INSTALLER_PATH"
chmod 0755 "$INSTALLER_PATH"

set -- sh "$INSTALLER_PATH" --target-dir "$TARGET_DIR" --profile "$PROFILE"

if [ -n "$REPO" ]; then
    set -- "$@" --repo "$REPO"
fi

if [ -n "$SOURCE_ROOT" ]; then
    set -- "$@" --source-root "$SOURCE_ROOT"
fi

if [ "$DRY_RUN" -eq 1 ]; then
    set -- "$@" --dry-run
fi

if [ "$FORCE" -eq 1 ]; then
    set -- "$@" --force
fi

exec "$@"
