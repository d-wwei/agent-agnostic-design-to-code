# Design Source Preprocessing

Use this reference at the start of every design-to-code task. Before writing any code, identify the design source type and extract specifications using the appropriate strategy.

## Why this matters

Different source types provide different levels of precision. An HTML file gives you exact pixel values; a PNG gives you visual intent that requires interpretation. Choosing the wrong extraction strategy wastes time and introduces drift from the first line of code.

## Source type detection

Check what the user or task provides:

| Source type | How to detect | Precision level |
|-------------|--------------|-----------------|
| Image (PNG/JPG/PDF) | File extensions, `front-end design/` directories | Low — requires visual interpretation |
| HTML/CSS | `.html`, `.css` files or live URLs | High — exact values readable from code |
| Figma | `figma.com/design/` URLs or Figma file keys | High — exact values via MCP API |
| Paper (.pen) | `.pen` files or active Paper editor | High — exact values via MCP API |

If the source is ambiguous, check the task spec or ask the user.

## Image sources (PNG/JPG/PDF)

Images are the least precise source. Compensate with structured preprocessing.

### Step 1: Inventory all views

Scan the design directory for all distinct screens/views. Name and number them:

```
01 — Home (default)
02 — Home (scrolled)
03 — Dashboard (sidebar expanded)
04 — Dashboard (sidebar collapsed)
05 — Design Comparison
06 — Browser Side Panel
```

### Step 2: Create multi-resolution tiers

For each design image, create 3 resolution levels:

```bash
mkdir -p compressed/ tiny/
# Compressed (600px) — for detailed comparison
for f in *.png; do sips -Z 600 "$f" --out "compressed/$f"; done
# Tiny (400px) — for quick scoring and context-safe comparison
for f in *.png; do sips -Z 400 "$f" --out "tiny/$f"; done
```

Use tiny/ for routine comparison (saves context window). Use compressed/ when investigating specific pixel-level differences. Use original only for final pixel-perfect verification.

### Step 3: Determine viewport dimensions

Estimate the target viewport from image aspect ratios:

- Desktop: typically 1440x900 or 1920x1080
- Tablet: typically 768x1024
- Mobile: typically 390x844
- Side panel: typically 350-390px wide

Record the target viewport in the implementation spec.

### Step 4: Extract what you can

From images alone, you can reliably extract:

- Layout structure (grid vs flex, column count, section ordering)
- Approximate color palette (use eyedropper tools or AI vision)
- Typography hierarchy (heading vs body vs label scale)
- Component patterns (cards, panels, nav bars)

You cannot reliably extract: exact pixel values for padding/gap/margin, exact font sizes, exact border-radius values, exact opacity values. These must be iterated through the fidelity loop.

### Image comparison during implementation

When comparing your implementation against image designs:

1. Take a browser screenshot at the same viewport size
2. Compress to the same resolution tier as the reference
3. Compare region-by-region, not the full page at once
4. For focused comparison, crop both images to the same region

## HTML/CSS sources

HTML/CSS is the most precise source. Read it, don't guess.

### Step 1: Read structure

```
Read the HTML file to understand:
- Page structure (sections, containers, grids)
- Component patterns (class names, nesting)
- Navigation and routing
- Data binding patterns
```

### Step 2: Extract design tokens from CSS

Read the CSS file to extract:

```css
/* Colors */
:root {
  --bg-main: #10141a;      /* Record every variable */
  --accent-gold: #f0c040;
}

/* Typography */
font-family: 'Space Grotesk', sans-serif;  /* Record every font stack */
font-size: 14px;                            /* Record every size */

/* Spacing */
padding: 16px 20px;    /* Record exact values */
gap: 12px;
border-radius: 8px;
```

### Step 3: Record in implementation spec

Transfer all extracted values into the implementation spec's design tokens section. These are ground truth — do not approximate.

## Figma sources (via MCP)

Use Figma MCP tools for precise extraction without manual inspection.

**MCP ecosystem awareness**: Multiple Figma MCPs exist with different capabilities:

| MCP variant | Tools | Auth | Notes |
|-------------|-------|------|-------|
| Official Figma MCP (remote) | 15+ (`get_design_context`, `get_screenshot`, `get_metadata`, `use_figma`, etc.) | OAuth2 | Full read+write, design system search, Code Connect |
| Framelink / GLips `figma-developer-mcp` | 2 (`get_figma_data`, `download_figma_images`) | API key | Read-only, YAML output optimized for LLM consumption |
| Enterprise forks (e.g. `@org/figma-developer-mcp`) | 2+ (base + custom) | API key | May add internal component recognition |

Detect which MCP is available before planning extraction. If only Framelink is available, you won't have `get_variable_defs` or `search_design_system` — extract tokens manually from the returned design data instead.

### Step 1: Get structure overview

```
get_metadata(nodeId, fileKey)
→ Returns XML with all node IDs, types, names, positions, sizes
→ Use this to identify all major sections and their node IDs
```

