# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "jinja2", "pypdf>=5", "typer>=0.12"]
# ///
"""CLI for building and publishing labeled resume profiles."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer

from resume.checks import check_outputs
from resume.core import (
    ROOT,
    ResumeValidationError,
    load_catalog,
    resolve_profile,
    validate,
)
from resume.pdf import render_pdfs
from resume.readme import render_readme
from resume.rxresume import publish_rxresume

app = typer.Typer(
    help="Build, validate, and publish labeled resume profiles.",
    no_args_is_help=True,
)

Profile = Annotated[str | None, typer.Option(help="Profile label to use.")]


def validated_catalog() -> dict:
    try:
        catalog = load_catalog()
        validate(catalog)
        return catalog
    except (OSError, json.JSONDecodeError, ResumeValidationError) as error:
        typer.echo(f"resume validation failed:\n{error}", err=True)
        raise typer.Exit(1) from error


def exit_if_failed(status: int) -> None:
    if status:
        raise typer.Exit(status)


@app.command("validate")
def validate_command() -> None:
    """Validate resume.json and profile labels."""
    validated_catalog()
    typer.echo("resume.json is valid")


@app.command("list")
def list_profiles() -> None:
    """List profile labels, slugs, and targets."""
    catalog = validated_catalog()
    for label, profile in catalog["profiles"].items():
        typer.echo(f"{label:16} slug={profile['slug']:18} targets={','.join(profile['targets'])}")


@app.command()
def resolve(
    profile: Annotated[str, typer.Option(help="Profile label to resolve.")] = "default",
) -> None:
    """Print one resolved profile as JSON."""
    catalog = validated_catalog()
    typer.echo(json.dumps(resolve_profile(catalog, profile), indent=2, ensure_ascii=False))


@app.command("readme")
def readme_command(
    profile: Annotated[str, typer.Option(help="Profile label to render.")] = "default",
    out: Annotated[str, typer.Option(help="Output path relative to the repo root.")] = "README.md",
) -> None:
    """Render README.md from a resolved profile."""
    validated_catalog()
    typer.echo(f"README written to {render_readme(profile, ROOT / out)}")


@app.command()
def pdf(
    profile: Annotated[
        str | None,
        typer.Option(help="Render only this profile. Defaults to all PDF target profiles."),
    ] = None,
    out_dir: Annotated[
        str,
        typer.Option(help="Output directory relative to the repo root."),
    ] = "resume",
) -> None:
    """Render PDF profiles with Typst."""
    validated_catalog()
    exit_if_failed(render_pdfs(profile, out_dir))


@app.command()
def rxresume(
    profile: Annotated[
        str | None,
        typer.Option(help="Publish only this profile. Defaults to all RxResume target profiles."),
    ] = None,
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write changes. Without this flag the command is a dry-run."),
    ] = False,
    theme: Annotated[
        str | None,
        typer.Option(help="Override the profile theme from data/themes.json."),
    ] = None,
) -> None:
    """Publish resolved profiles to RxResume."""
    validated_catalog()
    exit_if_failed(publish_rxresume(profile, apply, theme))


@app.command()
def build(profile: Profile = None) -> None:
    """Build generated README and PDF outputs."""
    catalog = validated_catalog()
    readme_profile = profile or "default"
    if not profile or "readme" in catalog["profiles"][profile]["targets"]:
        render_readme(readme_profile)
    if not profile or "pdf" in catalog["profiles"][profile]["targets"]:
        exit_if_failed(render_pdfs(profile))


@app.command()
def check() -> None:
    """Verify generated outputs and website build are current."""
    validated_catalog()
    exit_if_failed(check_outputs())


if __name__ == "__main__":
    app()
