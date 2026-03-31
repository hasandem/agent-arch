---
name: arch-escalate
description: 'Use when work in a solution repository reveals a gap, ambiguity, or improvement need in the central architecture. Creates architecture issues by default, and only prepares direct PRs when the policy class allows it.'
---

# Arch Escalate

## When To Use

- A solution repository discovers a missing contract, unclear standard, or reusable improvement
- The agent needs to choose between opening an issue and preparing a direct PR to the architecture repository
- A local deviation needs to be escalated and traced

## Procedure

1. Run [create architecture issue](./scripts/create-arch-issue.sh) as the default action.
2. Use [prepare architecture PR](./scripts/prepare-arch-pr.sh) only when policy class A, or explicitly approved class B, applies.
3. Use [change classes](./references/change-classes.md) to decide whether the change is low, moderate, or high risk.
