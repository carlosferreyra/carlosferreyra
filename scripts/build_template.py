# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2",
# ]
# ///
"""
Generates silver-dev-cv/cv.typ from silver-dev-cv/cv.typ.j2 + data/resume.json.

Jinja2 controls structure  — which sections exist, contacts header, layout.
Typst controls rendering   — fonts, spacing, PDF output.
resume.json is SSO         — all content and per-variant config live here.

Each variant in resume.json["variants"] can declare:
  - contacts: ordered list of link IDs to show in the header
  - sections: dict of section_name -> bool to include/exclude entire sections

Usage:
    uv run scripts/build_template.py
    uv run scripts/build_template.py --variant devops
"""

import argparse
import json
import glob
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def detect_installed_version(package: str = "silver-dev-cv") -> str:
    """Read version from typst.toml in the Typst package cache."""
    cache_candidates = [
        Path.home() / "Library" / "Caches" / "typst" / "packages" / "preview",  # macOS
        Path.home() / ".cache" / "typst" / "packages" / "preview",               # Linux
    ]
    for cache in cache_candidates:
        pattern = str(cache / package / "*" / "typst.toml")
        tomls = sorted(glob.glob(pattern))
        if tomls:
            with open(tomls[-1], "rb") as f:
                return tomllib.load(f)["package"]["version"]

    # Fallback: read from existing cv.typ import line
    cv_typ = Path(__file__).parent.parent / "silver-dev-cv" / "cv.typ"
    if cv_typ.exists():
        for line in cv_typ.read_text().splitlines():
            if f"{package}:" in line:
                return line.split(f"{package}:")[1].split('"')[0].split("}")[0]

    return "1.0.2"


def default_sections() -> dict:
    return {
        "about": True,
        "experience": True,
        "skills": True,
        "projects": True,
        "education": True,
        "certifications": True,
    }


def default_contacts() -> list:
    return ["portfolio", "github", "linkedin", "email"]


def render(variant: dict, version: str, repo_root: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(repo_root / "silver-dev-cv")),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    template = env.get_template("cv.typ.j2")
    return template.render(
        version=version,
        contacts=variant.get("contacts", default_contacts()),
        sections={**default_sections(), **variant.get("sections", {})},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render cv.typ.j2 into cv.typ for a given variant.")
    parser.add_argument(
        "--variant",
        default="all",
        help="Variant name from resume.json to use for structure (default: all)",
    )
    parser.add_argument(
        "--out",
        default="silver-dev-cv/cv.typ",
        help="Output .typ file path (relative to repo root)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    resume_path = repo_root / "data" / "resume.json"
    out_path = repo_root / args.out

    resume = json.loads(resume_path.read_text())
    variants = {v["name"]: v for v in resume.get("variants", [])}

    if args.variant not in variants:
        available = ", ".join(variants.keys())
        raise SystemExit(f"ERROR: variant '{args.variant}' not found. Available: {available}")

    variant = variants[args.variant]
    version = detect_installed_version()

    print(f"Rendering cv.typ  variant={args.variant}  silver-dev-cv@{version}")
    content = render(variant, version, repo_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
