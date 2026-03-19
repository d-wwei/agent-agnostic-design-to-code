# Agent Execution SOP

Use this SOP for any design-to-code task.

## Inputs

Required inputs before coding starts:

- filled implementation spec
- filled component map
- target repo context
- raw design inputs for reference

## Step 1: Read The Spec First

- Read the implementation spec before touching code.
- Read the component map before choosing existing components.
- Review raw design input only as supporting evidence.

Required: yes
Mode: agent-driven

## Step 2: Validate Spec Completeness

Confirm the spec is complete enough to implement:

- structure is defined
- key semantics are defined
- breakpoints are defined
- required states are defined
- non-negotiables are defined
- open questions are recorded

If not complete, update the spec first.

Required: yes
Mode: agent-driven, human-confirmed if blocking ambiguity remains

## Step 3: Resolve Component Mapping

For each spec component:

- map it to an existing repo component, primitive composition, or a new component
- document the choice in the component map
- record forbidden substitutions when needed

Required: yes
Mode: agent-driven

## Step 4: Produce A Short Plan

Before implementation, write down:

- files to change
- components to reuse
- components to create
- verification steps
- likely risks

Required: yes
Mode: agent-driven

## Step 5: Implement Against The Spec

- follow the implementation spec
- follow the component map
- do not replace missing clarity with improvisation
- if implementation reality forces a change, update the spec or map

Required: yes
Mode: agent-driven

## Step 6: Verify

Run the strongest checks available in the repo, for example:

- local preview
- screenshots
- responsive inspection
- automated tests

Required: yes
Mode: machine-verified where possible

## Step 7: Review Against Acceptance

Compare the result against `templates/acceptance-checklist.md`.

- mark pass or fail honestly
- capture evidence
- list unresolved gaps

Required: yes
Mode: agent-driven, human-reviewable

## Step 8: Revise Until Acceptable

- fix the highest-impact fidelity gaps first
- re-run verification after changes
- escalate only when a tradeoff needs human approval

Required: yes
Mode: agent-driven

## Step 9: Deliver With Traceability

A task is complete only when the repo contains:

- final implementation
- final implementation spec
- final component map
- completed acceptance checklist

Required: yes
Mode: agent-driven

## Hard Rules

- no direct screenshot-to-code jumps
- no silent component substitutions
- no completion without acceptance evidence
- no unresolved ambiguity hidden inside code
