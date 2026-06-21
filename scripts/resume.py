# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5"]
# ///
"""Unified local and CI interface for labeled resume profiles."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader

from resume_core import ROOT, ResumeValidationError, load_catalog, profiles_for_target, resolve_profile, validate


def run_script(name: str, *args: str) -> None:
    command = ["uv", "run", str(ROOT / "scripts" / name), *args]
    subprocess.run(command, cwd=ROOT, check=True)


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and publish labeled resume profiles.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("list")
    for name in ("resolve", "readme", "pdf", "rxresume", "build"):
        sub = commands.add_parser(name)
        sub.add_argument("--profile")
        if name == "rxresume":
            sub.add_argument("--apply", action="store_true")
    commands.add_parser("check")
    args = parser.parse_args()

    try:
        catalog = load_catalog()
        validate(catalog)
    except (OSError, json.JSONDecodeError, ResumeValidationError) as error:
        print(f"resume validation failed:\n{error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print("resume.json is valid")
    elif args.command == "list":
        for label, profile in catalog["profiles"].items():
            print(f"{label:16} slug={profile['slug']:18} targets={','.join(profile['targets'])}")
    elif args.command == "resolve":
        print(json.dumps(resolve_profile(catalog, args.profile or "default"), indent=2, ensure_ascii=False))
    elif args.command == "readme":
        run_script("build_readme.py", "--profile", args.profile or "default")
    elif args.command == "pdf":
        extra = ("--profile", args.profile) if args.profile else ()
        run_script("resume_pdf.py", *extra)
    elif args.command == "rxresume":
        extra = ["--profile", args.profile] if args.profile else []
        if args.apply:
            extra.append("--apply")
        run_script("resume_push.py", *extra)
    elif args.command == "build":
        readme_profile = args.profile or "default"
        if not args.profile or "readme" in catalog["profiles"][args.profile]["targets"]:
            run_script("build_readme.py", "--profile", readme_profile)
        extra = ("--profile", args.profile) if args.profile else ()
        if not args.profile or "pdf" in catalog["profiles"][args.profile]["targets"]:
            run_script("resume_pdf.py", *extra)
    elif args.command == "check":
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            temp_path = Path(temp)
            readme = temp_path / "README.md"
            run_script("build_readme.py", "--out", str(readme.relative_to(ROOT)))
            if readme.read_bytes() != (ROOT / "README.md").read_bytes():
                print("README.md is stale; run: uv run scripts/resume.py readme", file=sys.stderr)
                return 1
            pdf_dir = temp_path / "pdf"
            run_script("resume_pdf.py", "--out-dir", str(pdf_dir.relative_to(ROOT)))
            for generated in pdf_dir.glob("*.pdf"):
                committed = ROOT / "resume" / generated.name
                if not committed.exists() or pdf_text(generated) != pdf_text(committed):
                    print(f"{committed.relative_to(ROOT)} is stale", file=sys.stderr)
                    return 1
        subprocess.run(["bun", "run", "build"], cwd=ROOT / "web", check=True)
        print("generated outputs and website are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
