"""Push labeled profiles from resume.json to Reactive Resume by slug.

Repo is the source of truth; RxResume is a renderer. Each targeted profile is
created (if its slug is new) or updated (if it exists) so
it lives at rxresu.me/<username>/<slug>. An existing resume supplies the
structural template (theme, layout, typography).

Dry-run by default. Pass --apply to write.

Env: RXRESUME_BASE_URL, RXRESUME_TOKEN, RXRESUME_USERNAME
Run: uv run scripts/resume rxresume [--profile backend] [--apply]
"""

from __future__ import annotations

import copy
import json
import os
import secrets
import sys
from pathlib import Path

import httpx

from .core import ROOT, load_catalog, profiles_for_target, resolve_profile

THEMES = ROOT / "data" / "themes.json"
TEMPLATE_SLUG = "carlos-ferreyra"
MANAGED = {"profiles", "experience", "education", "skills", "projects", "certifications"}

# link id -> simple-icons network slug RxResume uses to render brand icons
NETWORK = {"github": "github", "linkedin": "linkedin", "twitter": "x", "leetcode": "leetcode"}


def cuid() -> str:
    return secrets.token_hex(12)


def ul(lines: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in lines) + "</ul>" if lines else ""


def p(text: str) -> str:
    return f"<p>{text}</p>" if text else ""


def link(url: str, label: str = "") -> dict:
    return {"url": url, "label": label, "inlineLink": False}


def build_data(template: dict, r: dict) -> dict:
    data = copy.deepcopy(template)
    pi = r["personalInfo"]
    data["basics"].update(
        name=pi["name"], headline=pi.get("title", ""), email=pi["email"], location=pi["location"]
    )
    if pi.get("phone"):
        data["basics"]["phone"] = pi["phone"]
    data["summary"]["content"] = p(r.get("summary") or pi.get("summary", ""))
    sec = data["sections"]

    sec["profiles"]["items"] = [
        {
            "id": cuid(), "hidden": False, "icon": "", "iconColor": "",
            "network": NETWORK.get(l["id"], l["label"]),
            "username": l["label"], "website": link(l["url"]),
        }
        for l in r.get("links", []) if l["id"] != "email"
    ]
    sec["experience"]["items"] = [
        {
            "id": cuid(), "hidden": False, "company": e["company"], "position": e["title"],
            "location": e.get("location", ""), "period": e["period"],
            "website": link(""), "description": ul(e.get("highlights", [])),
        }
        for e in r.get("experience", [])
    ]
    sec["education"]["items"] = [
        {
            "id": cuid(), "hidden": False, "school": ed["institution"], "degree": ed["degree"],
            "area": "", "grade": "", "location": ed.get("location", ""), "period": ed["period"],
            "website": link(""), "description": ul(ed.get("highlights", [])),
        }
        for ed in r.get("education", [])
    ]
    sec["skills"]["items"] = [
        {
            "id": cuid(), "hidden": False, "icon": "", "iconColor": "", "name": s["category"],
            "proficiency": "", "level": 0, "keywords": s["items"],
        }
        for s in r.get("skills", [])
    ]
    sec["projects"]["items"] = [
        {
            "id": cuid(), "hidden": False, "name": pr["name"], "period": "",
            "website": link(pr.get("url", "")), "description": p(pr.get("description", "")),
        }
        for pr in r.get("projects", [])
    ]
    sec["certifications"]["items"] = [
        {
            "id": cuid(), "hidden": False, "title": c["name"], "issuer": "",
            "date": str(c.get("year", "")), "website": link(c.get("url", "")), "description": "",
        }
        for c in r.get("certifications", [])
    ]
    for name, s in sec.items():
        if name not in MANAGED:
            s["items"] = []
    return data


def apply_theme(data: dict, theme: dict) -> dict:
    """Overlay a repo-owned theme: metadata (layout/colors/typography/page),
    avatar, and per-section chrome (title/icon/columns/hidden). The repo owns
    presentation — rxresu.me is a pure render target."""
    data["metadata"] = copy.deepcopy(theme["metadata"])
    data["picture"] = copy.deepcopy(theme["picture"])
    for key, meta in theme.get("sectionMeta", {}).items():
        if key in data["sections"]:
            data["sections"][key].update(meta)
    return data


def publish_rxresume(profile: str | None = None, apply: bool = False) -> int:
    base = os.environ.get("RXRESUME_BASE_URL", "").rstrip("/")
    token = os.environ.get("RXRESUME_TOKEN", "")
    username = os.environ.get("RXRESUME_USERNAME", "<username>")
    if not base or not token:
        print("error: RXRESUME_BASE_URL and RXRESUME_TOKEN must be set", file=sys.stderr)
        return 1

    catalog = load_catalog()
    if profile and "rxresume" not in catalog["profiles"].get(profile, {}).get("targets", []):
        print(f"error: profile '{profile}' does not target rxresume", file=sys.stderr)
        return 1
    labels = [profile] if profile else profiles_for_target(catalog, "rxresume")
    resumes = [resolve_profile(catalog, label) for label in labels]

    themes = json.loads(THEMES.read_text())
    headers = {"x-api-key": token}

    with httpx.Client(base_url=base, headers=headers, timeout=30) as client:
        listing = client.get("/resumes"); listing.raise_for_status()
        by_slug = {x["slug"]: x for x in listing.json()}
        template = client.get(f"/resumes/{by_slug[TEMPLATE_SLUG]['id']}").json()["data"]

        for r in resumes:
            slug = r["slug"]
            data = build_data(template, r)
            theme = themes[r.get("theme", "default")]
            data = apply_theme(data, theme)
            exists = slug in by_slug
            verb = "UPDATE" if exists else "CREATE"
            counts = {k: len(data["sections"][k]["items"]) for k in MANAGED}
            print(f"[{verb}] slug={slug:18} title='{r['personalInfo']['title']}' {counts}")
            print(f"         -> https://rxresu.me/{username}/{slug}")
            if not apply:
                continue
            if exists:
                rid = by_slug[slug]["id"]
                resp = client.put(f"/resumes/{rid}", json={"data": data})
            else:
                created = client.post(
                    "/resumes",
                    json={"name": r["personalInfo"]["title"], "slug": slug, "tags": [r["profile"]]},
                )
                created.raise_for_status()
                rid = created.json()
                resp = client.put(f"/resumes/{rid}", json={"data": data, "isPublic": True})
            resp.raise_for_status()
            print(f"         -> {verb.lower()}d id={rid}")

    if not apply:
        print("\ndry-run only. re-run with --apply to write to rxresu.me")
    return 0
