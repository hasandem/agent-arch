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
4. Solution-space records can capture alternatives and chosen solutions without becoming normative architecture.
5. Agents read documentation at different depth levels depending on the task.
6. Architecture changes are proposed through traceable issues and PRs.
7. Security is cross-cutting, not an afterthought.
8. Method comes before domain-specific examples.

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

1. If the repository must first be understood, start with `arch-intake`.
2. Read central architecture with `arch-read`.
3. Determine affected layers and security implications.
4. Implement locally when normative architecture does not need to change.
5. Escalate missing or unclear architecture with issues or PRs.
6. Let hooks and CI enforce local and server-side validation.

## Creativity-First In Consumer Repositories

The method also allows a creativity-first working mode in consuming
repositories when the main need is insight work, local innovation, or
evaluation of alternatives close to real solution work.

In that mode:

1. The consuming repository still reads central architecture as the normative
   reference point.
2. The team or agent may evaluate and choose a local solution that differs
   from the current normative architecture.
3. Such deviations must be deliberate, explicitly analyzed against the central
   architecture, and documented in a traceable way.
4. If the local learning suggests a better reusable pattern, contract, or
   principle, it should feed back into the central repository through the
   normal proposal and review path.

This means the central repository remains normative, while consuming
repositories remain the primary place where new insight can emerge.

## Solution space in the method

The method now distinguishes between two kinds of architecture material:

- canonical architecture documents, which remain the normative source of truth
- solution-space records, which document alternatives, chosen solutions, and guardrails close to real repository work

This helps other repositories understand not only the current recommendation,
but also which options were considered and why one path was chosen.

Solution-space records support architecture work, but they do not replace the
target architecture.

The same principle applies to local creativity-first knowledge in consuming
repositories: it may support analysis, decisions, and innovation, but it does
not become a peer source of truth next to canonical architecture.

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