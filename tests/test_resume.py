from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from resume_core import ResumeValidationError, load_catalog, profiles_for_target, resolve_profile, validate


class ResumeCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_catalog()

    def test_catalog_and_every_profile_validate_and_resolve(self) -> None:
        validate(self.catalog)
        for label in self.catalog["profiles"]:
            self.assertEqual(resolve_profile(self.catalog, label)["profile"], label)

    def test_exact_selection_does_not_inherit_default(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["projects"].append(
            {"name": "Default only", "description": "", "labels": ["default"]}
        )
        names = [project["name"] for project in resolve_profile(catalog, "backend")["projects"]]
        self.assertNotIn("Default only", names)

    def test_shared_entry_is_returned_once(self) -> None:
        projects = resolve_profile(self.catalog, "backend")["projects"]
        self.assertEqual([p["name"] for p in projects].count("Personal Website"), 1)

    def test_nested_highlights_are_filtered_independently(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["experience"][0]["highlights"].append(
            {"text": "Default-only detail", "labels": ["default"]}
        )
        backend = resolve_profile(catalog, "backend")
        self.assertNotIn("Default-only detail", backend["experience"][0]["highlights"])

    def test_sparse_profile_is_valid(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"]["sparse"] = {
            "slug": "sparse", "title": "Sparse", "summary": "", "targets": []
        }
        validate(catalog)
        self.assertFalse(resolve_profile(catalog, "sparse")["experience"])

    def test_rejects_missing_empty_and_unknown_labels(self) -> None:
        for labels in (None, [], ["missing-profile"]):
            with self.subTest(labels=labels):
                catalog = copy.deepcopy(self.catalog)
                if labels is None:
                    catalog["projects"][0].pop("labels")
                else:
                    catalog["projects"][0]["labels"] = labels
                with self.assertRaises(ResumeValidationError):
                    validate(catalog)

    def test_rejects_duplicate_slugs_and_invalid_targets(self) -> None:
        duplicate = copy.deepcopy(self.catalog)
        duplicate["profiles"]["backend"]["slug"] = duplicate["profiles"]["default"]["slug"]
        with self.assertRaises(ResumeValidationError):
            validate(duplicate)
        invalid = copy.deepcopy(self.catalog)
        invalid["profiles"]["default"]["targets"].append("printer")
        with self.assertRaises(ResumeValidationError):
            validate(invalid)

    def test_target_selection(self) -> None:
        self.assertNotIn("business-card", profiles_for_target(self.catalog, "pdf"))
        self.assertEqual(profiles_for_target(self.catalog, "business-card"), ["business-card"])

    def test_profile_personal_info_overrides_shared_identity(self) -> None:
        hospitality = resolve_profile(self.catalog, "hospitality")
        self.assertEqual(hospitality["personalInfo"]["location"], "USA")
        self.assertEqual(hospitality["personalInfo"]["phone"], "+1 (970) 710 1675")


if __name__ == "__main__":
    unittest.main()
