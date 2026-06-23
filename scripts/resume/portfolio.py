"""Fetch a deterministic GitHub portfolio snapshot from topic-tagged repos."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from .core import ROOT

CONFIG = ROOT / "data" / "portfolio-config.json"
SNAPSHOT = ROOT / "data" / "github-portfolio.json"

QUERY = """
query($search: String!, $first: Int!) {
  search(type: REPOSITORY, query: $search, first: $first) {
    nodes {
      ... on Repository {
        name
        nameWithOwner
        owner { login }
        url
        description
        homepageUrl
        openGraphImageUrl
        stargazerCount
        pushedAt
        updatedAt
        isArchived
        isFork
        isPrivate
        primaryLanguage { name }
        repositoryTopics(first: 20) {
          nodes { topic { name } }
        }
      }
    }
  }
}
"""


def load_config(path: Path = CONFIG) -> dict[str, Any]:
    return json.loads(path.read_text())


def repo_from_node(node: dict[str, Any]) -> dict[str, Any]:
    topics = sorted(
        topic["topic"]["name"]
        for topic in node["repositoryTopics"]["nodes"]
    )
    return {
        "name": node["name"],
        "nameWithOwner": node["nameWithOwner"],
        "owner": node["owner"]["login"],
        "url": node["url"],
        "description": node["description"] or "",
        "demo": node["homepageUrl"] or "",
        "thumbnail": f"https://opengraph.githubassets.com/portfolio/{node['nameWithOwner']}",
        "tags": topics,
        "stars": node["stargazerCount"],
        "pushedAt": node["pushedAt"] or "",
        "updatedAt": node["updatedAt"] or "",
        "primaryLanguage": (node["primaryLanguage"] or {}).get("name", ""),
    }


def eligible(node: dict[str, Any], topic: str) -> bool:
    topics = {item["topic"]["name"] for item in node["repositoryTopics"]["nodes"]}
    return (
        topic in topics
        and not node["isArchived"]
        and not node["isFork"]
        and not node["isPrivate"]
    )


def sort_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(projects, key=lambda repo: (repo["stars"], repo["pushedAt"], repo["nameWithOwner"]), reverse=True)


def working_on(projects: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(projects, key=lambda repo: (repo["pushedAt"], repo["nameWithOwner"]), reverse=True)[:limit]


def snapshot(projects: list[dict[str, Any]], topic: str, limit: int, generated_at: str) -> dict[str, Any]:
    ordered = sort_projects(projects)
    return {
        "generatedAt": generated_at,
        "topic": topic,
        "workingOn": working_on(ordered, limit),
        "projects": ordered,
    }


def stable_generated_at(next_data: dict[str, Any], out_path: Path) -> dict[str, Any]:
    if not out_path.exists():
        return next_data
    current = json.loads(out_path.read_text())
    comparable_current = {k: v for k, v in current.items() if k != "generatedAt"}
    comparable_next = {k: v for k, v in next_data.items() if k != "generatedAt"}
    if comparable_current == comparable_next:
        next_data["generatedAt"] = current.get("generatedAt", next_data["generatedAt"])
    return next_data


def search_queries(owner: str, topic: str) -> list[str]:
    base = f"topic:{topic} archived:false fork:false is:public"
    return [f"{base} user:{owner}", f"{base} org:{owner}"]


def fetch_projects(config: dict[str, Any], token: str) -> list[dict[str, Any]]:
    headers = {
        "accept": "application/vnd.github+json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "user-agent": "carlosferreyra-portfolio",
    }
    topic = config["topic"]
    by_url: dict[str, dict[str, Any]] = {}
    with httpx.Client(headers=headers, timeout=30) as client:
        for owner in config["owners"]:
            for search in search_queries(owner, topic):
                response = client.post(
                    "https://api.github.com/graphql",
                    json={"query": QUERY, "variables": {"search": search, "first": 100}},
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("errors"):
                    raise RuntimeError(payload["errors"])
                for node in payload["data"]["search"]["nodes"]:
                    if node and eligible(node, topic):
                        repo = repo_from_node(node)
                        by_url[repo["url"]] = repo
    return list(by_url.values())


def write_snapshot(out_path: Path = SNAPSHOT) -> Path:
    config = load_config()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("error: GITHUB_TOKEN or GH_TOKEN must be set", file=sys.stderr)
        raise SystemExit(1)
    data = stable_generated_at(
        snapshot(
            fetch_projects(config, token),
            config["topic"],
            int(config.get("workingOnLimit", 2)),
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        ),
        out_path,
    )
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return out_path
