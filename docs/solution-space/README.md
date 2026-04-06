# Solution Space

## Purpose

This folder holds solution-near architecture records.

The purpose is to make alternatives, chosen solutions, and guardrails visible
to other repositories without turning every design choice into normative
architecture.

## What belongs here

- intake-driven findings from another repository
- alternative solutions that were considered
- the chosen solution and why it was chosen
- rejected options and the reasons behind them
- guardrails, assumptions, and cross-layer impact
- links to any later ADR, issue, or normative architecture update

## What does not belong here

- the canonical target architecture for the organization
- undocumented local backlog notes
- implementation details that only matter inside one repository

## Status model

Each record should state its status clearly:

- `exploratory`
- `selected-for-pilot`
- `recommended-pattern`
- `superseded`
- `rejected`

## Recommended record shape

Use a simple structure that is easy for both people and agents to read:

1. Agent summary when useful
2. Problem and context
3. Source repositories or materials
4. Alternatives considered
5. Chosen solution
6. Rejected options
7. Guardrails and assumptions
8. Business, information, and application impact
9. Status and next step
10. Traceability links

## Example

- [Repository intake in solution repositories](repository-intake-in-solution-repos.md)
- [Information flow pattern from a pilot repository](information-flow-pattern-from-pilot.md)

## Reading support

You can read these records directly with `arch-read`, and the tool also supports
lightweight solution-space commands:

- `arch-read --solution-space` to list available records
- `arch-read --search-solution-space <query>` to search only within solution-space

## Relationship to normative architecture

Solution-space records support architecture work, but they are not the final
source of truth.

If a pattern becomes normative, it should be moved into the canonical
architecture documents or traced through an ADR and a controlled update.