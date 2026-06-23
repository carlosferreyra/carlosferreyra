"""Checks for generated resume outputs."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader

from .core import ROOT
from .pdf import render_pdfs
from .readme import render_readme


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def check_outputs() -> int:
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        temp_path = Path(temp)
        readme = temp_path / "README.md"
        render_readme(out_path=readme)
        if readme.read_bytes() != (ROOT / "README.md").read_bytes():
            print("README.md is stale; run: uv run scripts/resume readme", file=sys.stderr)
            return 1

        pdf_dir = temp_path / "pdf"
        result = render_pdfs(out_dir_name=str(pdf_dir.relative_to(ROOT)))
        if result:
            return result
        for generated in pdf_dir.glob("*.pdf"):
            committed = ROOT / "resume" / generated.name
            if not committed.exists() or pdf_text(generated) != pdf_text(committed):
                print(f"{committed.relative_to(ROOT)} is stale", file=sys.stderr)
                return 1

    subprocess.run(["bun", "run", "build"], cwd=ROOT / "web", check=True)
    print("generated outputs and website are current")
    return 0
