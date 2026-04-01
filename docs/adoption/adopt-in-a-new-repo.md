# Adopt the Method in a New Repository

## Purpose

Use this page as the entry point when introducing the arch method into a new
repository.

The first decision is the repository role. The adoption path differs depending
on whether the repo is a solution repository or a central governance repository.

## Choose the repository role

### Solution repository

Choose this when the repository implements services, APIs, integrations,
infrastructure, or application code that must follow central architecture.

Use this guide:

- [Adopt the method in a solution repository](adopt-a-solution-repo.md)

### Central architecture or governance repository

Choose this when the repository itself owns normative architecture, policy,
templates, or cross-repo governance.

Use this guide:

- [Adopt the method in a central architecture repository](adopt-a-central-architecture-repo.md)

## Shared rollout advice

Regardless of repo type:

1. Start with the minimum pieces that make architecture reading and escalation work.
2. Keep guidance, hooks, and CI aligned.
3. Add automation only where the repository actually needs enforcement.
4. Avoid copying this repository wholesale into every new repo.

## Related guides

- [Method overview](../method/overview.md)
- [Governance and enforcement](../method/governance.md)
- [Superpowers and GitHub Copilot](copilot-superpowers.md)