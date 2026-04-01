# Governance and Enforcement

## Goal

The method is only reusable if guidance and enforcement stay aligned.

This repository therefore uses a three-layer control chain:

1. Skills guide the workflow.
2. Hooks enforce deterministic checks before risky actions.
3. CI validates the same rules on PR and merge.

## Core repository roles

### Central architecture repository

Use `arch-governance` for:

- document contract validation
- issue and PR traceability
- protected-area checks
- policy enforcement before push and PR

### Solution repositories

Use `arch-consume` before architecture-sensitive implementation and
`arch-escalate` when local work reveals a gap in normative architecture.

## Change classes

| Class | Typical meaning | Expected flow |
| --- | --- | --- |
| A | Low-risk clarification or additive update | Direct PR may be allowed |
| B | Moderate-risk but still controlled change | Explicit review before PR |
| C | High-risk or cross-layer architectural change | Issue first, then coordinated change |

## Default rules

### Solution repositories

1. Read architecture first.
2. Keep local changes local when possible.
3. Create issues in target repos for cross-repo dependencies.
4. Use `arch-escalate` when shared architecture must change.

### Central architecture repository

1. Use `arch-governance` on architecture-sensitive edits.
2. Let hooks and CI call the same policy scripts.
3. Require stronger review for protected areas like strategy and security.

## Hooks and policy engine

Shared policy belongs in shell entrypoints so the behavior is consistent across
VS Code, Copilot CLI, and CI.

The key files are:

- `.github/hooks/arch-policy.json`
- `scripts/arch-policy.sh`
- `scripts/validate-docs.sh`
- `scripts/find-affected-services.sh`

## Review expectations

- findings first
- explicit residual risk
- policy breaches called out directly
- verification run before completion claims

## Cross-repo coordination

When repo A depends on repo B:

1. Create an issue in repo B where the change must happen.
2. Link back from repo A so the dependency is visible.
3. Escalate to the central architecture repo only if the dependency also reveals
   a normative architecture gap.