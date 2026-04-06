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
- service-level agent instructions from that profile
- the skills and support files listed in the installed manifest
- cross-repo dependency issue templates when relevant

Do not copy central-governance hooks and policy scripts unless the solution
repository is also intended to become a normative repository.

## Minimum setup

1. Add repository instructions.
   - Install `solution-standard` instead of copying files manually.
2. Keep `ARCH_DIR` pointed at a local clone of the central architecture repository.
3. Let the installer write `.github/agent-arch/source.env` so local scripts know which central repository they belong to.
4. Ensure the installed profile puts local method scripts on `PATH`.
5. Add target-repo issue templates if repo-to-repo dependencies are common.

## Setup snippet

```sh
npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-standard

export ARCH_DIR="${ARCH_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-arch}"
. .github/agent-arch/source.env
if [ ! -d "$ARCH_DIR/.git" ]; then
   git clone --depth 1 "https://github.com/$AGENT_ARCH_SOURCE_REPO.git" "$ARCH_DIR"
else
   git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$PWD/scripts"
```

Fallback when `npx skills` is unavailable:

```sh
mkdir -p scripts
curl -fsSL "https://raw.githubusercontent.com/<owner>/agent-arch/main/scripts/agent-arch-install.sh" -o scripts/agent-arch-install.sh
sh scripts/agent-arch-install.sh --repo <owner>/agent-arch --profile solution-standard
```

With the `npx skills` bootstrap path, the shared bootstrap skill is installed in `.agents/skills/agent-arch-install/` for GitHub Copilot before it materializes the normative local method surface into the repository itself.

## Working rules

1. If the repository must first be understood, use `arch-intake` before jumping into implementation.
2. Read central architecture before changing shared contracts, APIs, FHIR models, or security-sensitive behavior.
3. Keep local changes local when normative architecture does not need to change.
4. If repo A depends on repo B, create an issue in repo B where the change must happen.
5. If the real problem is a missing or unclear shared standard, escalate through `arch-escalate`.
6. Treat the installed manifest as the approved local method surface.
7. Keep validation commands explicit and runnable in the repository.

## Verification checklist

Before calling the method adopted in a solution repository, verify:

1. The agent can resolve and read central architecture.
2. `.github/agent-arch/solution-standard.manifest` exists and matches the only current normative solution profile.
3. `.github/agent-arch/source.env` points to the intended central repository and ref.
4. `arch-intake` is available if the repository will align existing solutions or evaluate pilots.
5. `arch-consume` is discoverable and usable.
6. `arch-escalate` is discoverable and usable.
7. Cross-repo dependency handling is explicit.
8. The repository has service-level instructions that point to the method.

## Avoid these mistakes

- Copying central-governance automation into every solution repo
- Copying method files manually instead of using `solution-standard`
- Skipping intake even though the repository first needs alignment or discovery
- Treating shared architecture as optional reading
- Hiding dependencies in comments instead of target-repo issues
- Mixing local implementation backlog with normative architecture changes

## Related guides

- [Adoption overview](adopt-in-a-new-repo.md)
- [Quickstart for a new solution repository](quickstart-solution-repo.md)
- [Method overview](../method/overview.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)
- [Superpowers and GitHub Copilot](copilot-superpowers.md)