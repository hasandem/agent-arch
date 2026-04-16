---
name: arch-context
description: 'Use in a consuming repository when the main need is insight work, local innovation, or structured analysis against central normative architecture before converging on a solution.'
---

# Arch Context

## When To Use

- When a consuming repository needs insight work before committing to an implementation path
- When comparing local solution options against central normative architecture
- When a team may deliberately choose a local path that differs from the current norm
- When local source material should be ingested into `docs/arch-knowledge/` to support analysis

## Core Rules

1. Read central architecture first as the comparison baseline.
2. Treat local creativity-first knowledge as supportive, not normative.
3. A deliberate local deviation is allowed only when the reasoning is explicit and traceable.
4. If the local learning suggests a reusable improvement, feed it back through `arch-escalate`.

## Procedure

1. Start from canonical context.
   - Read central architecture with `arch-read`.
   - Identify the central documents, principles, and contracts that matter to the local decision.
2. Build local context.
   - Review existing local material under `docs/arch-knowledge/` when present.
   - If the repository has source material worth capturing, add it under `docs/arch-knowledge/raw/`.
   - Use `arch-knowledge flush`, `arch-knowledge compile`, and `arch-knowledge lint` when the repository has enabled local knowledge support.
3. Compare alternatives explicitly.
   - State what the current normative baseline says.
   - State what the local situation requires or reveals.
   - Distinguish follow-the-norm options from deliberate deviation options.
4. Capture deliberate local deviations.
   - Use the local deviation record under `docs/arch-knowledge/deviations/`.
   - Record the baseline, the local decision, the evidence, the tradeoffs, and whether the learning should go back to central architecture.
5. Escalate reusable learning.
   - If the local decision reveals a missing pattern, unclear contract, or better architectural direction, switch to `arch-escalate`.

## Output Expectations

- Make the normative baseline explicit.
- Make any local deviation explicit.
- Keep evidence and tradeoffs readable for both humans and agents.
- Preserve a clear path from local learning to central architectural improvement.