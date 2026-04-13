# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2",
# ]
# ///
"""
Renders README.md from README.md.j2 + data/resume.json.

All data-driven content (name, skills, experience, projects, certifications,
links) is sourced from resume.json. Static narrative sections (GitHub stats
widgets, "Working on" bullets) live in the template itself.

Usage:
    uv run scripts/build_readme.py
    uv run scripts/build_readme.py --out README.md
"""

import argparse
import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_links(raw: list[dict]) -> dict:
    """Flatten links list into a {id: url} dict for easy template access."""
    return {l["id"]: l["url"] for l in raw}


def main() -> None:
    parser = argparse.ArgumentParser(description="Render README.md from README.md.j2 + resume.json.")
    parser.add_argument("--out", default="README.md", help="Output path (relative to repo root)")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    resume_path = repo_root / "data" / "resume.json"
    template_path = repo_root / "README.md.j2"
    out_path = repo_root / args.out

    if not template_path.exists():
        raise SystemExit(f"ERROR: {template_path} not found.")
    if not resume_path.exists():
        raise SystemExit(f"ERROR: {resume_path} not found.")

    resume = json.loads(resume_path.read_text())

    env = Environment(
        loader=FileSystemLoader(str(repo_root)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["slugify"] = slugify

    # Pre-render skills block with aligned columns
    skills_block = "\n".join(
        f"{(g['category'] + ':'):<24} {', '.join(g['items'])}"
        for g in resume["skills"]
    )

    template = env.get_template("README.md.j2")
    output = template.render(
        info=resume["personalInfo"],
        github=resume["githubUsername"],
        links=build_links(resume["links"]),
        skills=resume["skills"],
        skills_block=skills_block,
        experience=resume["experience"],
        education=resume["education"],
        certifications=resume["certifications"],
        projects=resume["projects"],
    )

    out_path.write_text(output)
    print(f"README.md written to {out_path}")


if __name__ == "__main__":
    main()
