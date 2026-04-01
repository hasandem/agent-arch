# Quickstart: New Central Architecture Repository

## Goal

Set up a new central architecture repository so it can:

- act as the normative architecture source for solution repositories
- enforce document and policy rules consistently
- provide reusable skills, scripts, hooks, and templates

This quickstart is the minimum practical setup.

## Resulting file layout

```text
your-arch-repo/
├── .github/
│   ├── copilot-instructions.md
│   ├── hooks/
│   │   └── arch-policy.json
│   └── skills/
│       ├── arch-consume/
│       ├── arch-escalate/
│       ├── arch-governance/
│       └── arch-*/                     # optional workflow wrappers
├── docs/
│   ├── adoption/
│   ├── method/
│   └── reference/
├── scripts/
│   ├── arch-policy.sh
│   ├── arch-read.sh
│   ├── validate-docs.sh
│   └── find-affected-services.sh
├── templates/
└── README.md
```

## Step 1: Add workspace instructions

Copy or adapt:

- `.github/copilot-instructions.md`

This should define the repository as normative and point skills, hooks, and CI
to the same operating model.

## Step 2: Add the core skills

Copy these skill folders into `.github/skills/`:

- `.github/skills/arch-consume/`
- `.github/skills/arch-escalate/`
- `.github/skills/arch-governance/`

Optional wrappers you may also want from day one:

- `.github/skills/arch-brainstorming/`
- `.github/skills/arch-writing-plans/`
- `.github/skills/arch-requesting-code-review/`
- `.github/skills/arch-systematic-debugging/`

## Step 3: Add hooks

Copy:

- `.github/hooks/arch-policy.json`

The hooks should call shared shell entrypoints rather than embedding policy
logic directly.

## Step 4: Add shared scripts

Copy these scripts into `scripts/`:

- `scripts/arch-policy.sh`
- `scripts/arch-read.sh`
- `scripts/validate-docs.sh`
- `scripts/find-affected-services.sh`
- `scripts/common.sh`

## Step 5: Add docs structure

Create:

- `docs/README.md`
- `docs/adoption/`
- `docs/method/`
- `docs/reference/`

Use this repository's docs structure as the starting point.

## Step 6: Add templates

Copy the templates the new architecture repo should publish for solution repos.

At minimum:

- `templates/service/AGENTS.md.tmpl`
- `templates/service/.github/ISSUE_TEMPLATE/upstream-dependency.md.tmpl`

## Step 7: Start a fresh Copilot session

After adding the files, start a new Copilot chat session in the repository.

## Step 8: Verify the setup

Check these behaviors:

1. The agent can find and use `arch-governance`.
2. Hooks run before and after relevant tool usage.
3. `sh scripts/arch-policy.sh validate-local` works.
4. The repo documents its method and adoption path under `docs/`.
5. A solution repository can consume the repo using `arch-read` and the published templates.

## Common mistakes

- Copying skill prose without the matching scripts and hooks
- Letting hook logic differ from CI logic
- Putting all method docs back into one giant strategy file
- Treating the repository as a shared backlog instead of a normative source

## After quickstart

If the repository will be the long-term architecture authority, continue with:

- [Adopt the method in a central architecture repository](adopt-a-central-architecture-repo.md)
- [Install GitHub Copilot support in a new repository](install-github-copilot-in-a-new-repo.md)
- [Templates and starter assets](../reference/templates-and-starter-assets.md)