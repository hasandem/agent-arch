# Install GitHub Copilot Support in a New Repository

## Purpose

Use this guide when you want a new repository to discover and use the arch
method through GitHub Copilot customizations.

This is the Copilot equivalent of the short installation guides used by
reusable method projects like `obra/superpowers`.

## Recommended mode

Use project-local installation.

That means storing instructions and skills inside the new repository so they are
versioned, reviewed, and shared with the team.

For solution repositories, use the `solution-standard` install profile rather than copying files manually.

## Project-local installation

### 1. Add workspace instructions

For solution repositories, prefer:

- `AGENTS.md` as the shared instruction file
- `CLAUDE.md` only as a thin Claude-specific adapter

When using the controlled install flow, those files are installed by the
profile. If they already exist, bootstrap leaves them in place unless you use
`--force`.

Use `.github/copilot-instructions.md` only when a repository has a verified
Copilot-specific need that cannot be expressed cleanly through `AGENTS.md`.

### 2. Install the normative profile for the repo role

For a solution repository, bootstrap the installer and apply `solution-standard`:

```sh
npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-standard
```

This installs only the files listed in `.github/agent-arch/solution-standard.manifest`.
It also writes `.github/agent-arch/source.env` so local scripts can resolve the right central repository and ref.
The shared bootstrap skill itself is installed into `.agents/skills/agent-arch-install/` for GitHub Copilot.

Fallback when `npx skills` is unavailable:

```sh
mkdir -p scripts
curl -fsSL "https://raw.githubusercontent.com/<owner>/agent-arch/main/scripts/agent-arch-install.sh" -o scripts/agent-arch-install.sh
sh scripts/agent-arch-install.sh --repo <owner>/agent-arch --profile solution-standard
```

If the repository also wants the optional creativity-first pilot surface for
insight work and documented local deviations, apply this profile after
`solution-standard`:

```sh
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-creativity-first-pilot
```

### 3. Add the skills that match the repo role

For a solution repository, typically add:

- `.github/skills/agent-arch-install/`
- `.github/skills/arch-intake/` when the repo needs intake or alignment support
- `.github/skills/arch-consume/`
- `.github/skills/arch-escalate/`
- optional workflow wrappers like `.github/skills/arch-systematic-debugging/`
- `.github/skills/arch-context/` when the repository is piloting creativity-first insight work

For a central architecture repository, typically add:

- `.github/skills/arch-governance/`
- plus any other local workflow wrappers you want available by default

### 4. Add hooks when the repo needs enforcement

Create:

- `.github/hooks/arch-policy.json`

Only do this when the repository should enforce deterministic governance
behavior, not just offer guidance.

### 5. Add supporting scripts if hooks or skills depend on them

Typical examples:

- `scripts/agent-arch-install.sh`
- `scripts/arch-policy.sh`
- `scripts/common.sh`
- `scripts/arch-read.sh`

For a solution repository, prefer the exact script set from `solution-standard` instead of selecting scripts manually.

### 6. Restart the agent session

Open a new Copilot chat session after the files are added so the new workspace
customizations are loaded. Apply the same rule for Claude or Codex after
changing `AGENTS.md` or `CLAUDE.md`.

## Verify installation

Start a new chat session in the target repository and ask for a task that should
trigger one of the installed skills.

Examples:

- "Help me plan this architecture-sensitive change"
- "We need to change a shared API contract"
- "Debug this failing integration test"

The agent should discover the installed skills and follow the repository's local
instructions.

## Personal installation

For experimentation, you can install skills in a personal directory such as:

- `~/.copilot/skills/`

Use this only for personal workflows or prototyping. Team-governed behavior
should live in the repository.

## What to install by repo type

### Solution repository

Install:

- the `solution-standard` install profile, which is the only current normative solution profile
- `AGENTS.md` plus the thin `CLAUDE.md` adapter from that profile
- `agent-arch-install`
- `arch-intake`, `arch-consume`, and `arch-escalate`
- optional local workflow wrappers that are explicitly added to `solution-standard`

Optional additive pilot install:

- `solution-creativity-first-pilot`
- `arch-context`
- the local deviation record starter files under `docs/arch-knowledge/deviations/`

Do not install central-governance hooks and scripts by default.

### Central architecture repository

Install:

- `.github/copilot-instructions.md`
- `arch-governance`
- hooks and shared policy scripts
- any reusable workflow wrappers the repository wants to standardize on

## Troubleshooting

### Skills are not being used

1. Confirm the skill folders exist under `.github/skills/`.
2. Confirm each skill has a valid `SKILL.md` with matching `name` and folder name.
3. Confirm `.github/agent-arch/solution-standard.manifest` exists for controlled solution installs.
4. Confirm `.github/agent-arch/source.env` points at the intended public agent-arch repository.
5. Start a fresh Copilot session after adding the files.
6. Check that the workspace instruction file is present and does not conflict with another instruction file.
7. If instructions are not behaving as expected, check `AGENTS.md` first and keep `CLAUDE.md` thin.

### Hooks are not behaving as expected

1. Confirm `.github/hooks/arch-policy.json` exists.
2. Confirm any referenced scripts exist and are executable by the shell.
3. Verify the scripts work when run directly.

## Related guides

- [Adopt the method in a solution repository](adopt-a-solution-repo.md)
- [Adopt the method in a central architecture repository](adopt-a-central-architecture-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)
