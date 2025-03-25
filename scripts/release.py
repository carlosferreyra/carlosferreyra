#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path
import os

def get_current_version():
    init_file = Path("src/carlosferreyra/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Version not found in __init__.py")
    return match.group(1)

def update_version(new_version):
    init_file = Path("src/carlosferreyra/__init__.py")
    content = init_file.read_text()
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    init_file.write_text(new_content)

def git_commands(version):
    commands = [
        ["git", "add", "src/carlosferreyra/__init__.py"],
        ["git", "commit", "-m", f"chore: bump version to {version}"],
    ]

    # Only create and push tags if not running in GitHub Actions
    if not os.getenv('GITHUB_ACTIONS'):
        commands.extend([
            ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"],
            ["git", "push", "origin", "main"],
            ["git", "push", "origin", f"v{version}"],
        ])

    for cmd in commands:
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./scripts/release.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")

    try:
        update_version(new_version)
        git_commands(new_version)
        print(f"✨ Successfully released version {new_version}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)