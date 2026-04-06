# Templates and Starter Assets

## Purpose

This guide explains what to copy from this repository when adopting the method
in another repository.

The goal is to copy only the assets that match the role of the target
repository.

## Principle

Do not copy everything by default.

Use the minimum starter set that gives the target repository the right agent
behavior, templates, and validation hooks for its role.

For solution repositories, use `solution-standard` rather than selecting files manually.

## Starter assets for a solution repository

These are the usual starting assets for a normal service or application repo.

### Copy directly

- Prefer bootstrapping with `npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy`, then materialize [install/profiles/solution-standard.manifest](../../install/profiles/solution-standard.manifest) through `.agents/skills/agent-arch-install/install-method.sh`; it is the only current normative solution profile

### Add or reference from the central architecture repo

- `agent-arch-install`
- `arch-intake` when the repo needs discovery or alignment before implementation
- `arch-consume`
- `arch-escalate`
- `arch-systematic-debugging` when debugging guidance is wanted locally
- `arch-read` with `ARCH_DIR` pointed at a local clone of the central architecture repository

### Usually do not copy

- central-repo hooks
- central-repo policy scripts
- central-repo CI validation rules
- governance-only templates that are specific to normative architecture
- files outside the `solution-standard` manifest

## Starter assets for a central architecture repository

These are the starting assets for a repo that owns normative architecture.

### Copy directly or recreate from this repository

- `.github/copilot-instructions.md`
- `.github/hooks/arch-policy.json`
- `.github/skills/arch-governance/`
- `.github/skills/arch-consume/`
- `.github/skills/arch-escalate/`
- arch-compatible wrapper skills as needed
- `scripts/arch-policy.sh`
- `scripts/validate-docs.sh`
- `scripts/find-affected-services.sh`
- `scripts/arch-read.sh`
- service templates under `templates/`

### Copy with care

- issue templates
- PR templates
- docs structure under `docs/`

These should be adapted to the new organization's vocabulary, repository names,
and governance boundaries.

## Copy matrix

| Asset | Solution repo | Central architecture repo |
| --- | --- | --- |
| `templates/service/AGENTS.md.tmpl` | Yes | As template only |
| `upstream-dependency.md.tmpl` | Often | As template only |
| `intake-brief.md.tmpl` | When needed | As template only |
| `solution-space-record.md.tmpl` | When needed | As template only |
| `arch-intake` | When needed | Optional |
| `arch-consume` | Yes | Optional |
| `arch-escalate` | Yes | Optional |
| `arch-governance` | No | Yes |
| hooks and shared policy scripts | No | Yes |
| docs structure under `docs/` | Minimal | Yes |
| validation scripts | Usually no | Yes |

## Practical rule

If the target repo consumes architecture, copy the consumer assets.

In practice, install `solution-standard` and treat its manifest plus `.github/agent-arch/source.env` as the local contract.

If the target repo defines normative architecture, copy the governance assets.

If a file only makes sense because this repository is the policy authority,
do not copy it blindly into a solution repository.

## Related guides

- [Adopt the method in a solution repository](../adoption/adopt-a-solution-repo.md)
- [Adopt the method in a central architecture repository](../adoption/adopt-a-central-architecture-repo.md)
- [Install GitHub Copilot support in a new repository](../adoption/install-github-copilot-in-a-new-repo.md)