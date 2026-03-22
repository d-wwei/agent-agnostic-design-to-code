#!/usr/bin/env bash
# Benchmark runner: generates code from design using current scaffold, then evaluates.
# Usage: bash benchmark/run.sh
# Output: prints structural_score to stdout (last line)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCHMARK_DIR="$REPO_DIR/benchmark"
OUTPUT_DIR="$BENCHMARK_DIR/output"
DESIGN_FILE="$BENCHMARK_DIR/design-structure.json"

# Clean previous output
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Read scaffold files to assemble context
SPEC_TEMPLATE=$(cat "$REPO_DIR/specs/implementation-spec.template.yaml")
COMPONENT_MAP=$(cat "$REPO_DIR/specs/component-map.template.json")
WORKFLOW_SOP=$(cat "$REPO_DIR/workflows/agent-execution-sop.md")
DESIGN_STRUCTURE=$(cat "$DESIGN_FILE")

# Build the generation prompt
PROMPT=$(cat <<'PROMPT_END'
You are a frontend developer implementing a design with pixel-perfect fidelity.

## Task
Generate a complete, single-file React component with Tailwind CSS that faithfully reproduces the "Welcome State" screen of the ACP Browser Client app.

## Design Structure (Ground Truth)
The following JSON describes the exact structure, layout, colors, typography, and components of the design:

PROMPT_END
)

PROMPT="$PROMPT
$DESIGN_STRUCTURE

## Scaffold Workflow
Follow this execution workflow for maximum design fidelity:

$WORKFLOW_SOP

## Implementation Spec Template (reference for structure)
$SPEC_TEMPLATE

## Requirements
1. Output a single React component file (WelcomeScreen.tsx) using TypeScript + Tailwind CSS
2. Match the EXACT color tokens from the design (use the hex values directly in Tailwind arbitrary values or CSS variables)
3. Match the EXACT layout structure: vertical root → TopBar + EmptyContent + InputBar
4. Match ALL text content verbatim
5. Use lucide-react for icons
6. Include ALL 3 steps with their exact content
7. Include the code block in Step 1
8. Include the input bar with all buttons
9. Dark theme throughout
10. Use DM Sans font family

## Output Format
Output ONLY the component code. No explanations, no markdown code fences, just the raw TypeScript/React code.
"

# Run claude --print to generate code
echo "[benchmark] Generating code via claude --print..." >&2
echo "$PROMPT" | claude --print --output-format text > "$OUTPUT_DIR/WelcomeScreen.tsx" 2>/dev/null

# Check if generation succeeded
if [ ! -s "$OUTPUT_DIR/WelcomeScreen.tsx" ]; then
    echo "structural_score: 0"
    echo "error: claude --print produced no output" >&2
    exit 1
fi

echo "[benchmark] Generation complete. Evaluating..." >&2

# Run evaluation
python3 "$BENCHMARK_DIR/evaluate.py"
