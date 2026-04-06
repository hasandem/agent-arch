---
name: arch-brainstorming
description: 'Use when scoping features, behavior changes, architecture changes, or other architecture-sensitive work before implementation. Adapts Superpowers brainstorming to the arch method by requiring architecture context, layer impact, and escalation decisions.'
---

# Arch Brainstorming

## When To Use

- Before proposing implementation for new features or behavior changes
- When the task may affect shared contracts, security, or cross-repo dependencies
- When a user asks for options, trade-offs, or a design recommendation

## Procedure

1. Determine the repository role first.
   - In a solution repository, use `arch-consume` before refining the design.
   - In the central architecture repository, use `arch-governance` before proposing protected changes.
2. Clarify the goal, constraints, success criteria, and whether the work is local or cross-repo.
3. Identify likely ArchiMate layers and security touchpoints before proposing solutions.
4. Present 2-3 approaches with trade-offs.
5. For each approach, state whether it is:
   - local to the current repository
   - an escalation candidate for `arch-escalate`
   - a potential class A/B/C change in the central architecture repository
6. When the discussion is solution-near and likely to be reused, capture the result in a solution-space record.
7. Recommend one approach and explain why it best fits the arch method.
8. If the user approves and the work is multi-step, continue with `arch-writing-plans`.

## Output Expectations

- Lead with the recommended approach
- Make the layer impact explicit
- Call out governance implications early instead of after implementation starts
- Keep design artifacts in repository-native locations; do not default to upstream Superpowers paths