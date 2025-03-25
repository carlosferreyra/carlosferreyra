#!/usr/bin/env python3
"""Main entry point for the carlosferreyra package.

This module provides the main entry point for the command line interface
of the carlosferreyra package. It implements an interactive menu to access
various profile links.
"""
import webbrowser
import typer
import sys

app = typer.Typer(
    help="CLI tool to access Carlos Ferreyra's professional profiles and portfolio"
)

GITHUB_URL = "https://github.com/carlosferreyra"
LINKEDIN_URL = "https://www.linkedin.com/in/eduferreyraok/"
WEBSITE_URL = "https://carlosferreyra.me"

def open_url(url: str) -> None:
    """Open a URL in the default web browser."""
    webbrowser.open(url)

@app.callback(invoke_without_command=True)
def main() -> None:
    """Interactive menu to access various profile links."""


    choices = {
        "1": ("Open GitHub Profile", GITHUB_URL),
        "2": ("Open LinkedIn Profile", LINKEDIN_URL),
        "3": ("Open Website", WEBSITE_URL),
        "q": ("Quit", None),
    }

    while True:
        typer.clear()
        typer.secho("Carlos Ferreyra - Professional Profiles", fg=typer.colors.CYAN, bold=True)
        typer.echo("\nSelect an option:")

        for key, (label, _) in choices.items():
            typer.echo(f"{key}) {label}")

        choice = typer.prompt("\nYour choice", type=str, default="q").lower()

        if choice == "q":
            typer.echo("Goodbye!")
            sys.exit(0)

        if choice in choices:
            _, url = choices[choice]
            if url:
                open_url(url)
        else:
            typer.secho("Invalid option!", fg=typer.colors.RED)
            typer.echo("Press Enter to continue...")
            input()

if __name__ == "__main__":
    app()
