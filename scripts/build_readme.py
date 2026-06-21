# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2"]
# ///
"""Render README.md from a labeled profile in the canonical resume.json."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from resume_core import ROOT, load_catalog, resolve_profile


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_readme(profile: str = "default", out_path: Path | None = None) -> Path:
    resume = resolve_profile(load_catalog(), profile)
    out_path = out_path or ROOT / "README.md"
    env = Environment(
        loader=FileSystemLoader(str(ROOT)), undefined=StrictUndefined,
        keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True,
    )
    env.filters["slugify"] = slugify
    skills_block = "\n".join(
        f"{(group['category'] + ':'):<24} {', '.join(group['items'])}"
        for group in resume["skills"]
    )
    output = env.get_template("README.md.j2").render(
        info=resume["personalInfo"], github=resume["githubUsername"],
        links={link["id"]: link["url"] for link in resume["links"]},
        skills=resume["skills"], skills_block=skills_block,
        experience=resume["experience"], education=resume["education"],
        certifications=resume["certifications"], projects=resume["projects"],
        last_update=datetime.now(timezone.utc).strftime("%Y"),
    )
    out_path.write_text(output)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="default")
    parser.add_argument("--out", default="README.md")
    args = parser.parse_args()
    print(f"README written to {render_readme(args.profile, ROOT / args.out)}")


if __name__ == "__main__":
    main()
