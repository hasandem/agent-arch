# Project Guidelines

## Purpose

This repository is the central architecture repository for the shared arch method.
Treat architecture documents, hooks, and policy scripts here as normative.

## Workflow

- In this repository, use `arch-governance` for architecture-sensitive changes.
- In solution repositories, use `arch-consume` before implementation and `arch-escalate` when normative architecture must change.
- For Superpowers-style process support in GitHub Copilot, prefer the local wrapper skills in `.github/skills/` over importing upstream Superpowers behavior directly.
- Treat upstream Superpowers as a source of workflow patterns, not as the authority for policy, review, or document locations in this repository.
- Do not assume `docs/superpowers/`, mandatory worktrees, or mandatory TDD unless the user explicitly asks for them.

## Validation

- Before push or PR from this repository, run `sh scripts/arch-policy.sh validate-local`.
- Do not bypass `.github/hooks/arch-policy.json`; hooks, shared shell scripts, and CI are the enforcement chain.

## Documentation

- Keep repo-wide guidance concise and link to existing documents instead of duplicating them.
- Use `superpowers-copilot-adoption.md` for the Superpowers-to-arch mapping in this repository.