#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/common.sh"

classify_change() {
    files=$(changed_files || true)

    if [ -z "$files" ]; then
        printf 'A\n'
        return 0
    fi

    layer_count=$(count_changed_layers)

    if printf '%s\n' "$files" | grep -Eq '^(motivasjon/prinsipper/|strategi/|sikkerhet/|impl-migrasjon/veikart/)'; then
        printf 'C\n'
        return 0
    fi

    if [ "$layer_count" -ge 3 ]; then
        printf 'C\n'
        return 0
    fi

    if printf '%s\n' "$files" | grep -Eq '^(registry/services\.yaml|adrs/|forretning/|informasjon/|applikasjon/|teknologi/|fysisk/|sikkerhet/per-lag/|views/)'; then
        printf 'B\n'
        return 0
    fi

    printf 'A\n'
}

validate_local() {
    sanitize_python_env

    if [ -f "$SCRIPT_DIR/validate-docs.sh" ]; then
        sh "$SCRIPT_DIR/validate-docs.sh"
    fi

    if [ -f "$(repo_root)/registry/services.yaml" ] && [ -f "$SCRIPT_DIR/find-affected-services.sh" ]; then
        sh "$SCRIPT_DIR/find-affected-services.sh" \
            --registry "$(repo_root)/registry/services.yaml" \
            --validate-only
    fi
}

session_start() {
    sanitize_python_env
    arch_dir=$(default_arch_dir)

    if [ -d "$arch_dir" ]; then
        emit_system_message "ARCH_DIR er tilgjengelig: $arch_dir"
        return 0
    fi

    emit_system_message "ARCH_DIR finnes ikke lokalt ennå. Klon myorg/arch til $arch_dir ved arkitekturrelevante oppgaver."
}

pre_tool() {
    sanitize_python_env
    payload=$(cat)
    compact_payload=$(printf '%s' "$payload" | tr '\n' ' ')
    change_class=$(classify_change)

    if printf '%s' "$compact_payload" | grep -Fq 'gh pr create' && printf '%s' "$compact_payload" | grep -Fq 'myorg/arch'; then
        case "$change_class" in
            C)
                emit_pretool_decision "deny" "Klasse C-endring krever issue og koordinering før PR"
                return 0
                ;;
            B)
                emit_pretool_decision "ask" "Klasse B-endring krever eksplisitt vurdering før PR"
                return 0
                ;;
        esac
    fi

    if printf '%s' "$compact_payload" | grep -Fq 'git push'; then
        if ! validate_local >/dev/null 2>&1; then
            emit_pretool_decision "deny" "Lokal validering må bestå før push"
            return 0
        fi
    fi

    if has_protected_changes && ! has_issue_reference "$compact_payload"; then
        emit_pretool_decision "ask" "Endringer i beskyttede områder bør ha issue-referanse"
        return 0
    fi

    emit_pretool_decision "allow" "Ingen policy-blokkering"
}

usage() {
    cat <<EOF
Bruk: arch-policy.sh <session-start|classify-change|pre-tool|validate-local>
EOF
}

command_name=${1:-}

case "$command_name" in
    session-start)
        session_start
        ;;
    classify-change)
        classify_change
        ;;
    pre-tool)
        pre_tool
        ;;
    validate-local)
        validate_local
        ;;
    *)
        usage >&2
        exit 1
        ;;
esac
