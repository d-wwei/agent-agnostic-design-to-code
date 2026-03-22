#!/usr/bin/env python3
"""Evaluate generated code against design structure.

Reads generated code from benchmark/output/ and scores structural fidelity
against the design rubric in benchmark/design-structure.json.

Output: prints "structural_score: XX" (0-100) to stdout.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
DESIGN_FILE = os.path.join(SCRIPT_DIR, "design-structure.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def load_generated_code():
    """Load all generated code files from output directory."""
    code = ""
    if not os.path.isdir(OUTPUT_DIR):
        return code
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        fpath = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(fpath):
            with open(fpath, "r", errors="replace") as f:
                code += f.read() + "\n"
    return code


def load_design():
    with open(DESIGN_FILE, "r") as f:
        return json.load(f)


def check_pattern(code, patterns, case_insensitive=True):
    """Check if any of the patterns match in the code."""
    flags = re.IGNORECASE if case_insensitive else 0
    for p in patterns:
        if re.search(p, code, flags):
            return True
    return False


def evaluate(code, design):
    """Evaluate code against design checks. Returns (score, max_score, details)."""
    checks = design["checks"]
    results = []
    total_score = 0
    max_score = 0

    # --- Structural checks ---
    structural_patterns = {
        "S01": [
            r"(topbar|top-bar|header|navbar|nav-bar|app-bar)",
            r"(agent.*select|select.*agent|dropdown.*agent)",
            r"(settings|gear|cog).*icon",
        ],
        "S02": [
            r"(flex.*center|items-center|justify-center|align-items:\s*center)",
            r"(main|content|empty|welcome|onboard)",
        ],
        "S03": [
            r"(logo|brand|globe).*?(rounded|border-radius|cornerRadius)",
            r"(rounded-xl|rounded-2xl|rounded-lg).*?(border|shadow)",
            r"(icon|logo).*?(container|frame|wrapper|box)",
        ],
        "S04": [
            r"ACP\s*Browser\s*Client",
        ],
        "S05": [
            r"Connect\s*(AI\s*)?agents?\s*to\s*(your\s*)?browser",
        ],
        "S06": [
            r"(step|步骤).*?[123]",
            r"(Start\s*Proxy|Select\s*Agent|Start\s*Chatting)",
        ],
        "S07": [
            r"npx\s*@anthropic",
            r"(code|pre|mono|command).*?(npx|proxy)",
            r"acp-browser-proxy",
        ],
        "S08": [
            r"(documentation|docs|help)",
            r"Need\s*help",
        ],
        "S09": [
            r"(input|message|chat).*?(bar|area|field|box)",
            r"(type.*message|placeholder|waiting.*connection)",
        ],
        "S10": [
            r"(attach|paperclip|clip|upload).*?(btn|button|icon)",
            r"(send|submit|arrow).*?(btn|button|icon)",
        ],
    }

    for check in checks["structural"]:
        cid = check["id"]
        weight = check["weight"]
        max_score += weight
        patterns = structural_patterns.get(cid, [])
        passed = check_pattern(code, patterns) if patterns else False
        # Special case: S06 needs multiple steps
        if cid == "S06":
            step_count = 0
            for label in ["Start Proxy", "Select Agent", "Start Chatting"]:
                if re.search(re.escape(label), code, re.IGNORECASE):
                    step_count += 1
            passed = step_count >= 3
        score = weight if passed else 0
        total_score += score
        results.append({"id": cid, "desc": check["desc"], "passed": passed, "score": score, "max": weight})

    # --- Layout checks ---
    layout_patterns = {
        "L01": [
            r"flex.*col",
            r"flex-direction:\s*column",
            r"display:\s*flex.*flex-direction:\s*column",
            r"flex-col",
        ],
        "L02": [
            r"(justify-between|justify-content:\s*space-between|space_between)",
            r"(topbar|header|nav).*?(flex|display).*?(between|space)",
        ],
        "L03": [
            r"(flex-1|flex-grow|grow).*?(items-center|align-items.*center)",
            r"(items-center|justify-center).*?(flex-1|grow)",
            r"(center|middle).*?(content|main)",
        ],
        "L04": [
            r"(gap|space-y|margin-bottom|mb-).*?(4|5|6|8|16|20|24)",
            r"gap:\s*\d+",
        ],
        "L05": [
            r"(step|item).*?(flex.*row|horizontal|flex-row|inline-flex)",
            r"(flex.*row|flex-row).*?(step|number|badge)",
            r"(flex|row|horizontal).*?(circle|badge|number)",
        ],
        "L06": [
            r"(sticky.*bottom|fixed.*bottom|mt-auto|margin-top:\s*auto)",
            r"(bottom|footer|input.*bar)",
        ],
    }

    for check in checks["layout"]:
        cid = check["id"]
        weight = check["weight"]
        max_score += weight
        patterns = layout_patterns.get(cid, [])
        passed = check_pattern(code, patterns)
        score = weight if passed else 0
        total_score += score
        results.append({"id": cid, "desc": check["desc"], "passed": passed, "score": score, "max": weight})

    # --- Visual checks ---
    visual_patterns = {
        "V01": [
            r"(#0f1117|#0F1117|#111|#0d0f14|#0e1015|rgb\(15|bg-\[#0)",
            r"(bg-gray-950|bg-slate-950|bg-zinc-950|bg-neutral-950|dark.*background)",
            r"(background.*dark|dark.*theme|bg-primary|bg-dark)",
        ],
        "V02": [
            r"(#1e2538|#1E2538|#1a1f2e|#1c2333|#1d2432)",
            r"(bg-gray-800|bg-slate-800|bg-zinc-800|bg-card)",
            r"(card.*background|surface|elevated)",
        ],
        "V03": [
            r"(#6ee7b7|#6EE7B7|#5ddba8|emerald|green-300|teal)",
            r"(accent|primary.*green|green.*accent|text-emerald)",
        ],
        "V04": [
            r"(border|outline|ring).*?(card|container|box|frame)",
            r"border.*?(white|gray|slate|zinc|opacity|\/)",
        ],
        "V05": [
            r"(shadow|box-shadow|drop-shadow)",
        ],
        "V06": [
            r"(status|dot|indicator|connected|online).*?(circle|dot|badge|green)",
            r"(w-2|w-3|h-2|h-3|size-2|size-3).*?(rounded-full|circle)",
        ],
        "V07": [
            r"(step.*number|badge|circle).*?(bg|background).*?(green|accent|emerald|#6ee7b7)",
            r"(rounded-full|border-radius.*50).*?(step|number|badge)",
            r"(w-6|w-7|w-8|h-6|h-7|h-8|size-6|size-7|size-8).*?(rounded-full|circle)",
        ],
    }

    for check in checks["visual"]:
        cid = check["id"]
        weight = check["weight"]
        max_score += weight
        patterns = visual_patterns.get(cid, [])
        passed = check_pattern(code, patterns)
        score = weight if passed else 0
        total_score += score
        results.append({"id": cid, "desc": check["desc"], "passed": passed, "score": score, "max": weight})

    # --- Typography checks ---
    typo_patterns = {
        "T01": [
            r"(DM\s*Sans|dm-sans|font-family.*sans)",
            r"(font-sans|Inter|system-ui)",
        ],
        "T02": [
            r"(text-xl|text-2xl|text-lg|font-size:\s*(18|20|22|24)px|fontSize.*?(18|20|22|24))",
            r"(font-bold|font-semibold|fontWeight.*?(600|700|bold))",
        ],
        "T03": [
            r"(text-gray-400|text-gray-500|text-slate-400|text-muted|#6b7280|#9ca3af)",
            r"(text-secondary|muted|subdued|opacity.*?(50|60|70))",
        ],
        "T04": [
            r"(font-mono|monospace|Courier|Menlo|Consolas|code|pre)",
        ],
    }

    for check in checks["typography"]:
        cid = check["id"]
        weight = check["weight"]
        max_score += weight
        patterns = typo_patterns.get(cid, [])
        passed = check_pattern(code, patterns)
        score = weight if passed else 0
        total_score += score
        results.append({"id": cid, "desc": check["desc"], "passed": passed, "score": score, "max": weight})

    # Normalize to 0-100
    normalized = round(total_score / max_score * 100) if max_score > 0 else 0
    return normalized, total_score, max_score, results


def main():
    code = load_generated_code()
    if not code.strip():
        print("structural_score: 0")
        print("error: no generated code found in benchmark/output/")
        sys.exit(1)

    design = load_design()
    normalized, raw, max_score, results = evaluate(code, design)

    # Print detailed results
    print(f"=== Design Fidelity Evaluation ===")
    print(f"Raw score: {raw}/{max_score}")
    print()
    categories = {}
    for r in results:
        cat = r["id"][0]
        if cat not in categories:
            categories[cat] = {"name": {"S": "Structural", "L": "Layout", "V": "Visual", "T": "Typography"}[cat], "items": []}
        categories[cat]["items"].append(r)

    for cat_key, cat in categories.items():
        cat_score = sum(i["score"] for i in cat["items"])
        cat_max = sum(i["max"] for i in cat["items"])
        print(f"[{cat['name']}] {cat_score}/{cat_max}")
        for item in cat["items"]:
            mark = "PASS" if item["passed"] else "FAIL"
            print(f"  [{mark}] {item['id']}: {item['desc']} ({item['score']}/{item['max']})")
        print()

    # The metric line - must be greppable
    print(f"structural_score: {normalized}")


if __name__ == "__main__":
    main()
