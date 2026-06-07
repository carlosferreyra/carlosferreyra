# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve baseline + per-stack overrides + combos into data/resumes.json.

Source of truth (edited by hand, committed to git):
  data/baseline.json          common core
  data/stacks/<stack>.json     deltas — keys here OVERRIDE baseline:
                                 scalar/list -> replace, dict -> deep-merge,
                                 null -> hide that section, absent -> inherit
  data/<combo>.json            a combo: { "extends": [stacks], "slug": ... , ...overrides }
                                 list sections are UNIONed (deduped) across the
                                 extended stacks; scalar overrides applied on top

Output (generated, do not edit): data/resumes.json — consumed by the site,
business-card, and the RxResume push.

Run: uv run scripts/resume_build.py
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
STACKS_DIR = DATA / "stacks"
OUT = DATA / "resumes.json"

LIST_SECTIONS = ["links", "skills", "experience", "education", "certifications", "projects"]
IDENTITY = {
    "links": lambda x: x.get("id") or x.get("url"),
    "skills": lambda x: x.get("category"),
    "experience": lambda x: (x.get("company"), x.get("title")),
    "education": lambda x: (x.get("institution"), x.get("degree")),
    "certifications": lambda x: x.get("name"),
    "projects": lambda x: x.get("name"),
}
CONTROL = {"extends", "slug"}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def deep_override(base: dict, override: dict) -> dict:
    """base with override applied: null deletes, dict merges, else replaces."""
    out = copy.deepcopy(base)
    for key, val in override.items():
        if key in CONTROL:
            continue
        if val is None:
            out.pop(key, None)
        elif isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_override(out[key], val)
        else:
            out[key] = val
    return out


def dedup(section: str, items: list[dict]) -> list[dict]:
    key = IDENTITY.get(section, lambda x: json.dumps(x, sort_keys=True))
    seen, result = set(), []
    for it in items:
        k = key(it)
        if k in seen:
            continue
        seen.add(k)
        result.append(it)
    return result


def resolve_stack(baseline: dict, override: dict) -> dict:
    return deep_override(baseline, override)


def resolve_combo(baseline: dict, stacks: dict[str, dict], combo: dict) -> dict:
    resolved = [resolve_stack(baseline, stacks[name]) for name in combo["extends"]]
    out = copy.deepcopy(baseline)
    for section in LIST_SECTIONS:
        merged = [it for r in resolved for it in r.get(section, [])]
        out[section] = dedup(section, merged)
    return deep_override(out, combo)


def main() -> int:
    baseline = load(DATA / "baseline.json")
    stacks = {p.stem: load(p) for p in sorted(STACKS_DIR.glob("*.json"))}
    combos = {
        p.stem: load(p)
        for p in sorted(DATA.glob("*.json"))
        if p.stem not in {"baseline", "resumes", "resume"}
        and "extends" in load(p)
    }

    resumes = []
    for name, override in stacks.items():
        resumes.append({"slug": name, "kind": "stack", **resolve_stack(baseline, override)})
    for name, combo in combos.items():
        resolved = resolve_combo(baseline, stacks, combo)
        resumes.append({"slug": combo.get("slug", name), "kind": "combo", **resolved})

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "data/baseline.json + data/stacks + combos",
        "count": len(resumes),
        "resumes": resumes,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    slugs = ", ".join(f"{r['slug']}({r['kind']})" for r in resumes)
    print(f"wrote {OUT.relative_to(Path.cwd())} — {len(resumes)} resumes: {slugs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
