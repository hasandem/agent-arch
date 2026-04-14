# Repository Layout and Artifacts

## Purpose

This reference describes the repository structure that supports the reusable
arch method.

## High-level layout

```text
.
├── .github/
│   ├── hooks/
│   └── skills/
├── docs/
│   ├── adoption/
│   ├── method/
│   ├── solution-space/
│   └── reference/
├── scripts/
├── templates/
├── README.md
└── LICENSE
```

## What each area is for

### `.github/skills/`

Reusable agent skills that guide agent behavior.

Core skills in this repository include:

- `arch-intake`
- `arch-consume`
- `arch-escalate`
- `arch-governance`
- arch-compatible workflow wrappers for brainstorming, planning, review, and debugging

### `.github/hooks/`

Deterministic runtime enforcement.

Hooks should stay short, auditable, and delegated to shared scripts when the
logic must also be reused by CI.

### `scripts/`

Shared shell entrypoints for reading, policy, validation, bootstrap, and the
local `arch-knowledge` pipeline.

### `templates/`

Starter assets for new service repositories, including issue templates and
agent instructions.

### `docs/`

Method and adoption documentation.

This is intentionally separated from architecture content so the reusable method
does not get buried inside one large strategy document.

The `solution-space/` area can be used for solution-near records that show
alternatives, chosen solutions, and traceable learning without turning those
records into normative target architecture.

## Reusable-method pattern

Inspired by repositories like `obra/superpowers`, the reusable-method pattern is:

1. Short root README for orientation.
2. Focused docs for adoption and platform-specific guidance.
3. Skills and scripts as the operational core.
4. Templates that help other repos adopt the method consistently.
