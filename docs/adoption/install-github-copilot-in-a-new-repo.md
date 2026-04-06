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

## Project-local installation

### 1. Add workspace instructions

Create:

- `.github/copilot-instructions.md`

Use this repository's file as the starting point when the target repository is a
central architecture repository.

For a solution repository, prefer a narrower instruction file that points to the
central architecture repo and local repo conventions.

### 2. Add the skills that match the repo role

For a solution repository, typically add:

- `.github/skills/arch-intake/` when the repo needs intake or alignment support
- `.github/skills/arch-consume/`
- `.github/skills/arch-escalate/`
- optional workflow wrappers like `.github/skills/arch-systematic-debugging/`

For a central architecture repository, typically add:

- `.github/skills/arch-governance/`
- plus any other local workflow wrappers you want available by default

### 3. Add hooks when the repo needs enforcement

Create:

- `.github/hooks/arch-policy.json`

Only do this when the repository should enforce deterministic governance
behavior, not just offer guidance.

### 4. Add supporting scripts if hooks or skills depend on them

Typical examples:

- `scripts/arch-policy.sh`
- `scripts/validate-docs.sh`
- `scripts/find-affected-services.sh`
- `scripts/arch-read.sh`

### 5. Restart the Copilot session

Open a new Copilot chat session after the files are added so the new workspace
customizations are loaded.

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

- service instructions
- `arch-intake` when the repository must first be understood or aligned
- `arch-consume`
- `arch-escalate`
- optional local workflow wrappers

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
3. Start a fresh Copilot session after adding the files.
4. Check that the workspace instruction file is present and does not conflict with another instruction file.

### Hooks are not behaving as expected

1. Confirm `.github/hooks/arch-policy.json` exists.
2. Confirm any referenced scripts exist and are executable by the shell.
3. Verify the scripts work when run directly.

## Related guides

- [Adopt the method in a solution repository](adopt-a-solution-repo.md)
- [Adopt the method in a central architecture repository](adopt-a-central-architecture-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)