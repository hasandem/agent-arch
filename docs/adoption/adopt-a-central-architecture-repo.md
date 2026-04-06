# Adopt the Method in a Central Architecture Repository

## Purpose

Use this guide when the repository itself is intended to own normative
architecture, shared policies, templates, or cross-repo governance.

This is the stronger form of adoption. The repository becomes a reference point
that other repositories consume.

## What to bring in

Add these parts first:

- `arch-intake` if solution repositories should be able to align against this repo through a standard workflow
- `arch-governance`
- shared policy scripts
- hook configuration
- CI validation using the same shared scripts
- templates for issues, PRs, and service-repo adoption

## Minimum setup

1. Create the method directories.
   - `.github/skills/`
   - `.github/hooks/`
   - `scripts/`
   - `templates/`
   - `docs/`
2. Define the document contract for normative architecture documents.
3. Add `arch-governance`.
4. Add shell-based validation and policy entrypoints.
5. Configure hooks to call those entrypoints.
6. Configure CI to use the same validation logic.
7. Add service-repo templates, including intake and solution-space templates when relevant.
8. Add service-repo adoption guides.

## Minimum repository assets

At a minimum, a central architecture repository should provide:

- a short root `README.md`
- a documentation index under `docs/`
- a clear place for solution-space guidance when solution-near decisions should be shared across repositories
- reusable skills under `.github/skills/`
- hooks under `.github/hooks/`
- validation and policy scripts under `scripts/`
- service templates under `templates/`

## Governance rules

1. Skills guide behavior but do not become a second policy engine.
2. Hooks and CI should call the same shared scripts.
3. Protected areas such as strategy, security, and document contracts should have stronger review requirements.
4. Direct PR autonomy should be tied to explicit change classes.
5. Architecture changes should remain traceable through issues and PRs.

## Validation checklist

Before calling the method adopted in a central architecture repository, verify:

1. Hooks are active and call shared scripts.
2. CI runs the same validation logic.
3. Document contracts are deterministic and machine-readable.
4. Skills, scripts, and templates point to the same workflow.
5. Solution repositories can consume the repo with minimal setup.

## Avoid these mistakes

- Encoding important policy only inside skill prose
- Letting hooks and CI drift apart
- Treating the repository as a general backlog
- Mixing reusable method docs with one project's local implementation details

## Related guides

- [Adoption overview](adopt-in-a-new-repo.md)
- [Quickstart for a new central architecture repository](quickstart-central-architecture-repo.md)
- [Governance and enforcement](../method/governance.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Repository layout and artifacts](../reference/repository-layout.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)