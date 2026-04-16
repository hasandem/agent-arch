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

### Walkthrough: Adding rate-limiting to a public API

This end-to-end example connects the method overview in
[`docs/method/overview.md`](docs/method/overview.md) with the governance rules in
[`docs/method/governance.md`](docs/method/governance.md).

1. **Orient in architecture** — the agent starts by reading the relevant
   application and security guidance for a planned rate-limit on a public API:

   ```sh
   arch-read --layer application --topic "Public API rate limiting"
   arch-read --layer security --topic "Public API rate limiting"
   ```

2. **Check local knowledge** — before inventing a new pattern, the agent checks
   whether the consuming repository already captured a local decision or
   implementation constraint:

   ```sh
   arch-read --knowledge --topic "Public API rate limiting"
   ```

3. **Escalate the gap** — the application guidance explains where throttling
   belongs, but the security layer has no normative standard for shared rate
   limit headers or audit requirements, so the agent opens a traceable issue in
   the central architecture repository:

   ```sh
   arch-escalate --kind policy-gap --layer security --title "Define normative rate-limiting policy for public APIs"
   ```

4. **Implement with visible annotation** — the feature still ships locally, but
   the code shows that the implementation depends on an open architecture gap:

   ```ts
   export function applyPublicApiRateLimit(req, res, next) {
     // ARCH-ESCALATE: hasandem/agent-arch#123
     res.setHeader("RateLimit-Limit", "120");
     res.setHeader("RateLimit-Remaining", remainingBudgetFor(req));
     return next();
   }
   ```

5. **Record the interim decision locally** — the agent flushes the reasoning
   into local knowledge and creates a deviation record that names the normative
   baseline, the temporary local choice, and the link back to the escalation:

   ```sh
   printf '%s\n' \
     'Temporary public API rate-limit headers until central policy lands; see hasandem/agent-arch#123.' \
     | arch-knowledge flush --session-id "rate-limit-public-api"
   ```

   The repository then adds a local deviation record under
   `docs/arch-knowledge/deviations/` so the temporary choice stays reviewable.

6. **Feedback-loop closes automatically** — when the central security policy is
   merged, CI can scan for `ARCH-ESCALATE:` references, find every linked local
   implementation, and prompt consuming repositories to replace the interim
   deviation with the new normative rule.

This demonstrates the full arch cycle: no silent policy invention, no waiting
for a human reply before shipping, full traceability from code to issue, and an
automatic path back from local deviation to shared architecture.

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

There is also one optional additive pilot profile for consuming repositories
that want to test creativity-first insight work without replacing the
normative method surface:

- `solution-creativity-first-pilot`

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

Fallback when `npx skills` is unavailable:

```sh
mkdir -p scripts
curl -fsSL "https://raw.githubusercontent.com/<owner>/agent-arch/main/scripts/agent-arch-install.sh" -o scripts/agent-arch-install.sh
sh scripts/agent-arch-install.sh --repo <owner>/agent-arch --profile solution-standard
```

The `solution-standard` bootstrap now treats repository instruction files as
user-owned. By default it installs `AGENTS.md` as the shared instruction entry
point for Codex, GitHub Copilot, and other agents, plus a thin `CLAUDE.md`
adapter for Claude-specific additions. If either file already exists, the
installer leaves it in place and continues with the rest of the method surface.
Use `--force` only when you intentionally want the bootstrap to overwrite those
instruction files.

The installed manifest in `.github/agent-arch/solution-standard.manifest`
defines the approved local method surface. If a consumer repository needs a new
method file, change the profile here in `agent-arch` rather than copying extra
files manually downstream.

The creativity-first pilot profile is additive. Install `solution-standard`
first, then optionally apply `solution-creativity-first-pilot` when a consumer
repository wants:

- an `arch-context` skill for insight work and innovation
- a template for documenting deliberate local deviations from the current
  normative architecture
- lightweight local knowledge support without changing the central repository's
  normative role

The shell installer remains a supported fallback when `npx skills` is not
available, but the intended bootstrap path is now the shared skill.

When bootstrapped through `npx skills`, the shared bootstrap skill is installed
in `.agents/skills/agent-arch-install/` for GitHub Copilot. Running its
`install-method.sh` script then materializes the normative repository-local
method surface under `.github/`, `scripts/`, and the other paths listed in the
installed manifest.

## LLM-Agnostic Arch Knowledge

This repository now includes a small `arch-knowledge` pipeline with three
commands:

- `arch-knowledge flush`
- `arch-knowledge compile`
- `arch-knowledge lint`

The design goal is portability across agent tools and model providers.
`flush` and `compile` are LLM-assisted, but they do not depend on any specific
provider SDK. Instead, they call a user-configured adapter command over a small
JSON stdin/stdout contract. `lint` is deterministic and never calls an LLM.

### Directory layout

The local knowledge base lives under:

