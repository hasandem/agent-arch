# Adopt the Method in a Solution Repository

## Purpose

Use this guide when a repository implements services, APIs, integrations,
infrastructure, or application code that must follow central architecture.

The goal is to make architecture reading, escalation, and cross-repo
coordination explicit without turning the solution repository into a second
governance repository.

Use the controlled installation profile `solution-standard` for the local method
surface. Do not pick files manually from the central repository.

## What to bring in

Add these parts first:

- the approved `solution-standard` install profile for solution repositories
- `AGENTS.md` plus the thin `CLAUDE.md` adapter from that profile
- the skills and support files listed in the installed manifest
- `arch-knowledge` scripts plus `docs/arch-knowledge/` starter files from that profile
- cross-repo dependency issue templates when relevant

Optional for creativity-first pilots in consuming repositories:

- the additive `solution-creativity-first-pilot` profile
- the `arch-context` skill
- the local deviation record starter files under `docs/arch-knowledge/deviations/`

Do not copy central-governance hooks and policy scripts unless the solution
repository is also intended to become a normative repository.

## Minimum setup

1. Add repository instructions.
   - Install `solution-standard` instead of copying files manually.
2. Keep `ARCH_DIR` pointed at a local clone of the central architecture repository.
3. Let the installer write `.github/agent-arch/source.env` so local scripts know which central repository they belong to.
4. Ensure the installed profile puts local method scripts on `PATH`.
5. Add target-repo issue templates if repo-to-repo dependencies are common.
6. Configure `ARCH_LLM_TOOL_CMD` if the repository will use `arch-knowledge flush` and `compile`.

If the repository wants a minimal creativity-first pilot surface, apply this
after `solution-standard`:

```sh
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-creativity-first-pilot
```

## Setup snippet

```sh
mkdir -p scripts
curl -fsSL "https://raw.githubusercontent.com/<owner>/agent-arch/main/scripts/arch-init" -o scripts/arch-init
chmod +x scripts/arch-init
sh scripts/arch-init

export ARCH_DIR="${ARCH_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-arch}"
export PATH="$PATH:$PWD/scripts"
```

Use `--repo <owner>/agent-arch` when bootstrapping from a fork or mirror.

Manual fallback when `arch-init` is unavailable:

```sh
npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-standard
```

With the `arch-init` bootstrap path, the shared bootstrap skill is installed in
`.agents/skills/agent-arch-install/` for GitHub Copilot before it materializes
the normative local method surface into the repository itself.

The installed profile also seeds `docs/arch-knowledge/` plus a generic
`scripts/arch-llm-adapter.py` wrapper. Set:

```sh
export ARCH_LLM_ADAPTER="$PWD/scripts/arch-llm-adapter.py"
export ARCH_LLM_TOOL_CMD="llm -m gpt-4.1-mini"
```

Replace `ARCH_LLM_TOOL_CMD` with any command that accepts prompt text on stdin
and returns plain text on stdout.

## Working rules

1. If the repository must first be understood, use `arch-intake` before jumping into implementation.
2. Read central architecture before changing shared contracts, APIs, FHIR models, or security-sensitive behavior.
3. Use creativity-first working practices when the first need is insight work, innovation, or evaluation of alternatives in the local solution repository.
4. A local team may choose a path that differs from the current normative architecture, but only when that choice is deliberate, documented, and explicitly analyzed against the central architecture.
5. If repo A depends on repo B, create an issue in repo B where the change must happen.
6. If the real problem is a missing or unclear shared standard, escalate through `arch-escalate`.
7. Treat the installed manifest as the approved local method surface.
8. Keep validation commands explicit and runnable in the repository.
9. Treat local `knowledge/` as supportive context, not normative architecture.

## Creativity-First In A Solution Repository

Creativity-first is the preferred mode when a consuming repository needs to do
insight work before converging on a solution. The purpose is not to ignore
central architecture, but to let teams compare their local reality against it,
explore alternatives, and make deliberate choices.

This means a solution repository may:

- ingest local or external source material into its local knowledge support files
- build local context and synthesize learning over time
- choose a local implementation path that diverges from the current normative architecture

But that freedom comes with obligations:

- the current normative architecture must be read and treated as the comparison baseline
- a local deviation must be explicitly justified against that baseline
- the reasoning and evidence must be traceable in repository artifacts
- if the local learning reveals a reusable improvement, the repository should feed it back through the normal escalation path instead of keeping it as an unspoken local exception

Creativity-first therefore supports innovation in the consuming repository,
while the central repository remains responsible for what becomes normative.

## Verification checklist

Before calling the method adopted in a solution repository, verify:

1. The agent can resolve and read central architecture.
2. `.github/agent-arch/solution-standard.manifest` exists and matches the only current normative solution profile.
3. `.github/agent-arch/source.env` points to the intended central repository and ref.
4. `arch-intake` is available if the repository will align existing solutions or evaluate pilots.
5. `arch-consume` is discoverable and usable.
6. `arch-escalate` is discoverable and usable.
7. The repository can document and trace deliberate local deviations from the current normative architecture.
8. Cross-repo dependency handling is explicit.
9. The repository has service-level instructions that point to the method.
10. `arch-knowledge doctor` and `arch-knowledge --help` work if the local knowledge pipeline is enabled.

## Avoid these mistakes

- Copying central-governance automation into every solution repo
- Copying method files manually instead of using `solution-standard`
- Skipping intake even though the repository first needs alignment or discovery
- Treating shared architecture as optional reading
- Treating local innovation as a substitute for explicit analysis against central architecture
- Leaving a deliberate local deviation undocumented or untraceable
- Hiding dependencies in comments instead of target-repo issues
- Mixing local implementation backlog with normative architecture changes

## Related guides

- [Adoption overview](adopt-in-a-new-repo.md)
- [Quickstart for a new solution repository](quickstart-solution-repo.md)
- [Method overview](../method/overview.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)
- [Superpowers and GitHub Copilot](copilot-superpowers.md)
