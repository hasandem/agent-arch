---
name: arch-writing-plans
description: 'Use when an approved design must be turned into an implementation plan for architecture-sensitive work. Adapts Superpowers planning to the arch method with repo-aware tasks, escalation points, and explicit validation steps.'
---

# Arch Writing Plans

## When To Use

- After a design has been approved
- When the work spans multiple steps, files, repos, or reviews
- When the plan must show where architecture reading, escalation, and validation happen

## Procedure

1. Confirm the plan starts from approved design and current architecture context.
2. Break the work into small, testable tasks with exact file paths and verification steps.
3. For every task, say which repository it belongs to and whether it is:
   - local implementation
   - blocked by another solution repository
   - blocked by normative architecture that requires `arch-escalate`
4. Include validation commands that match this method.
   - In this repository, use `sh scripts/arch-policy.sh validate-local`.
   - In solution repositories, use the repo's local test and validation commands plus any `arch-read`-based checks that matter to the task.
5. Mark any task that would create or change normative architecture as an escalation point instead of implementation work.
6. Keep the plan lean.
   - No mandatory worktree steps unless the user asks for isolated workspaces.
   - No mandatory TDD language unless the team already works that way.
   - No default `docs/superpowers/` paths.

## Output Expectations

- Tasks are actionable without hidden assumptions
- Repo boundaries and dependency edges are explicit
- Governance checkpoints appear before risky changes, not after