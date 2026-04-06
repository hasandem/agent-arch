# Arch-Repo — AI-driven architecture that actually gets used

> This repository is an active experiment. There is no guarantee this approach
> will succeed, and it is being tested in real workflows right now. Expect the
> method, guidance, and tooling to evolve as we learn from that use.

## The problem we're solving

As a product grows in complexity — more services, more integrations, more people,
more moving parts — architecture stops being optional. You need shared structure
to reason about change, manage risk, and keep teams aligned. Without it, every
decision is made in isolation, and the system drifts toward incoherence.

The trouble is that *having* an architecture and *adhering* to it are two very
different things. Architecture gets written once, put in a wiki, and then
ignored. Developers don't read it. Code and documentation drift apart.
Decisions are repeated. Mistakes are replicated. Over time, the gap between
what the architecture says and what the system actually looks like only grows.

Maintaining an architecture is hard because the world doesn't stand still.
Requirements shift, technology evolves, teams reorganise, and the pressure to
ship never lets up. Keeping the architecture accurate and relevant requires
continuous effort — and that effort rarely wins against the next feature deadline.

With AI agents writing more and more code, this problem gets worse. An agent
that doesn't know about the architecture builds whatever looks right in the
moment — without regard for the bigger picture. The result is technical debt
at machine scale.

We want to solve this. Not by writing better documents and hoping someone reads
them, but by making architecture an active part of the entire product lifecycle
— from early insight and design, through development and into long-term
maintenance. We want the architecture to be *used* — by humans and AI agents
alike — while building real-world products that serve users with their problems,
in the kind of complex landscape where architecture matters most.

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

For solution repositories, this method is now distributed through a controlled
installation surface rather than ad hoc copying. A consumer repository installs
the exact approved local method files from this repository and then works only
against that installed surface plus the central architecture clone.

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

## How Solution Repos Adopt The Method

Use `npx skills` to install the bootstrap skill, then let that bootstrap skill
materialize the exact approved method surface into the solution repository.

At the moment there is one normative solution-repository profile:

- `solution-standard`

That profile installs the expected local instructions, skills, templates, and
supporting scripts for a normal consumer repository. Consumer repositories
should not pick files manually from this repository and should not vendor the
entire repository into their own tree.

Typical bootstrap flow in a solution repository:

```sh
npx skills add <owner>/agent-arch --skill agent-arch-install -a github-copilot -y --copy
sh .agents/skills/agent-arch-install/install-method.sh --repo <owner>/agent-arch --profile solution-standard

export ARCH_DIR="${ARCH_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-arch}"
. .github/agent-arch/source.env
if [ ! -d "$ARCH_DIR/.git" ]; then
   git clone --depth 1 "https://github.com/$AGENT_ARCH_SOURCE_REPO.git" "$ARCH_DIR"
else
   git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$PWD/scripts"
```

The installed manifest in `.github/agent-arch/solution-standard.manifest`
defines the approved local method surface. If a consumer repository needs a new
method file, change the profile here in `agent-arch` rather than copying extra
files manually downstream.

The shell installer remains a supported fallback when `npx skills` is not
available, but the intended bootstrap path is now the shared skill.

When bootstrapped through `npx skills`, the shared bootstrap skill is installed
in `.agents/skills/agent-arch-install/` for GitHub Copilot. Running its
`install-method.sh` script then materializes the normative repository-local
method surface under `.github/`, `scripts/`, and the other paths listed in the
installed manifest.

## What's in this repo

Architecture documents are organized by ArchiMate layers under `docs/arkitektur/`:
motivation, strategy, business, information, application, technology, physical,
security, and implementation/migration. Each document follows a fixed contract
with an agent summary, solution architecture, and target architecture.

The repo also contains:

- **scripts/** — tools for reading, validation, and policy enforcement
- **install/profiles/** — controlled install manifests for consumer repositories
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

**Install a controlled local method surface.** Solution repositories should use
`agent-arch-install` with `solution-standard`, then rely on the installed files
instead of manually selecting files from the central repository.

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
- `scripts/` — tools for reading (`arch-read`), installation, validation, and policy
- `install/profiles/solution-standard.manifest` — the only current normative install profile for solution repositories
- `templates/` — templates for use in service repos
- `.github/skills/` — Copilot skills for `agent-arch-install`, `arch-consume`, `arch-escalate`, `arch-governance`, and arch-compatible Superpowers wrappers such as brainstorming, planning, review, and debugging