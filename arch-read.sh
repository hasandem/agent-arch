#!/usr/bin/env bash
# arch-read — Intelligent reader for arch-repo documents
# Extracts specific sections from markdown files based on reading level.
#
# Usage:
#   arch-read <file>                    # Level 2: Agent summary
#   arch-read <file> --solution         # Level 3: Summary + Solution Architecture
#   arch-read <file> --full             # Level 4: Full document
#   arch-read <file> --section <name>   # Specific section
#   arch-read --index <layer>           # Level 1: INDEX.md for a layer
#   arch-read --search <query>          # Search all agent summaries
#
# Examples:
#   arch-read fiat/informasjon/fhir/consent.md
#   arch-read fiat/informasjon/fhir/consent.md --solution
#   arch-read --index informasjon
#   arch-read --search "MedicationRequest"

set -euo pipefail

ARCH_DIR="${ARCH_DIR:-/tmp/arch}"

# ─── Colors (only if terminal) ─────────────────────────────────────
if [ -t 1 ]; then
    DIM='\033[2m'
    BOLD='\033[1m'
    CYAN='\033[36m'
    YELLOW='\033[33m'
    RESET='\033[0m'
else
    DIM='' BOLD='' CYAN='' YELLOW='' RESET=''
fi

# ─── Helper functions ──────────────────────────────────────────────

usage() {
    cat <<EOF
${BOLD}arch-read${RESET} — Read arch-repo documents context-efficiently

${BOLD}USAGE:${RESET}
  arch-read <file>                    Agent summary (level 2)
  arch-read <file> --solution          Summary + solution (level 3)
  arch-read <file> --target             Summary + target architecture (level 4)
  arch-read <file> --full             Full document
  arch-read <file> --section <name>   Specific section (fuzzy match)
  arch-read --index <layer>           INDEX.md for a layer (level 1)
  arch-read --search <query>          Search all agent summaries
  arch-read --list                    Show all layers and INDEX files
  arch-read --tokens <file>           Estimate tokens per section

${BOLD}ENVIRONMENT VARIABLES:${RESET}
  ARCH_DIR    Path to arch-repo (default: /tmp/arch)
EOF
    exit 0
}

# Extract a named section from a markdown file.
# Returns everything between ## <section name> and the next ## (or EOF).
extract_section() {
    local file="$1"
    local section="$2"

    awk -v section="$section" '
    BEGIN { found=0; IGNORECASE=1 }
    /^## / {
        if (found) exit
        # Remove "## " and trailing whitespace for matching
        header = $0
        sub(/^## */, "", header)
        sub(/ *$/, "", header)
        if (tolower(header) == tolower(section)) {
            found=1
            next
        }
    }
    found { print }
    ' "$file"
}

# Extract the agent summary. Tries several common headings.
extract_agent_summary() {
    local file="$1"
    local result=""

    for heading in "Agent-sammendrag" "Agent sammendrag" "Sammendrag" "TL;DR" "Summary"; do
        result=$(extract_section "$file" "$heading")
        if [ -n "$result" ]; then
            echo "$result"
            return 0
        fi
    done

    # Fallback: Get everything between first ## and second ##
    awk '
    BEGIN { count=0 }
    /^## / { count++; if (count == 2) exit; next }
    count == 1 { print }
    ' "$file"
}

# Extract the solution architecture section
extract_solution() {
    local file="$1"
    local result=""

    for heading in "Løsningsarkitektur" "Losningsarkitektur" "Solution Architecture" "Løsning" "Implementasjon"; do
        result=$(extract_section "$file" "$heading")
        if [ -n "$result" ]; then
            echo "$result"
            return 0
        fi
    done

    echo "${DIM}(No solution architecture section found)${RESET}" >&2
}

# Extract the target architecture section
extract_target() {
    local file="$1"
    local result=""

    for heading in "Målarkitektur" "Maalarkitektur" "Target Architecture" "Mål" "As-is / To-be"; do
        result=$(extract_section "$file" "$heading")
        if [ -n "$result" ]; then
            echo "$result"
            return 0
        fi
    done

    echo "${DIM}(No target architecture section found)${RESET}" >&2
}

# Fuzzy section search — find sections that partially match (h2 and h3)
extract_fuzzy_section() {
    local file="$1"
    local query="$2"

    awk -v query="$query" '
    BEGIN { found=0; level=0; IGNORECASE=1 }
    /^##+ / {
        # Count # to find level
        match($0, /^#+/)
        current_level = RLENGTH
        if (found) {
            # Stop if we hit same or higher level
            if (current_level <= level) exit
        }
        if (index(tolower($0), tolower(query)) > 0) {
            found=1
            level=current_level
            print $0
            next
        }
    }
    found { print }
    ' "$file"
}

# Show INDEX.md for a layer
show_index() {
    local layer="$1"
    local index_file=""

    # Try to find INDEX.md in various locations
    for candidate in \
        "${ARCH_DIR}/fiat/${layer}/INDEX.md" \
        "${ARCH_DIR}/${layer}/INDEX.md" \
        "${ARCH_DIR}/fiat/${layer}/index.md" \
        "${ARCH_DIR}/${layer}/index.md"; do
        if [ -f "$candidate" ]; then
            index_file="$candidate"
            break
        fi
    done

    if [ -z "$index_file" ]; then
        echo "INDEX.md not found for layer '${layer}'" >&2
        echo "Available layers:" >&2
        list_layers >&2
        exit 1
    fi

    cat "$index_file"
}

