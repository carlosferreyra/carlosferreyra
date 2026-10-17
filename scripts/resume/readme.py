"""Render README.md from a labeled profile in the canonical resume.json."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .core import ROOT, load_catalog, resolve_profile
from .github_stats import load_stats
from .pdf import pdf_name

PORTFOLIO = ROOT / "data" / "github-portfolio.json"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_portfolio(path: Path = PORTFOLIO) -> dict:
    if not path.exists():
        return {"workingOn": [], "projects": []}
    return json.loads(path.read_text())


def working_on_markdown(repos: list[dict]) -> str:
    if not repos:
        return ""
    links = " & ".join(f"[{repo['name']}]({repo['url']})" for repo in repos)
    return f"- 🔭 Working on: {links}"


def projects_markdown(projects: list[dict]) -> str:
    lines = []
    for project in projects:
        stars = f" · ⭐ {project['stars']}" if "stars" in project else ""
        lines.append(f"- [{project['name']}]({project['url']}) - {project['description']}{stars}")
    return "\n".join(lines)


def render_readme(profile: str = "default", out_path: Path | None = None) -> Path:
    catalog = load_catalog()
    resume = resolve_profile(catalog, profile)
    readme = catalog["readme"]
    resume_links = [
        {"label": item["label"], "path": "resume/" + pdf_name(
            slugify(resume["personalInfo"]["name"]),
            resolve_profile(catalog, item["profile"])["slug"],
        )}
        for item in readme["resumeProfiles"]
    ]
    portfolio = load_portfolio()
    github_stats = load_stats()
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
        certifications=resume["certifications"],
        projects_markdown=projects_markdown(portfolio["projects"]),
        working_on_markdown=working_on_markdown(portfolio["workingOn"]),
        projects=portfolio["projects"],
        readme=readme, resume_links=resume_links,
        github_stats=github_stats,
        last_updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    out_path.write_text(output)
    return out_path
