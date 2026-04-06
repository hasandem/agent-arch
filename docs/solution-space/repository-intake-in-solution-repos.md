# Repository Intake in Solution Repositories

## Agent-sammendrag

When a solution repository first needs to be understood, the recommended path is
to start with intake, not implementation. This gives the team a small,
traceable way to document alternatives, selected direction, and guardrails
before deciding what should stay local and what should be escalated into shared
architecture.

## Problem

We need a repeatable way to look at another repository and answer three
questions:

1. What is the current solution shape?
2. Which alternatives are realistic?
3. What learning should remain local, and what should become shared
   architecture?

Without this step, teams jump too quickly from local observations to proposed
normative architecture changes.

## Context

- **Related repositories:** solution repositories that consume central architecture
- **Related intake brief:** expected starting point when a repository must first be understood
- **Typical modes:** legacy, pilot, third-party

## Status

- [ ] Exploratory
- [x] Selected for pilot
- [ ] Recommended pattern
- [ ] Superseded
- [ ] Rejected

## Alternatives Considered

### Option A: Go straight to `arch-consume`

Use the normal implementation workflow immediately and rely on architecture
reading plus escalation if anything looks unclear.

### Option B: Add a separate intake step with its own lightweight artifacts

Start by clarifying scope, first evaluation unit, and first deliverable. Capture
alternatives and the selected direction in solution-space before implementation.

### Option C: Put all reasoning directly into ADRs

Use ADRs as the main place to document alternatives and chosen direction from
the start.

## Chosen Solution

Choose Option B.

The first step in a repository-alignment exercise should be `arch-intake`, with
an intake brief and one or more solution-space records. This keeps the first
deliverable small, makes alternatives visible, and avoids treating pilot or
legacy designs as hidden target architecture.

## Rejected Options

### Option A was rejected as the default

It moves too quickly into implementation thinking and does not leave enough room
to compare alternatives or document why one path was chosen.

### Option C was rejected as the default

ADRs are important for traceable decisions, but they are less suitable as the
first shared workspace for exploration and comparison across repositories.

## Guardrails and Assumptions

- intake should begin with one explicit evaluation unit, not a whole repository
- the record should show both alternatives and the chosen path
- pilot or experimental designs should not become normative architecture by
  default
- reusable learning should move forward through normal escalation and review

## Business Impact

Makes it easier for stakeholders to see why one direction was chosen and what
was deliberately left out of scope.

## Information Impact

Improves traceability between intake notes, solution choices, and later updates
to shared contracts or information models.

## Application Impact

Gives solution repositories a clearer entry point before implementation and
helps agents separate repository understanding from change implementation.

## Traceability

- **Related issue:** hasandem/agent-arch#1
- **Related ADR:** not yet created
- **Related normative architecture update:** method and skill updates in this repository