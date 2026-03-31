#!/usr/bin/env bash
# arch-read — Intelligent leser for arch-repo dokumenter
# Henter spesifikke seksjoner fra markdown-filer basert på lesenivå.
#
# Bruk:
#   arch-read <fil>                    # Nivå 2: Agent-sammendrag
#   arch-read <fil> --løsning          # Nivå 3: Sammendrag + Løsningsarkitektur
#   arch-read <fil> --full             # Nivå 4: Hele dokumentet
#   arch-read <fil> --seksjon <navn>   # Spesifikk seksjon
#   arch-read --index <lag>            # Nivå 1: INDEX.md for et lag
#   arch-read --search <søkeord>       # Søk i alle agent-sammendrag
#
# Eksempler:
#   arch-read fiat/informasjon/fhir/consent.md
#   arch-read fiat/informasjon/fhir/consent.md --løsning
#   arch-read --index informasjon
#   arch-read --search "MedicationRequest"

set -euo pipefail

ARCH_DIR="${ARCH_DIR:-/tmp/arch}"

# ─── Farger (kun hvis terminal) ───────────────────────────────────
if [ -t 1 ]; then
    DIM='\033[2m'
    BOLD='\033[1m'
    CYAN='\033[36m'
    YELLOW='\033[33m'
    RESET='\033[0m'
else
    DIM='' BOLD='' CYAN='' YELLOW='' RESET=''
fi

# ─── Hjelpefunksjoner ────────────────────────────────────────────

usage() {
    cat <<EOF
${BOLD}arch-read${RESET} — Les arch-repo dokumenter konteksteffektivt

${BOLD}BRUK:${RESET}
  arch-read <fil>                    Agent-sammendrag (nivå 2)
  arch-read <fil> --løsning          Sammendrag + løsning (nivå 3)
  arch-read <fil> --mål              Sammendrag + målarkitektur (nivå 4)
  arch-read <fil> --full             Hele dokumentet
  arch-read <fil> --seksjon <navn>   Spesifikk seksjon (fuzzy match)
  arch-read --index <lag>            INDEX.md for et lag (nivå 1)
  arch-read --search <søkeord>       Søk i alle agent-sammendrag
  arch-read --list                   Vis alle lag og INDEX-filer
  arch-read --tokens <fil>           Estimer tokens for seksjoner

${BOLD}MILJØVARIABLER:${RESET}
  ARCH_DIR    Sti til arch-repo (default: /tmp/arch)
EOF
    exit 0
}

# Hent en navngitt seksjon fra en markdown-fil.
# Returnerer alt mellom ## <seksjonsnavn> og neste ## (eller EOF).
extract_section() {
    local file="$1"
    local section="$2"

    awk -v section="$section" '
    BEGIN { found=0; IGNORECASE=1 }
    /^## / {
        if (found) exit
        # Fjern "## " og trailing whitespace for matching
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

# Hent agent-sammendraget. Prøver flere vanlige overskrifter.
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

    # Fallback: Hent alt mellom første ## og andre ##
    awk '
    BEGIN { count=0 }
    /^## / { count++; if (count == 2) exit; next }
    count == 1 { print }
    ' "$file"
}

# Hent løsningsarkitektur-seksjonen
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

    echo "${DIM}(Ingen løsningsarkitektur-seksjon funnet)${RESET}" >&2
}

# Hent målarkitektur-seksjonen
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

    echo "${DIM}(Ingen målarkitektur-seksjon funnet)${RESET}" >&2
}

