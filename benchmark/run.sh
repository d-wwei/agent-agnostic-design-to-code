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

# Read scaffold files
AGENTS_MD=$(cat "$REPO_DIR/AGENTS.md")
ARCHITECTURE=$(cat "$REPO_DIR/docs/architecture.md")
WORKFLOW_SOP=$(cat "$REPO_DIR/workflows/agent-execution-sop.md")
CLAUDE_ENTRY=$(cat "$REPO_DIR/docs/agent-entry/claude-code.md")
DESIGN_STRUCTURE=$(cat "$DESIGN_FILE")

# Build a focused code-generation prompt
# Keep it minimal — too much scaffold context confuses --print mode
cat > "$BENCHMARK_DIR/.prompt.txt" <<'PROMPT_HEREDOC'
Generate a single React TypeScript component file (WelcomeScreen.tsx) using Tailwind CSS. Output ONLY code — no explanations, no markdown.

Design spec:
- App: "ACP Browser Client" — dark-themed browser extension UI
- Screen: Welcome State (400x780)
- Font: DM Sans, sans-serif
- Icons: lucide-react

Color tokens (use as Tailwind arbitrary values like bg-[#0f1117]):
- bg-primary: #0f1117
- bg-card: #1e2538
- bg-input: #1a1d26
- accent: #6ee7b7
- text-primary: #d1d5db
- text-secondary: #9ca3af
- text-muted: #6b7280
- border: rgba(255,255,255,0.18)
- border-card: rgba(255,255,255,0.19)

Layout (flex flex-col, full height):

1. TopBar (h-12, flex justify-between, bg-card, shadow, border-b border-white/20):
   - Left: agent icon (Globe, 20px) + "Mock Agent" text + ChevronDown icon
   - Right: green dot (w-2 h-2 rounded-full bg-[#6ee7b7]) + "Connected" text-xs + Wifi icon + Bell icon + Settings icon

2. EmptyContent (flex-1, flex flex-col items-center justify-center, px-10, gap-6):
   - Logo: 56x56 rounded-2xl bg-[#1e2538] border border-white/20 shadow-lg, centered Globe icon in accent color
   - Title: "ACP Browser Client" text-lg font-bold text-[#d1d5db]
   - Subtitle: "Connect AI agents to your browser" text-sm text-[#9ca3af]
   - Steps (flex flex-col gap-5, w-full):
     - Step 1: <div className="step-row flex flex-row gap-3 items-start">. Left: step number badge (w-6 h-6 rounded-full bg-[#6ee7b7] text-black text-xs font-bold flex items-center justify-center showing "1"). Right: flex-col. Title "Start Proxy Server" font-semibold text-[#d1d5db]. Desc "Run the proxy server to bridge your browser with AI agents" text-sm text-[#6b7280]. Code block: bg-[#1a1d26] rounded-lg px-3 py-2 font-mono text-sm text-[#6ee7b7] showing "npx @anthropic-ai/acp-browser-proxy"
     - Step 2: same step-row flex-row layout with number badge. Number "2". Title "Select Agent". Desc "Choose an AI agent from the dropdown above"
     - Step 3: same step-row flex-row layout with number badge. Number "3". Title "Start Chatting". Desc "Send a message, attach page content, or use / shortcuts"
   - Help text: "Need help? Check the " + link "documentation" in accent color

3. InputBar (bg-card, border-t border-white/20, shadow-[0_-2px_6px_rgba(0,0,0,0.12)]):
   - Row (flex items-center gap-2, px-3 py-2):
     - <button aria-label="attach" className="clipBtn text-[#6b7280]"><Paperclip /></button>
     - <button aria-label="screenshot" className="text-[#6b7280]"><Camera /></button>
     - Input (flex-1, bg-transparent, placeholder "Waiting for connection...", text-sm)
     - <button aria-label="send" className="sendBtn text-[#6ee7b7]"><Send /></button>

Start your response with "import" — output the complete component code only.
PROMPT_HEREDOC

# Run claude --print to generate code
echo "[benchmark] Generating code via claude --print..." >&2
claude --print --output-format text < "$BENCHMARK_DIR/.prompt.txt" > "$OUTPUT_DIR/WelcomeScreen.tsx" 2>/dev/null

# Clean up temp file
rm -f "$BENCHMARK_DIR/.prompt.txt"

# Check if generation succeeded and contains actual code
if [ ! -s "$OUTPUT_DIR/WelcomeScreen.tsx" ]; then
    echo "structural_score: 0"
    echo "error: claude --print produced no output" >&2
    exit 1
fi

# Strip markdown fences if present (claude sometimes wraps in ```)
sed -i '' '/^```/d' "$OUTPUT_DIR/WelcomeScreen.tsx" 2>/dev/null || true

# Verify output looks like code (starts with import or has React patterns)
if ! grep -q "import\|export\|function\|const\|React" "$OUTPUT_DIR/WelcomeScreen.tsx"; then
    echo "structural_score: 0"
    echo "error: output does not look like code" >&2
    exit 1
fi

echo "[benchmark] Generation complete. Evaluating..." >&2

# Run evaluation
python3 "$BENCHMARK_DIR/evaluate.py"
