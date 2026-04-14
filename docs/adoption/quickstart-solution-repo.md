# Quickstart: New Solution Repository

## Goal

Set up a new solution repository so agents can:

- understand the current solution before implementation when needed
- read central architecture before implementation
- escalate missing shared architecture explicitly
- handle cross-repo dependencies in the right place

This quickstart is the minimum practical setup.

Use the `solution-standard` installation profile instead of copying files one by one.

## Resulting file layout

```text
your-solution-repo/
├── .agents/
│   └── skills/
│       └── agent-arch-install/
│           ├── SKILL.md
│           └── install-method.sh
├── .github/
│   ├── agent-arch/
│   │   ├── source.env
│   │   └── solution-standard.manifest
│   ├── skills/
│   │   ├── agent-arch-install/
│   │   ├── arch-intake/
│   │   ├── arch-consume/
│   │   ├── arch-escalate/
│   │   └── arch-systematic-debugging/
│   └── ISSUE_TEMPLATE/
│       └── upstream-dependency.md
├── AGENTS.md
├── CLAUDE.md
├── docs/
│   ├── arch-knowledge/
│   │   ├── README.md
│   │   ├── arch-statement.md
│   │   ├── compliance-profile.yaml
│   │   ├── raw/
│   │   ├── daily/
│   │   └── knowledge/
│   ├── intake/
│   │   └── intake-brief.md
│   └── solution-space/
│       └── solution-space-record.md
├── arch-read.sh
└── scripts/
    ├── agent-arch-install.sh
    ├── arch-knowledge
    ├── arch-llm-adapter.py
    ├── arch_knowledge/
    ├── arch-policy.sh
    ├── arch-read.sh
    └── common.sh
```

## Step 1: Install `solution-standard`

```sh
npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-standard
```

This installs the only current normative local method surface for solution repositories, listed in `.github/agent-arch/solution-standard.manifest`.
The bootstrap skill itself is placed in `.agents/skills/agent-arch-install/` for GitHub Copilot.

Fallback when `npx skills` is unavailable:

```sh
mkdir -p scripts
curl -fsSL "https://raw.githubusercontent.com/<owner>/agent-arch/main/scripts/agent-arch-install.sh" -o scripts/agent-arch-install.sh
sh scripts/agent-arch-install.sh --repo <owner>/agent-arch --profile solution-standard
```

## Step 2: Use the installed instruction entry points

`solution-standard` installs:

- `AGENTS.md` as the shared instruction file for Codex, GitHub Copilot, and
  other agents
- `CLAUDE.md` as a thin Claude adapter that should defer to `AGENTS.md`
- `docs/arch-knowledge/` starter files
- `scripts/arch-knowledge` plus the Python package and generic adapter wrapper

If either file already exists, bootstrap leaves it untouched unless you rerun
the installer with `--force`.

Use the service template as your starting point or merge target:

- [templates/service/AGENTS.md.tmpl](../../templates/service/AGENTS.md.tmpl)
- [templates/service/CLAUDE.md.tmpl](../../templates/service/CLAUDE.md.tmpl)

## Step 3: Point local tooling at central architecture

Add this setup snippet to your repo instructions or bootstrap docs:

```sh
export ARCH_DIR="${ARCH_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-arch}"
. .github/agent-arch/source.env
if [ ! -d "$ARCH_DIR/.git" ]; then
    git clone --depth 1 "https://github.com/$AGENT_ARCH_SOURCE_REPO.git" "$ARCH_DIR"
else
    git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$PWD/scripts"
```

The installed local `arch-read` wrapper uses `ARCH_DIR` to read the central architecture clone.

## Step 4: Configure the local LLM command

Set the adapter and the tool command you want to use:

```sh
export ARCH_LLM_ADAPTER="python3 scripts/arch-llm-adapter.py"
export ARCH_LLM_TOOL_CMD="llm -m gpt-4.1-mini"
```

Replace `ARCH_LLM_TOOL_CMD` with any command that reads prompt text on stdin
and returns plain text on stdout.

## Step 5: Start a fresh agent session

After adding the files, start a new Claude, Copilot, or Codex session in the repository.

## Step 6: Verify the setup

Ask the agent something that should trigger the installed skills.

Examples:

- "Help me implement a change to a shared API"
- "We need to change a FHIR contract"
- "This integration test is failing, debug it systematically"

Expected behavior:

- `agent-arch-install` is available for controlled upgrades of the local method surface
- the agent uses `arch-intake` when the repository first needs to be understood
- the agent uses `arch-consume` before architecture-sensitive implementation
- the agent uses `arch-escalate` when shared architecture must change
- the agent prefers target-repo issues for cross-repo dependencies
- `arch-knowledge --help` works
- `arch-knowledge lint` runs without needing a model

## Common mistakes

- Installing central-governance hooks in a normal solution repo
- Copying method files manually instead of using `solution-standard`
- Forgetting to point `ARCH_DIR` at a local clone of the central architecture repo
- Editing centrally managed method files locally without first changing the central profile

## After quickstart

If the repository needs stronger local workflow support, continue with:

- [Adopt the method in a solution repository](adopt-a-solution-repo.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)
