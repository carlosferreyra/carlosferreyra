# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2",
# ]
# ///
"""
Renders cv.typ from cv.typ.j2 and compiles one PDF per variant.

For each variant:
  1. build_template renders cv.typ.j2 → cv.typ  (structure from resume.json)
  2. typst compile cv.typ → resume/<name>-<variant>.pdf  (content from resume.json)

Output: resume/carlos-ferreyra-{variant}.pdf

Usage:
    uv run scripts/build_variants.py
    uv run scripts/build_variants.py --variant devops
    uv run scripts/build_variants.py --list
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Reuse render logic from build_template without subprocess overhead
sys.path.insert(0, str(Path(__file__).parent))
from build_template import detect_installed_version, render


def slugify(text: str) -> str:
    """Convert a name like 'Carlos Ferreyra' to 'carlos-ferreyra'."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def pdf_path(person_name: str, variant_name: str) -> str:
    """Return the relative output path for a variant PDF."""
    slug = slugify(person_name)
    if variant_name == "all":
        return f"resume/{slug}.pdf"
    return f"resume/{slug}-{variant_name}.pdf"


def load_variants(resume: dict) -> list[dict]:
    variants = resume.get("variants", [])
    if not any(v["name"] == "all" for v in variants):
        variants = [{"name": "all", "label": "Full Resume"}] + variants
    return variants


def compile_variant(variant: dict, person_name: str, repo_root: Path, cv_typ: Path, version: str) -> bool:
    name = variant["name"]
    out_rel = pdf_path(person_name, name)
    out = repo_root / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)

    # Render cv.typ.j2 → cv.typ for this variant's structure
    cv_typ.write_text(render(variant, version, repo_root))

    cmd = [
        "typst", "compile",
        "--root", str(repo_root),
        "--input", f"variant={name}",
        str(cv_typ),
        str(out),
    ]

    print(f"  [{name}]  →  {out_rel} ...", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size_kb = out.stat().st_size // 1024
        print(f"OK ({size_kb}KB)")
        return True
    else:
        print("FAILED")
        print(result.stderr.strip(), file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-variant PDFs from cv.typ + resume.json.")
    parser.add_argument("--variant", help="Build only this variant (default: all variants)")
    parser.add_argument("--list", action="store_true", help="List available variants and exit")
    parser.add_argument("--cv", default="silver-dev-cv/cv.typ", help="Path to cv.typ (relative to repo root)")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    resume_path = repo_root / "data" / "resume.json"
    cv_typ = repo_root / args.cv
    j2_path = repo_root / "silver-dev-cv" / "cv.typ.j2"

    if not resume_path.exists():
        print(f"ERROR: {resume_path} not found.", file=sys.stderr)
        sys.exit(1)
    if not j2_path.exists():
        print(f"ERROR: {j2_path} not found.", file=sys.stderr)
        sys.exit(1)

    resume = json.loads(resume_path.read_text())
    person_name = resume["personalInfo"]["name"]
    version = detect_installed_version()
    variants = load_variants(resume)

    if args.list:
        print("Available variants:")
        for v in variants:
            print(f"  {v['name']:12}  →  {pdf_path(person_name, v['name'])}")
        return

    if args.variant:
        variants = [v for v in variants if v["name"] == args.variant]
        if not variants:
            print(f"ERROR: variant '{args.variant}' not found in resume.json.", file=sys.stderr)
            sys.exit(1)

    print(f"Building {len(variants)} variant(s) for {person_name}...\n")
    failed = []
    for v in variants:
        ok = compile_variant(v, person_name, repo_root, cv_typ, version)
        if not ok:
            failed.append(v["name"])

    print()
    if failed:
        print(f"Failed variants: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("All variants built successfully.")


if __name__ == "__main__":
    main()
