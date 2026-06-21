"""Load, validate, and resolve labeled profiles from the canonical resume.json."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "resume.json"
SECTIONS = ("links", "skills", "experience", "education", "certifications", "projects")
NESTED = ("experience", "education")
TARGETS = {"website", "readme", "pdf", "rxresume", "business-card"}


class ResumeValidationError(ValueError):
    pass


def load_catalog(path: Path = RESUME) -> dict:
    return json.loads(path.read_text())


def validate(catalog: dict) -> None:
    errors: list[str] = []
    profiles = catalog.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        errors.append("profiles must be a non-empty object")
        profiles = {}
    if "default" not in profiles:
        errors.append("profiles.default is required")

    slugs: set[str] = set()
    for label, profile in profiles.items():
        if not isinstance(profile, dict):
            errors.append(f"profiles.{label} must be an object")
            continue
        for field in ("slug", "title", "summary", "targets"):
            if field not in profile:
                errors.append(f"profiles.{label}.{field} is required")
        slug = profile.get("slug")
        if slug in slugs:
            errors.append(f"duplicate profile slug: {slug}")
        if isinstance(slug, str):
            slugs.add(slug)
        targets = profile.get("targets", [])
        if not isinstance(targets, list) or any(t not in TARGETS for t in targets):
            errors.append(f"profiles.{label}.targets contains an invalid target")

    declared = set(profiles)
    for section in SECTIONS:
        items = catalog.get(section, [])
        if not isinstance(items, list):
            errors.append(f"{section} must be an array")
            continue
        for index, item in enumerate(items):
            _validate_labels(item, f"{section}[{index}]", declared, errors)
            if section in NESTED:
                highlights = item.get("highlights", []) if isinstance(item, dict) else []
                if not isinstance(highlights, list):
                    errors.append(f"{section}[{index}].highlights must be an array")
                else:
                    for hi, highlight in enumerate(highlights):
                        _validate_labels(
                            highlight, f"{section}[{index}].highlights[{hi}]", declared, errors
                        )

    info = catalog.get("personalInfo")
    if not isinstance(info, dict) or not all(info.get(k) for k in ("name", "email", "location")):
        errors.append("personalInfo requires name, email, and location")
    if errors:
        raise ResumeValidationError("\n".join(f"- {error}" for error in errors))


def _validate_labels(item: object, path: str, declared: set[str], errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"{path} must be an object")
        return
    labels = item.get("labels")
    if not isinstance(labels, list) or not labels or not all(isinstance(x, str) for x in labels):
        errors.append(f"{path}.labels must be a non-empty string array")
        return
    unknown = set(labels) - declared
    if unknown:
        errors.append(f"{path}.labels references undeclared profiles: {', '.join(sorted(unknown))}")


def resolve_profile(catalog: dict, label: str = "default") -> dict:
    validate(catalog)
    if label not in catalog["profiles"]:
        raise ResumeValidationError(f"unknown profile: {label}")
    profile = catalog["profiles"][label]
    result = {
        "profile": label,
        "slug": profile["slug"],
        "theme": profile.get("theme", "default"),
        "targets": copy.deepcopy(profile["targets"]),
        "personalInfo": {
            **copy.deepcopy(catalog["personalInfo"]),
            **copy.deepcopy(profile.get("personalInfo", {})),
            "title": profile["title"],
            "summary": profile["summary"],
        },
        "summary": profile["summary"],
        "githubUsername": catalog.get("githubUsername", ""),
    }
    for section in SECTIONS:
        resolved = []
        for source in catalog.get(section, []):
            if label not in source["labels"]:
                continue
            item = {k: copy.deepcopy(v) for k, v in source.items() if k != "labels"}
            if section in NESTED:
                item["highlights"] = [
                    h["text"] for h in source.get("highlights", []) if label in h["labels"]
                ]
            resolved.append(item)
        result[section] = resolved
    return result


def profiles_for_target(catalog: dict, target: str) -> list[str]:
    return [label for label, profile in catalog["profiles"].items() if target in profile["targets"]]
