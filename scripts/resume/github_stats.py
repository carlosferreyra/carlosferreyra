"""Fetch GitHub profile data and render static README statistics cards."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

from .core import ROOT, load_catalog, resolve_profile

API = "https://api.github.com"
GRAPHQL = f"{API}/graphql"
SNAPSHOT = ROOT / "data" / "github-stats.json"
ASSETS = ROOT / "assets"

CONTRIBUTIONS_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
            weekday
          }
        }
      }
    }
  }
}
"""

LEVEL_COLORS = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}
LANGUAGE_COLORS = ("#58a6ff", "#a371f7", "#f778ba", "#f2cc60", "#3fb950")


def api_headers(token: str) -> dict[str, str]:
    return {
        "accept": "application/vnd.github+json",
        "authorization": f"Bearer {token}",
        "user-agent": "carlosferreyra-profile-stats",
    }


def fetch_profile(client: httpx.Client, username: str) -> dict[str, Any]:
    response = client.get(f"{API}/users/{username}")
    response.raise_for_status()
    return response.json()


def fetch_repositories(client: httpx.Client, username: str) -> list[dict[str, Any]]:
    url: str | None = f"{API}/users/{username}/repos"
    params: dict[str, Any] | None = {
        "type": "owner",
        "sort": "updated",
        "direction": "desc",
        "per_page": 100,
    }
    repositories: list[dict[str, Any]] = []
    while url:
        response = client.get(url, params=params)
        response.raise_for_status()
        repositories.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return repositories


def fetch_language_bytes(
    client: httpx.Client, repositories: list[dict[str, Any]]
) -> dict[str, int]:
    languages: Counter[str] = Counter()
    for repository in repositories:
        if repository["fork"]:
            continue
        response = client.get(repository["languages_url"])
        response.raise_for_status()
        languages.update(response.json())
    return dict(languages)


