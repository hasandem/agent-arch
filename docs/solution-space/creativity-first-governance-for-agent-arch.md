# Creativity-First Governance for Agent-Arch

## Agent-sammendrag

The creativity-first direction identifies a real weakness in the current
method: too much workflow friction can make agents optimize for passing gates
instead of solving the right problem well. The proposed plan, however, goes too
far by replacing the repository's core method with a new local knowledge
product. The recommended direction is to keep the current normative architecture
workflow, reduce friction in front of it, and add only a small, optional,
agent-universal memory layer built from plain files and simple shell/Python
entrypoints.

## Problem

The current method is built around:

- `arch-intake`
- `arch-consume`
- `arch-escalate`
- `arch-governance`
- hooks, policy scripts, and controlled installation via `solution-standard`

That fits the repository's original purpose well, but it can also become too
sequential and too heavy in repositories where agents need fast local progress.

The creativity-first proposal tries to solve this by introducing:

- local `arch-knowledge` CLI
- automatic knowledge capture and synthesis
- `arch-context`, `arch-compliance`, and `arch-propose`
- removal of existing workflow skills and blocking hooks

The question is not whether friction exists. It does. The question is whether
the proposed replacement still serves the original method.

## Context

- **Repository role:** central architecture repository for a reusable method
- **Primary assets today:** `arch-read`, install manifests, policy scripts,
  hooks, architecture workflow skills
- **Core promise to consumer repos:** controlled local method surface, not a
  second evolving product with its own lifecycle
- **Key constraint from the user:** the technical mechanism should be simple,
  low-dependency, and usable with "all" agent types

## Status

- [ ] Exploratory
- [x] Selected for pilot
- [ ] Recommended pattern
- [ ] Superseded
- [ ] Rejected

## Alternatives Considered

### Option A: Replace the current method with the full creativity-first plan

Implement `arch-knowledge`, remove `arch-intake`, `arch-consume`,
`arch-escalate`, remove the arch-compatible workflow wrappers, and treat
post-hoc compliance plus a local knowledge base as the new default method.

### Option B: Keep the current method and add a minimal optional context cache

Preserve `arch-read`, `arch-consume`, `arch-escalate`, `arch-governance`,
`solution-standard`, and the existing enforcement chain. Add a very small local
context mechanism that helps agents orient faster, but does not replace the
normative workflow or become a new source of truth.

### Option C: Keep the current method unchanged

Treat the friction as acceptable and reject any new local context or memory
mechanism.

## Chosen Solution

Choose Option B.

The repository should not replace its core method with a local memory compiler.
That would change the product from "reusable architecture governance method" to
"cross-agent local architecture memory system", which is a different and much
harder thing to get right.

At the same time, the current method should acknowledge the valid critique:
agents need a lighter-weight way to get enough context early without being
forced through an overly ceremonial sequence every time.

The right move is therefore:

- keep the current normative flow and names
- reduce unnecessary gating and duplicated steps
- add a small optional context cache as support, not as replacement
- keep compliance and escalation traceable and explicit

## Behold / Endre / Forkast

### Behold

- `arch-read` as the primary way to read canonical architecture
- `arch-consume`, `arch-escalate`, and `arch-governance` as the normative flow
- controlled installation through `solution-standard`
- hooks and shared scripts as the enforcement chain
- solution-space as the place to explore alternative workflow ideas

### Endre

- reduce the feeling of hard sequencing in solution repositories
- make `arch-consume` cheaper to use for small tasks
- allow lightweight context preparation before full compliance-sensitive work
- keep compliance checks focused on meaningful boundaries instead of every
  possible interaction
- make guidance more agent-neutral where possible, but without dropping the
  existing method vocabulary

### Forkast

- deleting `arch-intake`, `arch-consume`, and `arch-escalate`
- replacing the method with `arch-context`, `arch-compliance`, and
  `arch-propose` as the new default vocabulary
- turning this repository into a general-purpose local knowledge compiler
- adding a heavy LLM-driven `flush -> compile -> lint` subsystem as the main
  runtime path
- making local synthesized knowledge a peer or replacement to canonical
  architecture

## Technical Assessment

### What the concept should be technically

If we keep any part of the creativity-first idea, it should be a thin support
layer with these properties:

- plain markdown and text files
- shell-first entrypoints, with small Python helpers only where parsing is
  genuinely easier
- no mandatory background services
- no agent SDK dependency
- no mandatory database
- no mandatory external API call for the base workflow

That means the universal interface should remain:

- files
- shell commands
- git hooks only where they are deterministic and low-risk

### Recommended minimal mechanism

Use a two-layer model, not the proposed three-stage compiler system:

1. **Canonical context**
   Read from central architecture using existing `arch-read`.
2. **Local context cache**
   Store a small local file in the consumer repository, for example:
   `docs/arch-local/context.md` or `.github/agent-arch/context.md`

That local cache should contain only:

- current task context
- relevant links to canonical docs
- local assumptions and open questions
- traceability links to issue/PR/intake/solution-space records

This gives agents one cheap place to orient, without inventing a parallel
knowledge system.

### Recommended commands

If a CLI extension is desired, keep it minimal and deterministic:

- `arch-read` stays as-is for canonical reading
- `arch-context refresh` generates or updates the small local context file
- `arch-context show` prints the local context summary
- `arch-context clear` resets stale local context

These commands can be shell scripts with tiny Python helpers if needed. They do
not need LLM calls to be useful.

### What to avoid technically

- mandatory `flush` on every session event
- automatic compile pipelines that rewrite local knowledge articles
- health scoring systems that create another governance surface to maintain
- provider abstraction, LLM config, and synthesis logic in the core path
- platform-specific hook logic as the primary mechanism

Those ideas are attractive conceptually, but they create a large operational
surface, many failure modes, and a second source of truth.

## Cross-Agent Compatibility

The design should assume the lowest common denominator:

- an agent can read files
- an agent can run shell commands
- an agent may or may not support rich hooks
- an agent may or may not have stable long-term memory

Therefore the order of preference should be:

1. Plain files
2. Shell commands
3. Git hooks as optional automation
4. Agent-specific adapters as thin convenience layers

This keeps Claude Code, Codex, Cursor, Copilot, and future tools on roughly
the same contract.

## Guardrails and Assumptions

- canonical architecture must remain the only normative source of truth
- local context files are supportive and disposable
- local context must point back to canonical documents and traceability records
- any reusable pattern discovered locally still moves through normal escalation
- the method should optimize for low operational burden before cleverness

## Business Impact

Preserves the repository's original value proposition while reducing the risk
of turning it into an over-engineered side system.

## Information Impact

Keeps canonical and local information roles clearly separated: canonical
architecture remains authoritative, while local context remains temporary and
task-oriented.

## Application Impact

Improves agent usability across tools by relying on file and shell conventions
instead of rich platform-specific integrations.

## Next Step

Write a much smaller follow-up design for:

- simplifying `arch-consume` and related workflow friction
- introducing one optional local context cache
- defining the exact file location and shell contract for that cache
- validating the approach in one pilot repository before changing
  `solution-standard`

## Traceability

- **Related issue:** not yet created
- **Related ADR:** not yet created
- **Related normative architecture update:** none yet; this remains
  solution-space until piloted
