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
│   └── reference/
├── scripts/
├── templates/
├── README.md
└── LICENSE
```

## What each area is for

### `.github/skills/`

Reusable Copilot skills that guide agent behavior.

Core skills in this repository include:

- `arch-consume`
- `arch-escalate`
- `arch-governance`
- arch-compatible workflow wrappers for brainstorming, planning, review, and debugging

### `.github/hooks/`

Deterministic runtime enforcement.

Hooks should stay short, auditable, and delegated to shared scripts when the
logic must also be reused by CI.

### `scripts/`

Shared shell entrypoints for reading, policy, and validation.

### `templates/`

Starter assets for new service repositories, including issue templates and
agent instructions.

### `docs/`

Method and adoption documentation.

This is intentionally separated from architecture content so the reusable method
does not get buried inside one large strategy document.

## Reusable-method pattern

Inspired by repositories like `obra/superpowers`, the reusable-method pattern is:

1. Short root README for orientation.
2. Focused docs for adoption and platform-specific guidance.
3. Skills and scripts as the operational core.
4. Templates that help other repos adopt the method consistently.