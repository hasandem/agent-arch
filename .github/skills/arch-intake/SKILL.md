---
name: arch-intake
description: 'Use when a solution repository must first be understood and aligned before implementation. Captures alternatives, chosen solutions, and reusable learning in intake briefs and solution-space records.'
---

# Arch Intake

## When To Use

- Before implementation when a repository must first be understood
- When aligning an existing solution repository with central architecture
- When learning from a legacy, pilot, or third-party repository
- When the first need is to understand alternatives and chosen solutions, not to write code immediately

## Procedure

1. Infer the intake mode first: `legacy`, `pilot`, or `third-party`.
2. Run a short clarification round and ask for:
   - the source documents that should anchor the first pass
   - whether the round is about concept exploration, normative clarification, or production hardening
   - the first evaluation unit
   - the first deliverable
3. Create or update an intake brief using the repository's chosen template.
4. Evaluate one explicit unit at a time across business, information, and application together.
5. Capture alternatives, chosen solution, rejected options, and guardrails in a solution-space record.
6. If the work becomes concrete implementation, switch to `arch-consume`.
7. If the work reveals a reusable architecture gap or improvement, switch to `arch-escalate`.

## Output Expectations

- Keep the first deliverable small and traceable
- Make the mode and status explicit
- Separate pilot experimentation from normative architecture
- Use repository-native artifacts such as intake briefs and solution-space records instead of ad hoc notes