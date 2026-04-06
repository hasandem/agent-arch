---
name: arch-consume
description: 'Use when implementing or reviewing work in a solution repository that must follow central architecture. Reads the right architecture layers, checks security context, and classifies impact before code changes.'
---

# Arch Consume

## When To Use

- Before architecture-sensitive implementation in a solution repository
- When a task may affect shared contracts, FHIR models, APIs, or security
- When the agent must decide whether a need is local or should be escalated
- When a relevant solution-space record already exists and should inform concrete work

## Procedure

1. Run [resolve context](./scripts/resolve-context.sh) to locate the central architecture repository and normalize the local shell environment.
2. Run [classify impact](./scripts/classify-impact.sh) to get a first-pass A/B/C classification.
3. Read the relevant architecture layers in the order described in [reading order](./references/reading-order.md).
4. If a relevant solution-space record exists, read it to understand alternatives, guardrails, and the chosen solution.
5. If the need cannot be solved locally without changing normative architecture, switch to `arch-escalate`.
