# Acceptance Loop

Use this reference when deciding whether a design-to-code task is actually done.

## Core rule

Treat fidelity as an acceptance problem, not a generation problem.

## Review order

1. Structural fidelity
2. Component fidelity
3. Visual fidelity
4. Responsive fidelity
5. Interaction fidelity
6. Evidence and traceability

## Pass criteria

Pass only when:

- the implementation still matches the current spec
- the component map still describes the shipped code
- the most important visual and behavioral requirements hold
- evidence exists for the claim that the task is complete

## Fail criteria

Fail when:

- a generic substitution weakened an important design element
- the implementation no longer matches the spec
- responsive or interaction behavior is missing
- the output is "close enough" but not explicitly accepted

## Revision rule

Fix the highest-impact fidelity gaps first, then re-run the relevant checks.

Do not compensate for drift with narrative explanations unless the user explicitly accepts the tradeoff.
