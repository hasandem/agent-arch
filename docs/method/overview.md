# Method Overview

## Purpose

`myorg/arch` is a central repository that acts as a shared architecture
constitution for service repositories.

The method is designed for AI-assisted development:

- agents read architecture before writing code
- agents escalate missing architecture through issues and PRs
- hooks, skills, and CI enforce the method consistently

The repository is meant to be reusable across projects and domains.

## Design principles

1. Architecture is organized by ArchiMate layers.
2. Documents are agent-first and optimized for limited context windows.
3. Target and solution architecture live in the same document.
4. Agents read documentation at different depth levels depending on the task.
5. Architecture changes are proposed through traceable issues and PRs.
6. Security is cross-cutting, not an afterthought.
7. Method comes before domain-specific examples.

## Layers

| Tag | Layer | Main question | Typical audience |
| --- | --- | --- | --- |
| `[M]` | Motivation | Why are we doing this? | Architects, leadership |
| `[S]` | Strategy | What can and will we do? | Architects, leadership |
| `[B]` | Business | Who does what? | Domain and solution teams |
| `[I]` | Information | What data exists? | Solution teams and agents |
| `[A]` | Application | What systems interact? | Solution teams and agents |
| `[T]` | Technology | What platform do we run on? | Platform and solution teams |
| `[Ph]` | Physical | What hardware or network is involved? | Hardware and platform teams |
| `[Sec]` | Security | Is it safe and compliant? | All layers |
| `[IM]` | Implementation & Migration | How do we realize the change? | Architects and delivery teams |

## Working model

An agent typically works like this:

1. Read central architecture with `arch-read`.
2. Determine affected layers and security implications.
3. Implement locally when normative architecture does not need to change.
4. Escalate missing or unclear architecture with issues or PRs.
5. Let hooks and CI enforce local and server-side validation.

## What belongs here

This repository should contain:

- shared contracts and canonical models
- cross-team architecture principles and standards
- reusable workflows for agent and human collaboration
- governance rules, templates, and enforcement logic

This repository should not become:

- a service-specific implementation wiki
- a shadow backlog for solution repositories
- a dumping ground for local operational details