def fetch_calendar(client: httpx.Client, username: str) -> dict[str, Any]:
    response = client.post(
        GRAPHQL,
        json={"query": CONTRIBUTIONS_QUERY, "variables": {"login": username}},
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    if calendar is None:
        raise RuntimeError(f"GitHub returned no contribution calendar for {username}")
    return calendar


def build_snapshot(
    username: str,
    profile: dict[str, Any],
    repositories: list[dict[str, Any]],
    language_bytes: dict[str, int],
    calendar: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    source_repositories = [repository for repository in repositories if not repository["fork"]]
    total_bytes = sum(language_bytes.values())
    languages = [
        {
            "name": name,
            "bytes": size,
            "percentage": round(size / total_bytes * 100, 1) if total_bytes else 0,
        }
        for name, size in sorted(language_bytes.items(), key=lambda item: (-item[1], item[0]))[:5]
    ]
    return {
        "generatedAt": generated_at,
        "username": username,
        "summary": {
            "publicRepositories": profile["public_repos"],
            "followers": profile["followers"],
            "following": profile["following"],
            "totalStars": sum(repository["stargazers_count"] for repository in source_repositories),
            "publicContributions": calendar["totalContributions"],
        },
        "languages": languages,
        "contributionCalendar": {"weeks": calendar["weeks"]},
    }


def stable_generated_at(next_data: dict[str, Any], out_path: Path) -> dict[str, Any]:
    if not out_path.exists():
        return next_data
    current = json.loads(out_path.read_text())
    current_without_timestamp = {key: value for key, value in current.items() if key != "generatedAt"}
    next_without_timestamp = {key: value for key, value in next_data.items() if key != "generatedAt"}
    if current_without_timestamp == next_without_timestamp:
        next_data["generatedAt"] = current.get("generatedAt", next_data["generatedAt"])
    return next_data


def svg_document(width: int, height: int, title: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
  <title id="title">{escape(title)}</title>
  <rect width="100%" height="100%" rx="10" fill="#0d1117"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="9.5" fill="none" stroke="#30363d"/>
  {body}
</svg>
'''


def stats_svg(data: dict[str, Any]) -> str:
    summary = data["summary"]
    metrics = (
        ("Public repos", summary["publicRepositories"]),
        ("Followers", summary["followers"]),
        ("Total stars", summary["totalStars"]),
        ("Public contributions (1y)", summary["publicContributions"]),
    )
    positions = ((24, 80), (260, 80), (24, 140), (260, 140))
    rows = []
    for (label, value), (x, y) in zip(metrics, positions, strict=True):
        rows.append(
            f'<text x="{x}" y="{y - 18}" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="13">{escape(label)}</text>'
        )
        rows.append(
            f'<text x="{x}" y="{y + 6}" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="22" font-weight="600">{value:,}</text>'
        )
    title = f"@{data['username']} GitHub stats"
    body = "\n  ".join(
        [
            f'<text x="24" y="34" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="18" font-weight="600">{escape(title)}</text>',
            *rows,
            f'<text x="24" y="178" fill="#6e7681" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="11">Updated {escape(data["generatedAt"][:10])} UTC</text>',
        ]
    )
    return svg_document(495, 195, title, body)


def languages_svg(data: dict[str, Any]) -> str:
    title = "Top Languages"
    rows = [
        f'<text x="24" y="34" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="18" font-weight="600">{title}</text>'
    ]
    if not data["languages"]:
        rows.append(
            '<text x="24" y="80" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="14">No public source files yet</text>'
        )
    for index, language in enumerate(data["languages"]):
        y = 64 + index * 25
        color = LANGUAGE_COLORS[index % len(LANGUAGE_COLORS)]
        name = escape(language["name"])
        percentage = language["percentage"]
        rows.extend(
            [
                f'<text x="24" y="{y}" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="13">{name}</text>',
                f'<rect x="150" y="{y - 10}" width="280" height="8" rx="4" fill="#21262d"/>',
                f'<rect x="150" y="{y - 10}" width="{max(3, round(280 * percentage / 100))}" height="8" rx="4" fill="{color}"/>',
                f'<text x="465" y="{y}" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="12">{percentage:.1f}%</text>',
            ]
        )
    return svg_document(495, 195, title, "\n  ".join(rows))


def activity_svg(data: dict[str, Any]) -> str:
    weeks = data["contributionCalendar"]["weeks"][-53:]
    width = 760
    cell = 10
    gap = 3
    graph_x = 24
    graph_y = 60
    cells = []
    for week_index, week in enumerate(weeks):
        x = graph_x + week_index * (cell + gap)
        for day in week["contributionDays"]:
            y = graph_y + day["weekday"] * (cell + gap)
            color = LEVEL_COLORS.get(day["contributionLevel"], LEVEL_COLORS["NONE"])
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}"><title>{escape(day["date"])}: {day["contributionCount"]} contributions</title></rect>'
            )
    count = data["summary"]["publicContributions"]
    title = "Contribution Activity"
    body = "\n  ".join(
        [
            f'<text x="24" y="34" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="18" font-weight="600">{title}</text>',
            f'<text x="736" y="34" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="13">{count:,} public contributions in the last year</text>',
            *cells,
        ]
    )
    return svg_document(width, 165, title, body)


def render_assets(data: dict[str, Any], assets_dir: Path = ASSETS) -> list[Path]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        assets_dir / "github-stats.svg": stats_svg(data),
        assets_dir / "github-languages.svg": languages_svg(data),
        assets_dir / "github-activity.svg": activity_svg(data),
    }
    for path, content in paths.items():
        path.write_text(content)
    return list(paths)


def write_stats(out_path: Path = SNAPSHOT, assets_dir: Path = ASSETS) -> list[Path]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("error: GITHUB_TOKEN or GH_TOKEN must be set", file=sys.stderr)
        raise SystemExit(1)

    username = resolve_profile(load_catalog())["githubUsername"]
    with httpx.Client(headers=api_headers(token), follow_redirects=True, timeout=30) as client:
        profile = fetch_profile(client, username)
        repositories = fetch_repositories(client, username)
        language_bytes = fetch_language_bytes(client, repositories)
        calendar = fetch_calendar(client, username)
    data = stable_generated_at(
        build_snapshot(
            username,
            profile,
            repositories,
            language_bytes,
            calendar,
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        ),
        out_path,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return [out_path, *render_assets(data, assets_dir)]


def load_stats(path: Path = SNAPSHOT) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())
