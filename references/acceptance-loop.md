# Acceptance Loop

Use this reference both **during** and **after** implementation. Fidelity is checked continuously, not just at the end.

## Core rule

Treat fidelity as an iterative optimization problem, not a one-shot generation problem.

## Two modes

### Mode 1: Continuous (during implementation)

Run after each implementation phase and after significant changes. The goal is early detection — catch drift before it compounds.

**Per-phase checks:**

| Phase | What to check |
|-------|--------------|
| 1. Structure | All views exist and are navigable |
| 2. Data | Content is populated, no empty containers |
| 3. Spacing & Typography | Visual rhythm matches, heading hierarchy is clear |
| 4. Viewport Proportions | Key sections match design proportions |
| 5. Component States | Each state variant matches its design reference |
| 6. Detail Polish | Gradients, shadows, borders match at compressed resolution |
| 7. Standalone Components | Standalone and integrated versions are consistent |

**Continuous check protocol:**

1. Screenshot the implementation at the same viewport as the design
2. Compare region-by-region against the design reference
3. Note the top 3 visible differences
4. Fix the highest-impact difference first
5. Re-screenshot and re-compare
6. When no visible differences remain at compressed resolution, the phase passes

See [fidelity-loop.md](fidelity-loop.md) for the full single-variable experiment protocol.

### Mode 2: Final (after implementation converges)

Run when the fidelity loop has stabilized. This is the formal acceptance gate.

## Quantitative metrics

Track these three metrics throughout the task. They provide an objective complement to qualitative visual review.

### 1. Visual fidelity score (%)

Region-by-region assessment of how closely the implementation matches the design.

| Score range | Meaning |
|-------------|---------|
| 90–100% | Pixel-perfect or near-perfect — differences invisible at compressed resolution |
| 75–89% | High fidelity — structure and rhythm correct, minor spacing/color drift |
| 50–74% | Medium fidelity — layout correct but noticeable visual differences |
| < 50% | Low fidelity — significant structural or visual divergence |

How to estimate: after each fidelity loop round, rate each region (header, main, sidebar, footer, modals) on a 1–5 scale. Average across regions, multiply by 20 to get a percentage. Record in the fidelity progress TSV.

### 2. Component mapping accuracy (%)

Percentage of design components that were correctly mapped to code counterparts.

```
accuracy = (components correctly mapped / total components in spec) × 100
```

A component is "correctly mapped" when:
- it uses the specified repo component (or justified primitive composition)
- it preserves the intended hierarchy and behavior
- no silent substitutions were made

Target: 100%. Any gap should be documented in the component map with explicit rationale.

### 3. Design token coverage (%)

Percentage of design-specified tokens (colors, spacing, typography, borders) that are used in the implementation instead of hardcoded or approximated values.

```
coverage = (tokens used from design system / total style values in implementation) × 100
```

How to check: search the implementation for hardcoded color hex values, magic-number pixel values, and inline font specifications that should reference design tokens. Each hardcoded value that has a corresponding design token is a coverage miss.

Target: 95%+ for API-sourced designs (Figma/Paper), 80%+ for image-sourced designs.

### Recording metrics

Add a metrics summary to the acceptance checklist or fidelity progress log:

```
## Metrics Summary
- Visual fidelity: 87% (header 95%, main 90%, sidebar 80%, footer 85%)
- Component mapping: 100% (12/12 components mapped)
- Design token coverage: 92% (3 hardcoded values remain — documented in spec)
```

## Final review order

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
- the fidelity loop has converged (no further improvements possible at reasonable cost)

## Fail criteria

Fail when:

- a generic substitution weakened an important design element
- the implementation no longer matches the spec
- responsive or interaction behavior is missing
- the output is "close enough" but not explicitly accepted
- component states are incomplete (missing collapsed, error, hover, etc.)

## Theme & CSS Variable Chain Verification

Before visual pass/fail, verify:

1. HTML root has the correct theme class (`<html class="dark">` or `<html class="light">`)
2. CSS file contains matching selectors (`.dark { --bg: #0a0a0a; ... }`)
3. Components use `var(--bg)`, not hardcoded `#0a0a0a`
4. If a theme store exists, its default value matches the HTML class
5. A runtime sync effect keeps HTML class and store aligned

If any layer is missing, mark as **fail** — the theme will not activate correctly regardless of whether individual colors look right in a specific OS setting.

## Screenshot Comparison

When a design reference is available:

1. Take a screenshot of the implementation at the same viewport size
2. Use the appropriate resolution tier: tiny (400px) for structural check, compressed (600px) for detail check
3. Compare region-by-region: header, main content, sidebar, footer
4. Check for: color accuracy, spacing consistency, typography matching, layout alignment
5. Flag any visible drift — even small cumulative differences indicate problems

When drift is found, prefer switching to inline styles with exact pixel values from the design API over adjusting utility classes.

## CSS Framework Pitfalls to Check

- **Tailwind approximation**: verify that `py-2.5` actually equals the design's padding value (it may be 8px instead of 10px)
- **`space-y-N` + Fragments**: verify spacing is consistent when children use React Fragments
- **Missing CSS variable definitions**: verify all `var(--name)` references have corresponding definitions
- **position:sticky failures**: verify sticky elements actually stick (they may silently fail)

See [tactical-patterns.md](tactical-patterns.md) for the full pitfalls list and workarounds.

## Revision rule

Fix the highest-impact fidelity gaps first, then re-run the relevant checks.

Do not compensate for drift with narrative explanations unless the user explicitly accepts the tradeoff.

When multiple small gaps remain but no single fix improves the score, try combining 2-3 related changes in one commit.
