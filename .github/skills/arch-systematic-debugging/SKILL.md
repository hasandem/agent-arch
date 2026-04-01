---
name: arch-systematic-debugging
description: 'Use when debugging bugs, test failures, build failures, integration issues, or unexpected behavior in an architecture-sensitive context. Adapts Superpowers systematic debugging and verification-before-completion to the arch method.'
---

# Arch Systematic Debugging

## When To Use

- When a bug, failing test, build break, integration issue, or unexpected behavior needs investigation
- When there is pressure to apply a quick fix without understanding the cause
- When repeated fixes have failed or the issue may indicate a deeper architectural problem

## Core Rules

1. No fix before root cause investigation.
2. No completion claim without fresh verification evidence.
3. If the issue reveals a gap in normative architecture, escalate it explicitly instead of hiding it inside a local patch.

## Procedure

1. Start with architecture context.
   - In a solution repository, use `arch-consume` before changing architecture-sensitive code.
   - In this repository, use `arch-governance` before changing protected documents, hooks, or policy scripts.
2. Investigate root cause before proposing fixes.
   - Read the full error output carefully.
   - Reproduce the issue consistently.
   - Check recent changes, configuration, and environment differences.
   - In multi-component flows, gather evidence at component boundaries to find where behavior diverges.
3. Analyze patterns before editing.
   - Find working examples in the same codebase.
   - Compare broken and working behavior directly.
   - List differences instead of assuming which ones matter.
4. Form one hypothesis at a time.
   - State the hypothesis clearly.
   - Test it with the smallest possible change.
   - If it fails, form a new hypothesis rather than stacking fixes.
5. Implement only after the root cause is understood.
   - Reproduce the issue with a test or another repeatable verification step whenever practical.
   - Fix the root cause, not the symptom.
   - Avoid unrelated cleanup while debugging.
6. Verify before claiming success.
   - Identify the exact command or step that proves the claim.
   - Run it fresh after the change.
   - Read the output and exit status.
   - Only then say the issue is fixed, tests pass, or the build is green.
7. Escalate architectural issues when the debugging evidence points there.
   - If three or more fix attempts fail, stop and question the architecture.
   - In a solution repository, use `arch-escalate` if the real issue is a missing contract, unclear standard, or broken architectural assumption.
   - In this repository, pause before further edits and review the policy implications with `arch-governance`.

## Red Flags

- "Just try this quickly"
- "It probably works now"
- "Let's bundle a few fixes"
- "I will verify later"
- "The agent says it succeeded"
- "One more attempt" after multiple failed fixes

Any of these means stop and go back to investigation.

## Output Expectations

- State the observed failure before proposing a remedy.
- Distinguish evidence, hypothesis, and fix.
- Report fresh verification evidence before any success claim.
- Call out when the debugging result is really an escalation, not a local fix.