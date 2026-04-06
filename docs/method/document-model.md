# Document Model and Reading Flow

## Why the model exists

Agents have limited context windows. The method therefore optimizes documents so
an agent can read exactly as much architecture as needed for a task.

## Target and solution in one document

Each architecture document contains both concrete implementation guidance and
strategic direction.

The standard structure is:

```markdown
# <Title>

## Agent-sammendrag

## Løsningsarkitektur

## Målarkitektur

## Referanser
```

## Reading levels

Use increasing depth only when needed:

1. `INDEX.md` for orientation
2. `Agent-sammendrag` for most tasks
3. `Løsningsarkitektur` for implementation work
4. `Målarkitektur` for architecture changes

## Solution-space records

The canonical architecture documents still use the standard contract above.

In addition, the method can use solution-space records for solution-near
architecture work. These records live outside the strict normative document
contract and are meant to capture:

- alternatives that were considered
- the chosen solution and its guardrails
- rejected options and the reasons behind them
- traceability back to intake, ADRs, issues, and later architecture updates

This lighter record type is especially useful when learning from another
repository, evaluating a pilot, or documenting why one solution path was
chosen over another.

## `arch-read`

`arch-read` is the method's context-efficient reader.

Typical usage:

```bash
arch-read --index informasjon
arch-read docs/arkitektur/informasjon/fhir/consent.md
arch-read docs/arkitektur/informasjon/fhir/consent.md --solution
arch-read docs/arkitektur/informasjon/fhir/consent.md --target
arch-read docs/arkitektur/informasjon/fhir/consent.md --full
arch-read --search "MedicationRequest"
arch-read --solution-space
arch-read --search-solution-space "intake"
```

When solution-space is used often, these commands make it easier to find and
reuse solution-near records without scanning the whole repository first.

## Contract rules

For tools and validation to remain deterministic:

1. Use exact H2 headings.
2. Keep one H1 per document.
3. Keep H2 sections in fixed order.
4. Keep H3 headings unique inside the same H2 section.
5. Use repo-relative file paths in examples.
6. Update the relevant `INDEX.md` when adding a new document.

## Reading order

When impact is unclear, read architecture in this order:

1. Relevant `INDEX.md`
2. Relevant `Agent-sammendrag`
3. Relevant security documents
4. Relevant `Løsningsarkitektur`
5. `Målarkitektur` only if normative change is under consideration

## Rule of thumb

- Writing code: summary plus solution architecture
- Reviewing impact: add security and adjacent layers
- Proposing architecture changes: read the full target context
- Understanding an existing repository: start with intake material and any relevant solution-space record