# Search all agent summaries
search_summaries() {
    local query="$1"
    local found=0

    # Search all .md files under ARCH_DIR
    while IFS= read -r -d '' file; do
        summary=$(extract_agent_summary "$file" 2>/dev/null)
        if echo "$summary" | grep -qi "$query"; then
            found=1
            # Relative path for readability
            rel_path="${file#${ARCH_DIR}/}"
            echo -e "${BOLD}${CYAN}═══ ${rel_path} ═══${RESET}"
            echo "$summary" | grep -i --color=auto "$query" || echo "$summary"
            echo ""
        fi
    done < <(find "$ARCH_DIR" -name "*.md" -not -path "*/.git/*" -print0 2>/dev/null)

    if [ "$found" -eq 0 ]; then
        echo "No agent summaries contain '${query}'" >&2
        exit 1
    fi
}

# List available layers
list_layers() {
    echo -e "${BOLD}Available layers in ${ARCH_DIR}:${RESET}"
    for dir in "${ARCH_DIR}"/fiat/*/  "${ARCH_DIR}"/sikkerhet/ "${ARCH_DIR}"/impl-migrasjon/ "${ARCH_DIR}"/motivasjon/ "${ARCH_DIR}"/strategi/; do
        if [ -d "$dir" ]; then
            layer=$(basename "$dir")
            if [ -f "${dir}INDEX.md" ]; then
                echo -e "  ${CYAN}${layer}${RESET} — INDEX.md exists"
            else
                echo -e "  ${DIM}${layer}${RESET} — INDEX.md missing"
            fi
        fi
    done
}

# Estimate token usage per section (rough: ~4 chars per token)
estimate_tokens() {
    local file="$1"
    echo -e "${BOLD}Token estimate for: ${file}${RESET}\n"

    for section in "Agent-sammendrag" "Løsningsarkitektur" "Målarkitektur" "Referanser"; do
        content=$(extract_section "$file" "$section" 2>/dev/null)
        if [ -n "$content" ]; then
            chars=$(echo "$content" | wc -c)
            tokens=$((chars / 4))
            echo -e "  ${section}: ~${tokens} tokens (${chars} chars)"
        fi
    done

    total_chars=$(wc -c < "$file")
    total_tokens=$((total_chars / 4))
    echo -e "\n  ${BOLD}Total: ~${total_tokens} tokens${RESET}"
}

# ─── Resolve file path ──────────────────────────────────────────

resolve_path() {
    local input="$1"

    # If the file exists as given, use it
    if [ -f "$input" ]; then
        echo "$input"
        return
    fi

    # Try relative to ARCH_DIR
    if [ -f "${ARCH_DIR}/${input}" ]; then
        echo "${ARCH_DIR}/${input}"
        return
    fi

    # Try under fiat/
    if [ -f "${ARCH_DIR}/fiat/${input}" ]; then
        echo "${ARCH_DIR}/fiat/${input}"
        return
    fi

    echo ""
}

# ─── Main logic ──────────────────────────────────────────────────

    # No arguments
if [ $# -eq 0 ]; then
    usage
fi

    # Parse arguments
case "$1" in
    -h|--help)
        usage
        ;;
    --index)
        [ $# -lt 2 ] && { echo "Usage: arch-read --index <layer>" >&2; exit 1; }
        show_index "$2"
        ;;
    --search)
        [ $# -lt 2 ] && { echo "Usage: arch-read --search <keyword>" >&2; exit 1; }
        search_summaries "$2"
        ;;
    --list)
        list_layers
        ;;
    *)
        # First argument is file path
        FILE=$(resolve_path "$1")
        if [ -z "$FILE" ]; then
            echo "File not found: $1" >&2
            echo "Tried: $1, ${ARCH_DIR}/$1, ${ARCH_DIR}/fiat/$1" >&2
            exit 1
        fi

        shift
        MODE="${1:---summary}"

        case "$MODE" in
            --summary|--sammendrag|"")
                echo -e "${DIM}[Level 2: Agent summary — ${FILE}]${RESET}\n"
                extract_agent_summary "$FILE"
                echo -e "\n${DIM}[Use --solution for implementation details, --full for everything]${RESET}"
                ;;
            --løsning|--losning|--solution)
                echo -e "${DIM}[Level 3: Summary + Solution — ${FILE}]${RESET}\n"
                echo -e "${BOLD}── Agent summary ──${RESET}"
                extract_agent_summary "$FILE"
                echo -e "\n${BOLD}── Solution architecture ──${RESET}"
                extract_solution "$FILE"
                ;;
            --mål|--maal|--target)
                echo -e "${DIM}[Level 4: Summary + Target — ${FILE}]${RESET}\n"
                echo -e "${BOLD}── Agent summary ──${RESET}"
                extract_agent_summary "$FILE"
                echo -e "\n${BOLD}── Target architecture ──${RESET}"
                extract_target "$FILE"
                ;;
            --full)
                echo -e "${DIM}[Level 4: Full — ${FILE}]${RESET}\n"
                cat "$FILE"
                ;;
            --seksjon|--section)
                SECTION="${2:-}"
                [ -z "$SECTION" ] && { echo "Usage: arch-read <file> --section <name>" >&2; exit 1; }
                echo -e "${DIM}[Section: ${SECTION} — ${FILE}]${RESET}\n"
                result=$(extract_fuzzy_section "$FILE" "$SECTION")
                if [ -n "$result" ]; then
                    echo "$result"
                else
                    echo "Section '${SECTION}' not found in ${FILE}" >&2
                    echo "Available sections:" >&2
                    grep "^## " "$FILE" | sed 's/^## /  /' >&2
                    exit 1
                fi
                ;;
            --tokens)
                estimate_tokens "$FILE"
                ;;
            *)
                echo "Unknown flag: $MODE" >&2
                usage
                ;;
        esac
        ;;
esac