```text
docs/arch-knowledge/
├── raw/
├── daily/
├── knowledge/
├── arch-statement.md
├── compliance-profile.yaml
└── .state.json
```

### Quick setup

1. Bootstrap the repository with `solution-standard`.
2. Ensure `scripts/` is on `PATH`.
3. Set `ARCH_LLM_ADAPTER` to the installed adapter script.
4. Set `ARCH_LLM_TOOL_CMD` to the command you want to use for model calls.

Minimal config example:

```yaml
llm:
  adapter_command: "python3 scripts/arch-llm-adapter.py"
  timeout_seconds: 60
```

Minimal shell setup:

```sh
export ARCH_LLM_ADAPTER="python3 scripts/arch-llm-adapter.py"
export ARCH_LLM_TOOL_CMD="llm -m gpt-4.1-mini"
export ARCH_LLM_TIMEOUT_SECONDS=60
```

`ARCH_LLM_TOOL_CMD` can point to any command that reads prompt text on `stdin`
and returns plain text on `stdout`. Common patterns are:

```sh
export ARCH_LLM_TOOL_CMD="llm -m gpt-4.1-mini"
export ARCH_LLM_TOOL_CMD="aichat"
export ARCH_LLM_TOOL_CMD="python3 scripts/my-company-llm-wrapper.py"
```

Bootstrap installs these starter files automatically:

```text
docs/arch-knowledge/
├── README.md
├── arch-statement.md
├── compliance-profile.yaml
├── raw/
├── daily/
└── knowledge/
```

If the repository installs the optional creativity-first pilot profile, it also
gets:

```text
docs/arch-knowledge/
└── deviations/
  ├── README.md
  └── local-deviation-record.md
```

Use those files when a consuming repository deliberately chooses a path that
differs from the current normative architecture and needs to capture the
baseline, the reasoning, and whether the learning should feed back into the
central repository.

### Adapter contract

The configured adapter command must:

- read one JSON request from `stdin`
- write one JSON response to `stdout`
- exit with code `0` on success

Request example for `flush`:

```json
{
  "task": "flush",
  "system": "You are an architecture knowledge filter...",
  "input": "raw text to filter",
  "options": {
    "max_chars": 15000
  }
}
```

Success response:

```json
{
  "ok": true,
  "content": "## Decisions\n- ..."
}
```

Error response:

```json
{
  "ok": false,
  "error": "adapter failed"
}
```

This lets the same pipeline work with local Ollama, hosted APIs, enterprise
gateways, or any custom wrapper, as long as the wrapper obeys the contract.

### Usage

After bootstrap and adapter setup, verify the command surface:

```sh
arch-knowledge --help
```

Append architecture-relevant findings from stdin:

```sh
git show HEAD~1..HEAD | arch-knowledge flush --session-id "$(date +%s)"
```

Append from a file:

```sh
arch-knowledge flush --input-file .git/COMMIT_EDITMSG
```

Compile changed daily logs into knowledge articles:

```sh
arch-knowledge compile
```

Force recompilation of all daily logs:

```sh
arch-knowledge compile --all
```

Run deterministic health checks:

```sh
arch-knowledge lint
```

Recommended first-run sequence in a new repository:

```sh
arch-knowledge lint
printf 'We decided to keep shared auth in a dedicated boundary.' | arch-knowledge flush
arch-knowledge compile
arch-knowledge lint
```

### Operational rules

- Canonical architecture remains the normative source of truth.
- `daily/` is append-oriented capture.
- `knowledge/` is local synthesized support material.
- `lint` must stay deterministic.
- If the adapter is missing or fails, `flush` and `compile` fail clearly
  without changing canonical architecture.
- Existing `AGENTS.md` and `CLAUDE.md` are not overwritten during bootstrap
  unless `--force` is used.

## What's in this repo

Architecture documents are organized by ArchiMate layers under `docs/arkitektur/`:
motivation, strategy, business, information, application, technology, physical,
security, and implementation/migration. Each document follows a fixed contract
with an agent summary, solution architecture, and target architecture.

The repo also contains:

- **scripts/** — tools for reading, validation, and policy enforcement
- **scripts/arch-knowledge** — LLM-agnostic local knowledge pipeline wrapper
- **install/profiles/** — controlled install manifests for consumer repositories
- **templates/** — reusable templates for service repos, including `AGENTS.md`
  and a thin `CLAUDE.md` adapter
- **.github/skills/** — reusable agent skills that govern agent workflows
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
- [docs/adoption/install-github-copilot-in-a-new-repo.md](docs/adoption/install-github-copilot-in-a-new-repo.md) — how the shared bootstrap works for repositories that use GitHub Copilot
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
- `.github/skills/` — reusable skills for `agent-arch-install`, `arch-consume`, `arch-escalate`, `arch-governance`, and arch-compatible workflow wrappers such as brainstorming, planning, review, and debugging
