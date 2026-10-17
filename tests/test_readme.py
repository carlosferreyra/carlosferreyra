from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from resume.core import load_catalog
from resume.readme import render_readme


class ReadmeTests(unittest.TestCase):
    def test_json_metadata_controls_copy_resume_links_and_display_limits(self) -> None:
        catalog = load_catalog()
        catalog["readme"].update(
            tagline=["Custom focus"], summary="Custom introduction.",
            availability="Custom availability.", contactLabel="Contact me",
            featuredProjectLimit=1, experienceHighlightLimit=1,
            resumeProfiles=[{"profile": "backend", "label": "Backend résumé"}],
        )
        catalog["profiles"]["backend"]["slug"] = "backend-review"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "README.md"
            with patch("resume.readme.load_catalog", return_value=catalog):
                render_readme(out_path=output)
            text = output.read_text()
        for expected in (
            "Custom focus", "Custom introduction.", "Custom availability.",
            "[Contact me]", "[Backend résumé](resume/carlos-ferreyra-backend-review.pdf)",
        ):
            self.assertIn(expected, text)
        self.assertEqual(text.count("\n### ["), 1)
        self.assertNotIn("Mapped manual processes", text)
        self.assertNotIn("Backend services · Developer tools · Automation", text)


if __name__ == "__main__":
    unittest.main()
