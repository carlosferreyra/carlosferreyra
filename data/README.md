# Resume Data Reference

The hand-edited source is split into a shared baseline, stack overrides, and combo definitions.
`scripts/resume_build.py` resolves them into `data/resumes.json`, the generated contract consumed
by the README, PDFs, RxResume, and portfolio.

## Files

```text
data/
├── baseline.json       shared fields inherited by every resume
├── stacks/
│   ├── backend.json    stack-specific override
│   ├── cli.json
│   ├── devops.json
│   └── fullstack.json
├── dev.json            combo extending backend + fullstack
├── themes.json         RxResume presentation configuration
└── resumes.json        generated output; do not edit
```

## Merge Rules

Stack files are applied over `baseline.json`:

- scalar and list values replace the baseline value
- dictionaries deep-merge
- `null` removes a section
- absent keys inherit from the baseline

Combo files contain `extends`, optionally set a public `slug`, and may override any resolved field.
List sections from extended stacks are unioned and deduplicated before combo overrides are applied.

Example stack:

```json
{
  "personalInfo": {
    "title": "Backend Engineer"
  },
  "skills": [
    {
      "category": "Backend",
      "items": ["Python", "Django"]
    }
  ]
}
```

Example combo:

```json
{
  "extends": ["fullstack", "backend"],
  "slug": "carlos-ferreyra",
  "personalInfo": {
    "title": "Software Engineer"
  }
}
```

## Common Operations

Build all resolved resumes:

```bash
uv run scripts/resume_build.py
```

List slugs and generated PDF/RxResume destinations without writing output:

```bash
uv run scripts/resume_build.py --list
```

Create a stack:

1. Add `data/stacks/<slug>.json`.
2. Include only fields that differ from `baseline.json`.
3. Run the build and inspect the new resolved entry.

Create a combo:

1. Add `data/<name>.json` with an `extends` array.
2. Set `slug` when the public slug should differ from the filename.
3. Add only combo-specific overrides.
4. Run the build and inspect the resolved entry.

Update shared data in `baseline.json`; update role-specific data in its stack or combo. Removing a
stack/combo removes it from the next generated `resumes.json`, but remote RxResume pruning is not
currently automatic.

## Full Local Verification

```bash
uv run scripts/resume_build.py
uv run scripts/build_readme.py
uv run scripts/resume_pdf.py
cd web && bun run build
```

Use `uv run scripts/resume_push.py` for an RxResume dry-run. Add `--apply` only when the printed
changes are correct.
