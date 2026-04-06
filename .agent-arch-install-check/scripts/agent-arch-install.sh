#!/usr/bin/env sh
set -eu

PROFILE=${AGENT_ARCH_PROFILE:-solution-standard}
TARGET_DIR=${PWD}
REPO=${AGENT_ARCH_REPO:-}
REF=${AGENT_ARCH_REF:-main}
SOURCE_ROOT=${AGENT_ARCH_SOURCE_ROOT:-}
DRY_RUN=0

usage() {
    cat <<EOF
Usage: agent-arch-install.sh [options]

Install the approved agent-arch method surface into a solution repository.

Options:
  --repo <owner/repo>     Public GitHub repository to install from
  --ref <git-ref>         Git ref to install from (default: main)
  --profile <name>        Install profile (default: solution-standard)
  --target-dir <dir>      Target repository directory (default: current directory)
  --source-root <dir>     Read files from a local checkout instead of GitHub
  --dry-run               Print planned file operations without writing files
  -h, --help              Show this help

Environment variables:
  AGENT_ARCH_REPO
  AGENT_ARCH_REF
  AGENT_ARCH_PROFILE
  AGENT_ARCH_SOURCE_ROOT
EOF
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "Required command not found: $1" >&2
        exit 1
    }
}

fetch_to_stdout() {
    relative_path=$1

    if [ -n "$SOURCE_ROOT" ]; then
        source_path="$SOURCE_ROOT/$relative_path"
        if [ ! -f "$source_path" ]; then
            echo "Source file not found: $source_path" >&2
            exit 1
        fi
        cat "$source_path"
        return 0
    fi

    if [ -z "$REPO" ]; then
        echo "You must provide --repo <owner/repo> unless --source-root is used" >&2
        exit 1
    fi

    curl -fsSL "https://raw.githubusercontent.com/$REPO/$REF/$relative_path"
}

install_entry() {
    source_path=$1
    target_path=$2
    mode=$3
    destination="$TARGET_DIR/$target_path"
    destination_dir=$(dirname "$destination")
    temp_file="$destination.agent-arch.$$"

    printf '%s -> %s\n' "$source_path" "$target_path"

    if [ "$DRY_RUN" -eq 1 ]; then
        return 0
    fi

    mkdir -p "$destination_dir"
    fetch_to_stdout "$source_path" > "$temp_file"
    chmod "$mode" "$temp_file"
    mv "$temp_file" "$destination"
}

write_source_metadata() {
    metadata_dir="$TARGET_DIR/.github/agent-arch"
    metadata_file="$metadata_dir/source.env"
    temp_file="$metadata_file.agent-arch.$$"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf '%s\n' ".github/agent-arch/source.env <- repo metadata"
        return 0
    fi

    mkdir -p "$metadata_dir"

    {
        printf 'AGENT_ARCH_SOURCE_REPO=%s\n' "${REPO:-}"
        printf 'AGENT_ARCH_SOURCE_REF=%s\n' "$REF"
    } > "$temp_file"

    chmod 0644 "$temp_file"
    mv "$temp_file" "$metadata_file"
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

if [ -z "$SOURCE_ROOT" ]; then
    require_command curl
fi

manifest_path="install/profiles/$PROFILE.manifest"
manifest_data=$(fetch_to_stdout "$manifest_path")

printf 'Installing agent-arch profile %s into %s\n' "$PROFILE" "$TARGET_DIR"

printf '%s\n' "$manifest_data" | while IFS='|' read -r source_path target_path mode; do
    case "$source_path" in
        ''|'#'*)
            continue
            ;;
    esac

    if [ -z "$target_path" ] || [ -z "$mode" ]; then
        echo "Invalid manifest entry: $source_path|$target_path|$mode" >&2
        exit 1
    fi

    install_entry "$source_path" "$target_path" "$mode"
done

write_source_metadata

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'Dry run completed for profile %s\n' "$PROFILE"
else
    printf 'Installed profile %s\n' "$PROFILE"
fi