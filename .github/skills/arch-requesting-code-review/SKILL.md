---
name: arch-requesting-code-review
description: 'Use when reviewing architecture-sensitive changes before push or PR. Adapts Superpowers review to the arch method with findings-first review, change classification, policy checks, and governance traceability.'
---

# Arch Requesting Code Review

## When To Use

- Before push or PR for architecture-sensitive changes
- After completing a substantial implementation task with cross-repo or normative impact
- When a user asks for a review of changes in this repository or a related solution repository

## Procedure

1. Review findings first, ordered by severity.
2. Check whether the change is effectively class A, B, or C against the shared policy.
3. Verify the change is happening in the correct repository.
   - Local solution change stays local.
   - Missing normative architecture becomes `arch-escalate` work.
   - Protected architecture changes in this repository follow `arch-governance`.
4. For this repository, run `sh scripts/arch-policy.sh validate-local` before concluding the change is ready.
5. Call out missing issue links, policy breaches, cross-layer surprises, and security review needs explicitly.
6. Only provide a short summary after findings and open questions.

## Output Expectations

- Findings first
- File and line references where possible
- Explicit residual risk when no findings are discovered