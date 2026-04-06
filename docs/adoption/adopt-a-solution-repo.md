# Adopt the Method in a Solution Repository

## Purpose

Use this guide when a repository implements services, APIs, integrations,
infrastructure, or application code that must follow central architecture.

The goal is to make architecture reading, escalation, and cross-repo
coordination explicit without turning the solution repository into a second
governance repository.

## What to bring in

Add these parts first:

- `arch-intake` when the repo needs alignment or discovery before implementation
- `arch-consume`
- `arch-escalate`
- service-level agent instructions
- cross-repo dependency issue templates when relevant

Do not copy central-governance hooks and policy scripts unless the solution
repository is also intended to become a normative repository.

## Minimum setup

1. Add repository instructions.
   - Start from [templates/service/AGENTS.md.tmpl](../../templates/service/AGENTS.md.tmpl).
2. Make `arch-read` available from the central architecture repository.
3. Add intake and solution-space templates if the repo will align existing solutions or learn from pilots.
4. Ensure agents can use `arch-consume` before architecture-sensitive work.
5. Ensure agents can use `arch-escalate` when local work uncovers a gap in shared architecture.
6. Add target-repo issue templates if repo-to-repo dependencies are common.

## Setup snippet

```sh
export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
if [ ! -d "$ARCH_DIR/.git" ]; then
    git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
else
    git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$ARCH_DIR/scripts"
```

## Working rules

1. If the repository must first be understood, use `arch-intake` before jumping into implementation.
2. Read central architecture before changing shared contracts, APIs, FHIR models, or security-sensitive behavior.
3. Keep local changes local when normative architecture does not need to change.
4. If repo A depends on repo B, create an issue in repo B where the change must happen.
5. If the real problem is a missing or unclear shared standard, escalate through `arch-escalate`.
6. Keep validation commands explicit and runnable in the repository.

## Verification checklist

Before calling the method adopted in a solution repository, verify:

1. The agent can resolve and read central architecture.
2. `arch-intake` is available if the repository will align existing solutions or evaluate pilots.
3. `arch-consume` is discoverable and usable.
4. `arch-escalate` is discoverable and usable.
5. Cross-repo dependency handling is explicit.
6. The repository has service-level instructions that point to the method.

## Avoid these mistakes

- Copying central-governance automation into every solution repo
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