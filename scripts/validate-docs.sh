#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/common.sh"

ROOT_DIR=$(repo_root)
errors=0

collect_docs() {
    for layer in motivasjon strategi forretning informasjon applikasjon teknologi fysisk sikkerhet impl-migrasjon; do
        if [ -d "$ROOT_DIR/$layer" ]; then
            find "$ROOT_DIR/$layer" -type f -name '*.md'
        fi
    done
}

validate_file() {
    file=$1

    case "$(basename "$file")" in
        INDEX.md|README.md|template.md)
            return 0
            ;;
    esac

    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -le 30 ]; then
        return 0
    fi

    if ! awk '
        BEGIN {
            expected[1] = "## Agent-sammendrag"
            expected[2] = "## Løsningsarkitektur"
            expected[3] = "## Målarkitektur"
            expected[4] = "## Referanser"
            current_h2 = ""
            error = 0
            count = 0
        }
        /^## / {
            count++
            headings[count] = $0
            current_h2 = $0
        }
        /^### / {
            key = current_h2 SUBSEP $0
            if (++seen_h3[key] > 1) {
                error = 1
            }
        }
        END {
            idx = 1
            for (i = 1; i <= count; i++) {
                if (headings[i] == expected[idx]) {
                    idx++
                }
            }
            if (idx != 5) {
                error = 1
            }
            exit error
        }
    ' "$file"; then
        echo "Invalid document contract: $file" >&2
        errors=$((errors + 1))
    fi
}

files=$(collect_docs 2>/dev/null || true)

if [ -z "$files" ]; then
    exit 0
fi

while IFS= read -r file; do
    [ -n "$file" ] || continue
    validate_file "$file"
done <<EOF
$files
EOF

if [ "$errors" -gt 0 ]; then
    exit 1
fi
