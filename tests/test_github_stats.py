from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from resume.github_stats import activity_svg, build_snapshot, languages_svg, stable_generated_at, stats_svg


def calendar() -> dict:
    return {
        "totalContributions": 27,
        "weeks": [
            {
                "contributionDays": [
                    {
                        "contributionCount": 3,
                        "contributionLevel": "SECOND_QUARTILE",
                        "date": "2026-01-01",
                        "weekday": 4,
                    }
                ]
            }
        ],
    }


class GitHubStatsTests(unittest.TestCase):
    def test_snapshot_uses_public_repositories_and_excludes_forks_from_stars(self) -> None:
        data = build_snapshot(
            "octocat",
            {"public_repos": 4, "followers": 8, "following": 2},
            [
                {"fork": False, "stargazers_count": 5},
                {"fork": True, "stargazers_count": 99},
            ],
            {"Rust": 80, "Python": 20},
            calendar(),
            "2026-01-01T00:00:00Z",
        )

        self.assertEqual(data["summary"]["publicRepositories"], 4)
        self.assertEqual(data["summary"]["totalStars"], 5)
        self.assertEqual(data["summary"]["publicContributions"], 27)
        self.assertEqual(data["languages"][0], {"name": "Rust", "bytes": 80, "percentage": 80.0})

    def test_cards_render_the_snapshot_without_external_urls(self) -> None:
        data = build_snapshot(
            "octocat",
            {"public_repos": 4, "followers": 8, "following": 2},
            [{"fork": False, "stargazers_count": 5}],
            {"Rust": 80},
            calendar(),
            "2026-01-01T00:00:00Z",
        )

        self.assertIn("@octocat GitHub stats", stats_svg(data))
        self.assertIn("Rust", languages_svg(data))
        self.assertIn("2026-01-01: 3 contributions", activity_svg(data))

    def test_stable_generated_at_is_preserved_when_content_is_unchanged(self) -> None:
        current = {"generatedAt": "2026-01-01T00:00:00Z", "summary": {"followers": 1}}
        next_data = {"generatedAt": "2026-06-01T00:00:00Z", "summary": {"followers": 1}}

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "github-stats.json"
            path.write_text(json.dumps(current))
            stable = stable_generated_at(next_data, path)

        self.assertEqual(stable["generatedAt"], "2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
