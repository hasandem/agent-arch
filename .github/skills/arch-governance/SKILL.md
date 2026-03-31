---
name: arch-governance
description: 'Use in the central architecture repository to validate document contracts, enforce issue and PR policy, run pre-tool and post-tool checks, and keep architecture changes inside approved governance rules.'
---

# Arch Governance

## When To Use

- When editing the central architecture repository
- Before commit, push, or PR creation in architecture-sensitive work
- When validating document contracts, registry references, and issue traceability

## Procedure

1. Let hooks call [pre-tool gate](./scripts/pre-tool-gate.sh) automatically before risky actions.
2. Let hooks call [post-tool validate](./scripts/post-tool-validate.sh) after relevant edits.
3. Use [require issue link](./scripts/require-issue-link.sh) when a protected change must be traced.
4. Follow the decision rules in [policy matrix](./references/policy-matrix.md).
