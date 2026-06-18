# `web/src/lib/`

The portfolio data layer imports the generated `data/resumes.json` contract and selects the public
`carlos-ferreyra` resume. Components import that resolved entry through `resume.ts`.

```text
baseline + stacks + combos
        |
        | scripts/resume_build.py
        v
data/resumes.json -> web/src/lib/resume.ts -> components/sections/*.astro
```

## Rules

- Do not edit `data/resumes.json`; edit `data/baseline.json`, a stack, or a combo.
- Keep the public slug check in `resume.ts` so a missing public resume fails the Astro build.
- Add reusable ordering or selection logic here instead of duplicating it across components.
- Run `uv run scripts/resume_build.py` before `bun run build` after source-data changes.

## Current Mapping

The site renders identity, links, skills, experience, education, certifications, and projects from
the selected resolved resume. `About.astro` currently displays only the first education entry.

`linkById(id)` resolves links by their stable ID. The `Resume` type is inferred from an entry in the
generated array, while the exported `resume` object supplies the component-facing shape.

## Adding Data

1. Add shared fields to `data/baseline.json`, or role-specific fields to a stack/combo.
2. Run `uv run scripts/resume_build.py`.
3. Update `resume.ts` only if the component-facing TypeScript shape needs a new field.
4. Update the relevant Astro components and translations.
5. Run `bun run build`.
