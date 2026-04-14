---
name: agent-arch-install
description: 'Use when installing or updating the controlled agent-arch method surface in a solution repository. Applies a named profile from the public agent-arch repository instead of copying files manually.'
argument-hint: '<owner>/agent-arch [ref]'
---

# Agent Arch Install

## When To Use

- When bootstrapping a new solution repository with the arch method
- When updating an existing solution repository to the latest approved method surface
- When checking which method files are centrally managed versus local to the solution repository

## Procedure

1. Use the approved profile `solution-standard`. No other solution-repository profile is normative at this time.
2. If this skill was installed via `npx skills`, run [install-method.sh](./install-method.sh) with `--repo <owner>/agent-arch` so the full local method surface is materialized into the repository.
3. The bootstrap script downloads `scripts/agent-arch-install.sh` into the target repository and runs it with `--profile solution-standard`.
4. Review the installed manifest at `.github/agent-arch/solution-standard.manifest`.
5. Treat files listed in that manifest as centrally managed method files.
6. By default, keep any existing `AGENTS.md` or `CLAUDE.md`; use `--force` only when you intentionally want bootstrap to overwrite them.
7. Do not copy additional method files manually into the solution repository.
8. If `solution-standard` is missing something, change that profile in the central `agent-arch` repository instead of patching the consumer repository ad hoc.

## Output Expectations

- The repository gets the exact approved file set from `solution-standard`
- Installed method files remain traceable to the `solution-standard` manifest
- Existing repository-owned instruction files are preserved unless force-overwrite is requested
- Local repository work relates only to the installed method surface, not the full central repository
