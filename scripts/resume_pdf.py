# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate configured PDF profiles from the canonical resume.json."""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

from resume_core import ROOT, load_catalog, profiles_for_target, resolve_profile

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
    parser = argparse.ArgumentParser(description="Render PDF profiles from resume.json.")
    parser.add_argument("--profile", help="Render only this profile (default: PDF targets)")
    parser.add_argument("--out-dir", default="resume", help="Output directory relative to repo root")
    args = parser.parse_args()
    catalog = load_catalog()
    if args.profile and "pdf" not in catalog["profiles"].get(args.profile, {}).get("targets", []):
        print(f"error: profile '{args.profile}' does not target pdf", file=sys.stderr)
        return 1
    labels = [args.profile] if args.profile else profiles_for_target(catalog, "pdf")
    resumes = [resolve_profile(catalog, label) for label in labels]

    # render cv.typ once (only the version import is templated; slug is a runtime input)
    CV_TYP.write_text(TEMPLATE.read_text().replace("{{ version }}", silver_dev_version()))

    person = slugify(resumes[0]["personalInfo"]["name"])
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    failed = []
    with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
        for r in resumes:
            data = Path(temp_dir) / f"{r['slug']}.json"
            data.write_text(json.dumps(r, ensure_ascii=False))
            out = out_dir / pdf_name(person, r["slug"])
            cmd = [
                "typst", "compile", "--root", str(ROOT),
                "--input", f"data={data.relative_to(ROOT)}", str(CV_TYP), str(out),
            ]
            print(f"  [{r['profile']:18}] -> {out.relative_to(ROOT)} ...", end=" ", flush=True)
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"OK ({out.stat().st_size // 1024}KB)")
            else:
                print("FAILED")
                print(res.stderr.strip(), file=sys.stderr)
                failed.append(r["profile"])

    if failed:
        print(f"\nfailed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\nbuilt {len(resumes)} PDF(s) in {out_dir.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
