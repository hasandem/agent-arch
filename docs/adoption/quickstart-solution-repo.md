# Quickstart: New Solution Repository

## Goal

Set up a new solution repository so agents can:

- understand the current solution before implementation when needed
- read central architecture before implementation
- escalate missing shared architecture explicitly
- handle cross-repo dependencies in the right place

This quickstart is the minimum practical setup.

## Resulting file layout

```text
your-solution-repo/
├── .github/
│   ├── copilot-instructions.md
│   ├── skills/
│   │   ├── arch-intake/
│   │   ├── arch-consume/
│   │   ├── arch-escalate/
│   │   └── arch-systematic-debugging/   # optional
│   └── ISSUE_TEMPLATE/
│       └── upstream-dependency.md
├── docs/
│   └── solution-space/
└── AGENTS.md                            # or use only .github/copilot-instructions.md if preferred
```

## Step 1: Add repository instructions

Create one repository-level instruction entry point.

Recommended options:

- `.github/copilot-instructions.md`
- or `AGENTS.md`

Do not use both unless you have a deliberate hierarchy reason.

Use the service template as your starting point:

- [templates/service/AGENTS.md.tmpl](../../templates/service/AGENTS.md.tmpl)

## Step 2: Add the core skills

Copy these skill folders into the new repository under `.github/skills/`:

- `.github/skills/arch-intake/` when the repository needs intake or alignment work
- `.github/skills/arch-consume/`
- `.github/skills/arch-escalate/`

Optional but recommended:

- `.github/skills/arch-systematic-debugging/`

Only add planning, review, or brainstorming wrappers if the team wants that
workflow available locally.

## Step 3: Add intake and solution-space templates

Copy when the repository needs to align an existing solution, assess a pilot, or
document alternatives for reuse:

- [templates/service/intake-brief.md.tmpl](../../templates/service/intake-brief.md.tmpl)
- [templates/service/solution-space-record.md.tmpl](../../templates/service/solution-space-record.md.tmpl)

Suggested target locations:

- `docs/intake/intake-brief.md`
- `docs/solution-space/<topic>.md`

## Step 4: Add cross-repo dependency issue template

Copy:

- [templates/service/.github/ISSUE_TEMPLATE/upstream-dependency.md.tmpl](../../templates/service/.github/ISSUE_TEMPLATE/upstream-dependency.md.tmpl)

Rename it in the target repo to:

- `.github/ISSUE_TEMPLATE/upstream-dependency.md`

## Step 5: Make `arch-read` available

Add this setup snippet to your repo instructions or bootstrap docs:

```sh
export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
if [ ! -d "$ARCH_DIR/.git" ]; then
    git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
else
    git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$ARCH_DIR/scripts"
```

## Step 6: Start a fresh Copilot session

After adding the files, start a new Copilot chat session in the repository.

## Step 7: Verify the setup

Ask the agent something that should trigger the installed skills.

Examples:

- "Help me implement a change to a shared API"
- "We need to change a FHIR contract"
- "This integration test is failing, debug it systematically"

Expected behavior:

- the agent uses `arch-intake` when the repository first needs to be understood
- the agent uses `arch-consume` before architecture-sensitive implementation
- the agent uses `arch-escalate` when shared architecture must change
- the agent prefers target-repo issues for cross-repo dependencies

## Common mistakes

- Installing central-governance hooks in a normal solution repo
- Forgetting to make `arch-read` available
- Forgetting to add intake templates even though the repo needs alignment work
- Copying every wrapper skill before the team actually needs them
- Omitting the upstream dependency issue template even though the repo depends on other repos often

## After quickstart

If the repository needs stronger local workflow support, continue with:

- [Adopt the method in a solution repository](adopt-a-solution-repo.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)