#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/common.sh"

ROOT_DIR=$(repo_root)
REGISTRY="$ROOT_DIR/registry/services.yaml"
CHANGED_FILES=""
OUTPUT=""
VALIDATE_ONLY=0

usage() {
    cat <<EOF
Bruk: find-affected-services.sh [--registry <fil>] [--changed-files <fil>] [--output <fil>] [--validate-only]
EOF
}

extract_rows() {
    awk '
        /^services:[[:space:]]*$/ { in_services = 1; next }
        in_services && /^[^[:space:]]/ { in_services = 0 }
        in_services && /^  [A-Za-z0-9_-]+:[[:space:]]*$/ {
            service = $0
            sub(/^  /, "", service)
            sub(/:[[:space:]]*$/, "", service)
            repo = ""
            layer = ""
            next
        }
        in_services && /^    repo:[[:space:]]*/ {
            repo = $0
            sub(/^    repo:[[:space:]]*/, "", repo)
            sub(/^myorg\//, "", repo)
            next
        }
        in_services && /^      [A-Za-z0-9_-]+:[[:space:]]*$/ {
            layer = $0
            sub(/^      /, "", layer)
            sub(/:[[:space:]]*$/, "", layer)
            if (layer == "lag-mapping") {
                layer = ""
            }
            next
        }
        in_services && /^        - / {
            path = $0
            sub(/^        - /, "", path)
            if (service != "" && repo != "" && layer != "") {
                print service "\t" repo "\t" layer "\t" path
            }
        }
    ' "$REGISTRY"
}

mapping_exists() {
    layer=$1
    path=$2

    for candidate in \
        "$ROOT_DIR/$layer/$path" \
        "$ROOT_DIR/$layer/$path.md" \
        "$ROOT_DIR/$layer/$path.json" \
        "$ROOT_DIR/$layer/$path.yaml" \
        "$ROOT_DIR/$layer/$path.yml" \
        "$ROOT_DIR/$layer/$path.ts" \
        "$ROOT_DIR/$layer/$path.sh"; do
        if [ -e "$candidate" ]; then
            return 0
        fi
    done

    return 1
}

validate_registry() {
    rows=$(extract_rows)
    errors=0

    if [ -z "$rows" ]; then
        echo "Registry ser tom ut: $REGISTRY" >&2
        return 1
    fi

    while IFS=$(printf '\t') read -r service repo layer path; do
        [ -n "$service" ] || continue

        case "$layer" in
            motivasjon|strategi|forretning|informasjon|applikasjon|teknologi|fysisk|sikkerhet|impl-migrasjon)
                ;;
            *)
                echo "Ugyldig lag i registry: $layer ($service)" >&2
                errors=$((errors + 1))
                continue
                ;;
        esac

        case "$path" in
            ''|/*|*'..'*)
                echo "Ugyldig sti i registry: $path ($service)" >&2
                errors=$((errors + 1))
                continue
                ;;
        esac

        if [ -d "$ROOT_DIR/$layer" ] && ! mapping_exists "$layer" "$path"; then
            echo "Fant ikke mapping i repoet: $layer/$path ($service)" >&2
            errors=$((errors + 1))
        fi
    done <<EOF
$rows
EOF

    if [ "$errors" -gt 0 ]; then
        return 1
    fi

    return 0
}

match_change() {
    changed_path=$(normalize_changed_path "$1")
    target="$2/$3"

    case "$changed_path" in
        "$target"|"$target"/*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

write_output() {
    if [ -n "$OUTPUT" ]; then
        printf '%s\n' "$1" > "$OUTPUT"
        return 0
    fi

    printf '%s\n' "$1"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --registry)
            REGISTRY=$2
            shift 2
            ;;
        --changed-files)
            CHANGED_FILES=$2
            shift 2
            ;;
        --output)
            OUTPUT=$2
            shift 2
            ;;
        --validate-only)
            VALIDATE_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 1
            ;;
    esac
done

if [ ! -f "$REGISTRY" ]; then
    echo "Fant ikke registry: $REGISTRY" >&2
    exit 1
fi

if [ "$VALIDATE_ONLY" -eq 1 ]; then
    validate_registry
    exit 0
fi

if [ -z "$CHANGED_FILES" ] || [ ! -f "$CHANGED_FILES" ]; then
    echo "Du må angi --changed-files <fil>" >&2
    exit 1
fi

validate_registry

if grep -Fxq 'registry/services.yaml' "$CHANGED_FILES"; then
    repos=$(extract_rows | awk -F '\t' '{ print $2 }' | unique_lines)
    write_output "$repos"
    exit 0
fi

rows=$(extract_rows)
affected=""

while IFS= read -r changed; do
    [ -n "$changed" ] || continue

    while IFS=$(printf '\t') read -r service repo layer path; do
        [ -n "$service" ] || continue

        if match_change "$changed" "$layer" "$path"; then
            affected=$(printf '%s\n%s\n' "$affected" "$repo" | unique_lines)
        fi
    done <<EOF
$rows
EOF
done < "$CHANGED_FILES"

write_output "$(printf '%s\n' "$affected" | unique_lines)"