# Fuzzy seksjonssøk — finn seksjoner som matcher delvis (h2 og h3)
extract_fuzzy_section() {
    local file="$1"
    local query="$2"

    awk -v query="$query" '
    BEGIN { found=0; level=0; IGNORECASE=1 }
    /^##+ / {
        # Tell antall # for å finne nivå
        match($0, /^#+/)
        current_level = RLENGTH
        if (found) {
            # Stopp hvis vi treffer samme eller høyere nivå
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

# Vis INDEX.md for et lag
show_index() {
    local layer="$1"
    local index_file=""

    # Prøv å finne INDEX.md i ulike plasseringer
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
        echo "Fant ikke INDEX.md for lag '${layer}'" >&2
        echo "Tilgjengelige lag:" >&2
        list_layers >&2
        exit 1
    fi

    cat "$index_file"
}

# Søk i alle agent-sammendrag
search_summaries() {
    local query="$1"
    local found=0

    # Søk i alle .md-filer under ARCH_DIR
    while IFS= read -r -d '' file; do
        summary=$(extract_agent_summary "$file" 2>/dev/null)
        if echo "$summary" | grep -qi "$query"; then
            found=1
            # Relativ sti for lesbarhet
            rel_path="${file#${ARCH_DIR}/}"
            echo -e "${BOLD}${CYAN}═══ ${rel_path} ═══${RESET}"
            echo "$summary" | grep -i --color=auto "$query" || echo "$summary"
            echo ""
        fi
    done < <(find "$ARCH_DIR" -name "*.md" -not -path "*/.git/*" -print0 2>/dev/null)

    if [ "$found" -eq 0 ]; then
        echo "Ingen agent-sammendrag inneholder '${query}'" >&2
        exit 1
    fi
}

# List tilgjengelige lag
list_layers() {
    echo -e "${BOLD}Tilgjengelige lag i ${ARCH_DIR}:${RESET}"
    for dir in "${ARCH_DIR}"/fiat/*/  "${ARCH_DIR}"/sikkerhet/ "${ARCH_DIR}"/impl-migrasjon/ "${ARCH_DIR}"/motivasjon/ "${ARCH_DIR}"/strategi/; do
        if [ -d "$dir" ]; then
            layer=$(basename "$dir")
            if [ -f "${dir}INDEX.md" ]; then
                echo -e "  ${CYAN}${layer}${RESET} — INDEX.md finnes"
            else
                echo -e "  ${DIM}${layer}${RESET} — mangler INDEX.md"
            fi
        fi
    done
}

# Estimer token-bruk per seksjon (grov: ~4 tegn per token)
estimate_tokens() {
    local file="$1"
    echo -e "${BOLD}Token-estimat for: ${file}${RESET}\n"

    for section in "Agent-sammendrag" "Løsningsarkitektur" "Målarkitektur" "Referanser"; do
        content=$(extract_section "$file" "$section" 2>/dev/null)
        if [ -n "$content" ]; then
            chars=$(echo "$content" | wc -c)
            tokens=$((chars / 4))
            echo -e "  ${section}: ~${tokens} tokens (${chars} tegn)"
        fi
    done

    total_chars=$(wc -c < "$file")
    total_tokens=$((total_chars / 4))
    echo -e "\n  ${BOLD}Totalt: ~${total_tokens} tokens${RESET}"
}

# ─── Resolve filsti ──────────────────────────────────────────────

resolve_path() {
    local input="$1"

    # Hvis filen finnes som gitt, bruk den
    if [ -f "$input" ]; then
        echo "$input"
        return
    fi

    # Prøv relativ til ARCH_DIR
    if [ -f "${ARCH_DIR}/${input}" ]; then
        echo "${ARCH_DIR}/${input}"
        return
    fi

    # Prøv under fiat/
    if [ -f "${ARCH_DIR}/fiat/${input}" ]; then
        echo "${ARCH_DIR}/fiat/${input}"
        return
    fi

    echo ""
}

# ─── Hovedlogikk ─────────────────────────────────────────────────

# Ingen argumenter
if [ $# -eq 0 ]; then
    usage
fi

# Parse argumenter
case "$1" in
    -h|--help)
        usage
        ;;
    --index)
        [ $# -lt 2 ] && { echo "Bruk: arch-read --index <lag>" >&2; exit 1; }
        show_index "$2"
        ;;
    --search)
        [ $# -lt 2 ] && { echo "Bruk: arch-read --search <søkeord>" >&2; exit 1; }
        search_summaries "$2"
        ;;
    --list)
        list_layers
        ;;
    *)
        # Første argument er filsti
        FILE=$(resolve_path "$1")
        if [ -z "$FILE" ]; then
            echo "Fant ikke fil: $1" >&2
            echo "Prøvde: $1, ${ARCH_DIR}/$1, ${ARCH_DIR}/fiat/$1" >&2
            exit 1
        fi

        shift
        MODE="${1:---sammendrag}"

        case "$MODE" in
            --sammendrag|"")
                echo -e "${DIM}[Nivå 2: Agent-sammendrag — ${FILE}]${RESET}\n"
                extract_agent_summary "$FILE"
                echo -e "\n${DIM}[Bruk --løsning for implementasjonsdetaljer, --full for alt]${RESET}"
                ;;
            --løsning|--losning|--solution)
                echo -e "${DIM}[Nivå 3: Sammendrag + Løsning — ${FILE}]${RESET}\n"
                echo -e "${BOLD}── Agent-sammendrag ──${RESET}"
                extract_agent_summary "$FILE"
                echo -e "\n${BOLD}── Løsningsarkitektur ──${RESET}"
                extract_solution "$FILE"
                ;;
            --mål|--maal|--target)
                echo -e "${DIM}[Nivå 4: Sammendrag + Mål — ${FILE}]${RESET}\n"
                echo -e "${BOLD}── Agent-sammendrag ──${RESET}"
                extract_agent_summary "$FILE"
                echo -e "\n${BOLD}── Målarkitektur ──${RESET}"
                extract_target "$FILE"
                ;;
            --full)
                echo -e "${DIM}[Nivå 4: Full — ${FILE}]${RESET}\n"
                cat "$FILE"
                ;;
            --seksjon|--section)
                SECTION="${2:-}"
                [ -z "$SECTION" ] && { echo "Bruk: arch-read <fil> --seksjon <navn>" >&2; exit 1; }
                echo -e "${DIM}[Seksjon: ${SECTION} — ${FILE}]${RESET}\n"
                result=$(extract_fuzzy_section "$FILE" "$SECTION")
                if [ -n "$result" ]; then
                    echo "$result"
                else
                    echo "Fant ikke seksjon '${SECTION}' i ${FILE}" >&2
                    echo "Tilgjengelige seksjoner:" >&2
                    grep "^## " "$FILE" | sed 's/^## /  /' >&2
                    exit 1
                fi
                ;;
            --tokens)
                estimate_tokens "$FILE"
                ;;
            *)
                echo "Ukjent flagg: $MODE" >&2
                usage
                ;;
        esac
        ;;
esac
