from __future__ import annotations

import sys
import unittest
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from resume.portfolio import eligible, snapshot, stable_generated_at


def repo(
    name: str,
    *,
    stars: int = 0,
    pushed_at: str = "2024-01-01T00:00:00Z",
    topics: list[str] | None = None,
    archived: bool = False,
    fork: bool = False,
    private: bool = False,
) -> dict:
    return {
        "name": name,
        "nameWithOwner": f"owner/{name}",
        "owner": "owner",
        "url": f"https://github.com/owner/{name}",
        "description": "",
        "demo": "",
        "thumbnail": "",
        "tags": sorted(topics or ["portfolio"]),
        "stars": stars,
        "pushedAt": pushed_at,
        "updatedAt": pushed_at,
        "primaryLanguage": "",
    }


def node(
    *,
    topics: list[str] | None = None,
    archived: bool = False,
    fork: bool = False,
    private: bool = False,
) -> dict:
    return {
        "isArchived": archived,
        "isFork": fork,
        "isPrivate": private,
        "repositoryTopics": {
            "nodes": [{"topic": {"name": topic}} for topic in (topics or ["portfolio"])]
        },
    }


class PortfolioSnapshotTests(unittest.TestCase):
    def test_projects_sort_by_stars_then_recent_push(self) -> None:
        data = snapshot(
            [
                repo("recent-low", stars=1, pushed_at="2026-01-01T00:00:00Z"),
                repo("older-high", stars=5, pushed_at="2024-01-01T00:00:00Z"),
                repo("recent-high", stars=5, pushed_at="2025-01-01T00:00:00Z"),
            ],
            "portfolio",
            2,
            "2026-06-23T00:00:00Z",
        )

        self.assertEqual(
            [project["name"] for project in data["projects"]],
            ["recent-high", "older-high", "recent-low"],
        )

    def test_working_on_uses_latest_two_pushes(self) -> None:
        data = snapshot(
            [
                repo("old", pushed_at="2024-01-01T00:00:00Z"),
                repo("newest", pushed_at="2026-01-01T00:00:00Z"),
                repo("middle", pushed_at="2025-01-01T00:00:00Z"),
            ],
            "portfolio",
            2,
            "2026-06-23T00:00:00Z",
        )

        self.assertEqual([project["name"] for project in data["workingOn"]], ["newest", "middle"])

    def test_eligible_rejects_non_portfolio_and_unpublishable_repos(self) -> None:
        self.assertTrue(eligible(node(), "portfolio"))
        self.assertFalse(eligible(node(topics=["other"]), "portfolio"))
        self.assertFalse(eligible(node(archived=True), "portfolio"))
        self.assertFalse(eligible(node(fork=True), "portfolio"))
        self.assertFalse(eligible(node(private=True), "portfolio"))

    def test_stable_generated_at_is_preserved_when_content_is_unchanged(self) -> None:
        current = snapshot([repo("same")], "portfolio", 2, "2026-01-01T00:00:00Z")
        next_data = snapshot([repo("same")], "portfolio", 2, "2026-06-23T00:00:00Z")

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "github-portfolio.json"
            path.write_text(json.dumps(current))

            stable = stable_generated_at(next_data, path)

        self.assertEqual(stable["generatedAt"], "2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
