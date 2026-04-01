# Superpowers and GitHub Copilot in the Arch Method

## Purpose

This guide explains how to use selected ideas from `obra/superpowers` inside
GitHub Copilot without importing the upstream workflow unchanged.

## Short answer

Yes. Superpowers-style skills can be used with GitHub Copilot even without an
official Superpowers plugin for Copilot.

GitHub Copilot can discover `SKILL.md`-based skills from project and personal
directories such as:

- `.github/skills/`
- `.agents/skills/`
- `~/.copilot/skills/`

## Recommended adoption model

Use a thin compatibility layer:

1. Keep `arch-consume`, `arch-escalate`, and `arch-governance` as the primary architecture workflow.
2. Reuse selected Superpowers ideas only where they strengthen process discipline.
3. Map them into Copilot-native skills and instructions instead of importing upstream behavior unchanged.
4. Keep hooks and `scripts/arch-policy.sh` as the single source of truth for enforcement.

## Recommended mappings

| Superpowers concept | Arch-compatible adoption |
| --- | --- |
| `brainstorming` | `arch-brainstorming` |
| `writing-plans` | `arch-writing-plans` |
| `requesting-code-review` | `arch-requesting-code-review` |
| `systematic-debugging` | `arch-systematic-debugging` |
| `verification-before-completion` | folded into debugging and validation expectations |

## What not to import unchanged

Do not treat these as default policy in this method:

- `using-superpowers` as global controller
- mandatory `using-git-worktrees`
- mandatory TDD wording for every repository
- default `docs/superpowers/` paths
- plugin-specific bootstrap behavior

## License note

`obra/superpowers` is MIT-licensed.

- Reusing ideas and patterns is allowed.
- Copying or adapting substantial material should keep the upstream MIT notice.
- This repository records that notice in `THIRD_PARTY_NOTICES.md`.

## Current compatibility layer in this repository

- `.github/copilot-instructions.md`
- `.github/skills/arch-brainstorming/`
- `.github/skills/arch-writing-plans/`
- `.github/skills/arch-requesting-code-review/`
- `.github/skills/arch-systematic-debugging/`