# Design-to-Code MVP Architecture

## Purpose

This MVP exists to reduce quality loss between design intent and production code across different design inputs and different coding agents.

It does this by inserting a stable middle layer between design input and code.

## Problem Model

### Failure Modes

1. Design input is visually rich but operationally incomplete.
   It shows what something looks like, but usually not what is negotiable, what must stay exact, how it should map to code, or how fidelity will be judged.
2. Different agents produce different implementations from the same input.
   The missing piece is a shared, versioned execution truth in the repository.
3. Agents tend to improvise.
   Without a fixed process, translation, mapping, implementation, and validation collapse into one opaque step.
4. Existing repo patterns pull the result off design.
   Legacy components and default UI habits often override design intent unless mapping rules are explicit.
5. Most workflows lack a correction loop.
   If fidelity is not defined as an acceptance problem, the first plausible output becomes the final output.

## Why Design Access Alone Is Not Enough

Screenshots, exports, MCP, and design inspectors help the agent perceive the design.
They do not by themselves define:

- semantic structure
- implementation boundaries
- approved component mappings
- forbidden substitutions
- responsive rules
- interaction states
- pass and fail criteria

Perception is not execution control.

## Core System Decision

The system uses a canonical middle layer called the implementation spec.

That spec is the source of execution truth because it translates design intent into:

- structure
- semantics
- token roles
- responsive behavior
- component expectations
- acceptance criteria

## Minimum Subsystems

### 1. Design Input Layer

Stores raw screenshots, exports, notes, or inspector data.

Why it exists:
Preserves source evidence without forcing one design tool.

### 2. Implementation Specification Layer

Stores normalized, tool-agnostic requirements for the feature or page.

Why it exists:
Prevents every agent from re-interpreting the design from scratch.

### 3. Component Mapping Layer

Stores how spec elements map to real repo components or new components.

Why it exists:
Prevents silent generic substitutions and repo-driven drift.

### 4. Execution Workflow Layer

Stores the step-by-step SOP agents must follow.

Why it exists:
Reduces improvisation and makes tasks repeatable across agents.

### 5. Acceptance Layer

Stores the completion checklist and evidence expectations.

Why it exists:
Turns fidelity into a verification loop instead of a one-shot generation event.

## Repository Roles

- `AGENTS.md`
  Stable agent instructions for this repo
- `docs/architecture.md`
  System rationale and boundaries
- `specs/implementation-spec.template.yaml`
  Canonical implementation spec template
- `specs/component-map.template.json`
  Canonical component mapping template
- `workflows/agent-execution-sop.md`
  Required execution procedure
- `templates/acceptance-checklist.md`
  Completion gate

## MVP Working Model

For each task:

1. Gather raw design input from any tool.
2. Fill the implementation spec.
3. Fill the component map.
4. Implement against the spec, not directly against the screenshot.
5. Review against the acceptance checklist.
6. Revise until acceptable.

## Scope of This MVP

This scaffold is intentionally small.

It does not assume:

- one design vendor
- one coding agent
- one IDE
- automated screenshot diffing
- a mature design token pipeline

It is designed to be usable immediately by a solo operator and expandable later.
