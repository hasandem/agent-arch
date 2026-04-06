---
name: agent-arch-install
description: 'Use when installing or updating the controlled agent-arch method surface in a solution repository. Applies a named profile from the public agent-arch repository instead of copying files manually.'
---

# Agent Arch Install

## When To Use

- When bootstrapping a new solution repository with the arch method
- When updating an existing solution repository to the latest approved method surface
- When checking which method files are centrally managed versus local to the solution repository

## Procedure

1. Use the approved profile `solution-standard`. No other solution-repository profile is normative at this time.
2. Run `scripts/agent-arch-install.sh --repo <owner>/agent-arch --profile solution-standard` in the target repository.
3. Review the installed manifest at `.github/agent-arch/solution-standard.manifest`.
4. Treat files listed in that manifest as centrally managed method files.
5. Do not copy additional method files manually into the solution repository.
6. If `solution-standard` is missing something, change that profile in the central `agent-arch` repository instead of patching the consumer repository ad hoc.

## Output Expectations

- The repository gets the exact approved file set from `solution-standard`
- Installed method files remain traceable to the `solution-standard` manifest
- Local repository work relates only to the installed method surface, not the full central repository