### Step 2: Get design context per section

```
get_design_context(nodeId, fileKey)
→ Returns: reference code (React+Tailwind), screenshot, contextual hints
→ Code Connect snippets map to actual codebase components
→ Adapt the reference code to your target stack
```

### Step 3: Extract design tokens

```
get_variable_defs(nodeId, fileKey)
→ Returns all design variables: colors, spacing, typography tokens
→ Map these directly to CSS custom properties
```

### Step 4: Search for reusable components

```
search_design_system(query, fileKey)
→ Find existing design system components that match your needs
→ Import via importComponentByKeyAsync instead of recreating
```

### Recommended Figma extraction order

1. `get_metadata` on root → map out all sections
2. `get_variable_defs` → extract full token system
3. `get_design_context` on each major section → get reference code + screenshots
4. `search_design_system` for any component you're about to create → check if it exists first

## Paper sources (via MCP)

Use Paper MCP tools for precise extraction from .pen files.

### Step 1: Get editor state

```
get_editor_state({include_schema: true})
→ Returns: active file, page info, artboard list with dimensions, font families
→ Schema is needed before any read/write operations
```

### Step 2: Read node structure

```
batch_get({filePath, patterns: [{type: "frame"}], readDepth: 2})
→ Returns all top-level frames with their children
→ Identify major sections by name and dimensions
```

### Step 3: Extract exact styles

```
get_computed_styles({nodeIds: ["artboard-id", "section-id", ...]})
→ Returns exact CSS properties per node: colors, padding, gap, fonts, borders
→ These are ground truth values — use them directly
```

### Step 4: Get code representation

```
get_jsx({nodeId, format: "inline-styles"})
→ Returns JSX with inline styles — exact pixel values
→ Use as reference code, adapt to your target stack
```

### Step 5: Visual reference per section

```
get_screenshot({nodeId})
→ Returns base64 image of the specific node
→ Use for comparison during the fidelity loop
```

### Recommended Paper extraction order

1. `get_editor_state` → understand file structure
2. `get_basic_info` → list artboards with dimensions
3. `batch_get` on each artboard → map out sections
4. `get_computed_styles` on all key nodes → extract exact values
5. `get_jsx` on complex sections → get reference code
6. `get_screenshot` on each artboard → save as comparison references

## Design source quality rating

After extraction, rate the design source quality before implementation begins. This prevents wasted effort iterating on unreliable data.

### Rating rubric

| Grade | Criteria | Expected fidelity ceiling | Iteration strategy |
|-------|----------|--------------------------|-------------------|
| **A — Production-ready** | API source (Figma/Paper) with complete design tokens, named components, consistent naming conventions, and comprehensive state variants | 95%+ | Extract exact values; iterate on polish only |
| **B — Structured** | API source with partial tokens, or well-structured HTML/CSS with design system | 85–95% | Extract what's available; iterate on gaps in fidelity loop |
| **C — Visual-only** | High-res images with clear layout, consistent spacing, readable typography | 70–85% | Approximate from vision; expect significant fidelity loop iteration |
| **D — Incomplete** | Low-res images, partial screens, missing states, inconsistent design | 50–70% | Set expectations with user; focus on structure over pixel precision |

### Quality signals to check

**Positive signals** (raise the grade):
- Design tokens / CSS variables are defined and used consistently
- Components are named and structured (not flattened groups)
- All interaction states are represented (hover, active, disabled, error, empty)
- Typography hierarchy is explicit (heading/body/label/caption levels)
- Spacing is systematic (consistent padding/gap multiples)

**Negative signals** (lower the grade):
- Flattened/rasterized layers without structure
- Inconsistent spacing (different padding in similar components)
- Missing states (only default state shown)
- Hardcoded one-off values instead of token references
- Complex components exported as single images
- Design data too large for AI to fully parse (common with deeply nested Figma components)

### Recording the rating

Add the quality rating to the implementation spec:

```yaml
design_source:
  type: figma  # or image, html, paper
  quality_grade: B
  quality_notes: "Tokens defined for colors but not spacing. Navigation component is flattened. Missing error states for form inputs."
  precision_limits:
    - "Spacing values approximate — iterate in fidelity loop"
    - "Nav component requires manual decomposition"
  expected_fidelity_ceiling: 90%
```

This rating informs iteration strategy: for grade A/B sources, target the ceiling aggressively. For grade C/D sources, align with the user on acceptable fidelity before deep iteration — diminishing returns set in earlier.

## Output

After preprocessing, you should have:

1. A complete inventory of all views/screens
2. Design tokens (colors, fonts, spacing) recorded in the implementation spec
3. Multi-resolution reference images (for image sources) or saved screenshots (for API sources)
4. Target viewport dimensions
5. Component structure mapped
6. **Design source quality rating** with precision limits documented

Only then proceed to step 1 of the main workflow (discover repository contract).
