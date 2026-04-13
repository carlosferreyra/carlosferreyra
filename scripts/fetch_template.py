# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Fetches the latest version of the silver-dev-cv Typst template.

Usage:
    uv run scripts/fetch_template.py
    uv run scripts/fetch_template.py --package silver-dev-cv --out silver-dev-cv/template
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch latest Typst Universe package.")
    parser.add_argument("--package", default="silver-dev-cv", help="Package name on Typst Universe")
    parser.add_argument("--out", default="silver-dev-cv/template", help="Output directory (relative to repo root)")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    out_dir = repo_root / args.out
    import shutil
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    package_ref = f"@preview/{args.package}"
    print(f"Fetching {package_ref} into {out_dir}...")

    result = subprocess.run(
        ["typst", "init", package_ref, str(out_dir)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()
