#!/usr/bin/env sh
set -eu

repo_root() {
    git rev-parse --show-toplevel 2>/dev/null || pwd
}

sanitize_python_env() {
    unset VIRTUAL_ENV CONDA_PREFIX CONDA_DEFAULT_ENV PYTHONPATH PYTHONHOME PIP_REQUIRE_VIRTUALENV
}

current_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
}

current_repo_name() {
    basename "$(repo_root)"
}

default_arch_dir() {
    printf '%s\n' "${ARCH_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch}"
}

unique_lines() {
    awk 'NF && !seen[$0]++'
}

changed_files() {
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        return 0
    fi

    {
        if git rev-parse --verify HEAD >/dev/null 2>&1; then
            git diff --name-only --cached HEAD 2>/dev/null || true
        else
            git diff --cached --name-only 2>/dev/null || true
        fi
        git diff --name-only 2>/dev/null || true
    } | unique_lines
}

changed_layers() {
    changed_files \
        | awk -F/ 'NF { print $1 }' \
        | grep -E '^(motivasjon|strategi|forretning|informasjon|applikasjon|teknologi|fysisk|sikkerhet|impl-migrasjon|adrs|views|registry)$' \
        | sort -u
}

count_changed_layers() {
    changed_layers | wc -l | tr -d ' '
}

has_issue_reference() {
    input_text=${1:-}

    if [ -z "$input_text" ]; then
        input_text=$(current_branch)
    fi

    printf '%s\n' "$input_text" | grep -Eq '(^|[^0-9])(#[0-9]+|GH-[0-9]+|issues/[0-9]+|issue-[0-9]+)([^0-9]|$)'
}

has_protected_changes() {
    changed_files | grep -Eq '^(motivasjon/prinsipper/|strategi/|sikkerhet/|impl-migrasjon/veikart/|adrs/)'
}

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

emit_pretool_decision() {
    decision=$(json_escape "$1")
    reason=$(json_escape "$2")

    printf '{\n'
    printf '  "hookSpecificOutput": {\n'
    printf '    "hookEventName": "PreToolUse",\n'
    printf '    "permissionDecision": "%s",\n' "$decision"
    printf '    "permissionDecisionReason": "%s"\n' "$reason"
    printf '  }\n'
    printf '}\n'
}

emit_posttool_block() {
    reason=$(json_escape "$1")
    printf '{\n'
    printf '  "decision": "block",\n'
    printf '  "reason": "%s"\n' "$reason"
    printf '}\n'
}

emit_system_message() {
    message=$(json_escape "$1")
    printf '{\n'
    printf '  "systemMessage": "%s"\n' "$message"
    printf '}\n'
}

normalize_changed_path() {
    printf '%s' "$1" | sed 's#^\./##; s/\.[A-Za-z0-9_-][A-Za-z0-9_.-]*$//'
}
