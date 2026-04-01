# Arch-Repo — AI-driven architecture that actually gets used

## The problem we're solving

Most teams have architecture documentation. It gets written once, put in a wiki,
and then ignored. Developers don't read it. Architecture and code drift apart.
Decisions are repeated. Mistakes are replicated.

With AI agents writing more and more code, this problem gets worse. An agent
that doesn't know about the architecture builds whatever looks right in the
moment — without regard for the bigger picture. The result is technical debt
at machine scale.

And the problem compounds. As solutions grow in number and complexity, and
development speed ramps up, architecture becomes *more* important — not less.
Without shared guardrails, each new service and each new agent interaction
adds another opportunity for inconsistency. The faster you move, the more you
need a shared source of truth that everyone — human and machine — actually uses.

## What we're doing about it

This repo is an experiment in flipping the dynamic: instead of architecture
existing alongside development, we make it an active part of the workflow
where AI agents are first-class participants.

In practice, that means three things:

1. **Agents read the architecture before they write code.** Documents are
   structured so an agent can fetch exactly what it needs — from a brief
   summary to full implementation details — without wasting its context window.

2. **Agents keep the architecture up to date.** When an agent discovers
   something missing or incorrect, it creates an issue or PR. The architecture
   isn't static; it evolves through use.

3. **Agents follow the rules of the game.** Hooks, skills, and CI ensure
   agents don't bypass the architecture. They can propose changes, but not
   make them without traceability and review.

The point is that the architecture improves the more it's used, because agents
both consume and contribute to it as part of normal development.

## How it works in practice

An agent implementing a feature typically does this:

1. Fetches relevant architecture context via `arch-read` (a script that gives
   precise extracts without filling up the context window).
2. Checks security requirements for the relevant layer.
3. Implements the feature in the service repo.
4. If the architecture is missing something, the agent creates an issue or PR here.
5. If the work is blocked by another repo, the agent creates an issue where
   the change actually needs to happen — not just as an internal comment.

Everything is traceable. Agents don't commit architecture changes silently.

## What's in this repo

Architecture documents are organized by ArchiMate layers under `docs/arkitektur/`:
motivation, strategy, business, information, application, technology, physical,
security, and implementation/migration. Each document follows a fixed contract
with an agent summary, solution architecture, and target architecture.

The repo also contains:

- **scripts/** — tools for reading, validation, and policy enforcement
- **templates/** — reusable templates for service repos
- **.github/skills/** — Copilot skills that govern agent workflows
- **.github/hooks/** — hooks that stop risky actions before they happen

## Key principles

**Architecture should be read, not guessed.** Agents orient themselves in the
architecture before making decisions. The document structure makes this cheap
in terms of tokens.

**Changes happen through issues and PRs.** Nobody changes normative architecture
directly. Agents propose through the same processes as humans.

**Dependencies must be visible where they need to be resolved.** If repo A needs
a change in repo B, there should be an issue in repo B — not a hidden reference
in repo A.

**Method before domain.** This repo describes the workflow and governance
mechanisms. They can be reused across projects and domains. Domain examples
are illustrations, not the main purpose.

## What this is not

- A wiki that nobody updates.
- A secondary backlog or task list.
- Documentation for just one project.
- A place for details that only apply to a single service.

## Documentation

- [docs/README.md](docs/README.md) — documentation index for the reusable method
- [docs/adoption/adopt-in-a-new-repo.md](docs/adoption/adopt-in-a-new-repo.md) — how to adopt the method in a new repository
- [docs/adoption/adopt-a-solution-repo.md](docs/adoption/adopt-a-solution-repo.md) — minimum adoption path for a solution repository
- [docs/adoption/adopt-a-central-architecture-repo.md](docs/adoption/adopt-a-central-architecture-repo.md) — minimum adoption path for a central architecture repository
- [docs/adoption/quickstart-solution-repo.md](docs/adoption/quickstart-solution-repo.md) — copy/paste quickstart for a new solution repository
- [docs/adoption/quickstart-central-architecture-repo.md](docs/adoption/quickstart-central-architecture-repo.md) — copy/paste quickstart for a new central architecture repository
- [docs/adoption/install-github-copilot-in-a-new-repo.md](docs/adoption/install-github-copilot-in-a-new-repo.md) — how to install the method's Copilot skills and instructions in a new repository
- [docs/adoption/copilot-superpowers.md](docs/adoption/copilot-superpowers.md) — how selected Superpowers workflows map into GitHub Copilot
- [docs/method/overview.md](docs/method/overview.md) — high-level method overview
- [docs/method/document-model.md](docs/method/document-model.md) — document contract, reading levels, and `arch-read`
- [docs/method/governance.md](docs/method/governance.md) — governance, hooks, CI, and change control
- [docs/reference/repository-layout.md](docs/reference/repository-layout.md) — repository layout and reusable artifacts
- [docs/reference/templates-and-starter-assets.md](docs/reference/templates-and-starter-assets.md) — what to copy into a new repository and what to leave behind

## Repository Assets

- [LICENSE](LICENSE) — MIT license for this repository
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) — attribution and license notice for upstream material such as `obra/superpowers`
- `scripts/` — tools for reading (`arch-read`), validation, and policy
- `templates/` — templates for use in service repos
- `.github/skills/` — Copilot skills for `arch-consume`, `arch-escalate`, `arch-governance`, and arch-compatible Superpowers wrappers such as brainstorming, planning, review, and debugging