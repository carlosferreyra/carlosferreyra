# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate PDF resumes from data/resumes.json via Typst + silver-dev-cv.

Repo is the source of truth: scripts/resume_build.py resolves baseline + stacks
+ combos into data/resumes.json; this script renders one PDF per resume so a
committed PDF lives in resume/ alongside the live rxresu.me versions.

Output naming (matches the existing files):
  combo slug == person slug  -> resume/<person>.pdf
  otherwise                  -> resume/<person>-<slug>.pdf

Run: uv run scripts/resume_pdf.py [--slug backend]
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESUMES = ROOT / "data" / "resumes.json"
TEMPLATE = ROOT / "silver-dev-cv" / "cv.typ.j2"
CV_TYP = ROOT / "silver-dev-cv" / "cv.typ"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def silver_dev_version(package: str = "silver-dev-cv") -> str:
    caches = [
        Path.home() / "Library" / "Caches" / "typst" / "packages" / "preview",
        Path.home() / ".cache" / "typst" / "packages" / "preview",
    ]
    for cache in caches:
        tomls = sorted(glob.glob(str(cache / package / "*" / "typst.toml")))
        if tomls:
            return tomllib.load(open(tomls[-1], "rb"))["package"]["version"]
    return "1.0.2"


def pdf_name(person: str, slug: str) -> str:
    return f"{person}.pdf" if slug == person else f"{person}-{slug}.pdf"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render resume PDFs from resumes.json.")
    parser.add_argument("--slug", help="Render only this resume slug (default: all)")
    args = parser.parse_args()

    if not RESUMES.exists():
        print("error: data/resumes.json missing — run scripts/resume_build.py first", file=sys.stderr)
        return 1

    resumes = json.loads(RESUMES.read_text())["resumes"]
    if args.slug:
        resumes = [r for r in resumes if r["slug"] == args.slug]
        if not resumes:
            print(f"error: slug '{args.slug}' not found in resumes.json", file=sys.stderr)
            return 1

    # render cv.typ once (only the version import is templated; slug is a runtime input)
    CV_TYP.write_text(TEMPLATE.read_text().replace("{{ version }}", silver_dev_version()))

    person = slugify(resumes[0]["personalInfo"]["name"])
    out_dir = ROOT / "resume"
    out_dir.mkdir(exist_ok=True)

    failed = []
    for r in resumes:
        out = out_dir / pdf_name(person, r["slug"])
        cmd = [
            "typst", "compile", "--root", str(ROOT),
            "--input", f"slug={r['slug']}", str(CV_TYP), str(out),
        ]
        print(f"  [{r['slug']:18}] -> resume/{out.name} ...", end=" ", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"OK ({out.stat().st_size // 1024}KB)")
        else:
            print("FAILED")
            print(res.stderr.strip(), file=sys.stderr)
            failed.append(r["slug"])

    if failed:
        print(f"\nfailed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\nbuilt {len(resumes)} PDF(s) in resume/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
