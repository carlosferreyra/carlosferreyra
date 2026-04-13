# resume.json — Reference & Cheatsheet

`resume.json` is the single source of truth for all resume content, structure, and variant config.
Nothing else needs to be edited to update or generate a new resume.

---

## Structure overview

```
resume.json
├── personalInfo        — name, title, email, location, summary
├── summaries           — per-variant summary overrides
├── githubUsername
├── links               — all social/contact links (id, label, url)
├── skills              — grouped by category, each with tags
├── experience          — jobs, each with tags and highlights
├── education
├── certifications      — each with tags
├── projects            — each with tags
└── variants            — one entry per PDF output
    ├── name            — used as the tag filter and filename suffix
    ├── label           — human-readable label
    ├── contacts        — ordered list of link IDs for the header
    └── sections        — which sections to include (bool per section)
```

---

## Variant design checklist

Before adding or editing a variant, answer these three questions:

1. **Who is reading this?** Map the variant to one reader profile — DevOps hiring manager, backend
   team lead, data engineering recruiter. One variant = one reader.

2. **What story does this variant tell?** Summarize it in one sentence. If you can't, it's not
   focused enough.

3. **What would distract from that story?** Remove it via `sections` (whole section) or tags
   (individual items). A distraction is worse than a gap.

---

## When to use `sections` vs tags

| Situation                                 | What to do                                        |
| ----------------------------------------- | ------------------------------------------------- |
| Section is off-topic for the role         | `"sections": { "certifications": false }`         |
| Skill exists but irrelevant for this role | Remove its tag for this variant                   |
| Same job, different emphasis              | Keep the job, tag specific highlights differently |
| Completely different summary needed       | Add a key to `summaries` map                      |
| New role type                             | New variant entry + new tags on relevant items    |

### `sections` — whole section on/off (Jinja, pre-compile)

```json
"sections": {
  "about": true,
  "experience": true,
  "skills": true,
  "projects": false,
  "education": true,
  "certifications": true
}
```

Use when the section is **irrelevant** for the role, not just less relevant.

### tags — item-level filtering (Typst, compile-time)

Every taggable item accepts a `"tags"` array. Items with no `tags` field are always included. The
special tag `"all"` means the item appears in every variant.

```json
{ "name": "Kubernetes", "tags": ["devops"] }
{ "name": "Django",     "tags": ["backend"] }
{ "category": "Cloud",  "items": ["GCP", "AWS"], "tags": ["all", "devops"] }
```

---

## Sections reference

### `links`

Used to build the contacts header. Order matters — contacts are rendered in the order declared in
each variant's `contacts` array.

```json
{ "id": "github", "label": "GitHub", "url": "https://github.com/carlosferreyra" }
```

Available IDs: `github`, `linkedin`, `twitter`, `portfolio`, `email`, `leetcode`

### `skills`

Must be grouped by category. Each group can have its own tags.

```json
{
	"category": "Languages",
	"items": ["Python", "TypeScript"],
	"tags": ["all", "backend", "devops"]
}
```

### `experience`

Tags apply to the whole job entry — either it appears or it doesn't. Individual highlight filtering
is not supported at this level.

```json
{
	"title": "Backend Engineer",
	"company": "Devlights S.R.L",
	"period": "March 2021 - Sep 2021",
	"tags": ["all", "backend"],
	"highlights": ["..."]
}
```

### `certifications`

Tag these by domain relevance. Cloud certs → `devops`. DB/SQL certs → `backend`.

### `summaries`

Optional per-variant summary override. If a key matching the variant name exists, it replaces
`personalInfo.summary` for that variant.

```json
"summaries": {
  "devops":  "Platform engineer focused on...",
  "backend": "Backend engineer focused on..."
}
```

If no key matches, `personalInfo.summary` is used as the default.

---

## Adding a new variant

1. Add an entry to `variants[]`:

```json
{
	"name": "data",
	"label": "Data Engineer",
	"contacts": ["github", "linkedin", "email"],
	"sections": {
		"about": true,
		"experience": true,
		"skills": true,
		"projects": true,
		"education": true,
		"certifications": true
	}
}
```

1. Tag relevant items with `"data"` across skills, experience, certifications, projects.

2. Optionally add a `"data"` key to `summaries`.

3. Run `uv run scripts/build_variants.py` — a new `resume/carlos-ferreyra-data.pdf` is produced.

No script changes needed.

---

## Output filenames

| Variant   | Output                               |
| --------- | ------------------------------------ |
| `all`     | `resume/carlos-ferreyra.pdf`         |
| `devops`  | `resume/carlos-ferreyra-devops.pdf`  |
| `backend` | `resume/carlos-ferreyra-backend.pdf` |
| `<name>`  | `resume/carlos-ferreyra-<name>.pdf`  |

---

## Build commands

```bash
# Build all variants
uv run scripts/build_variants.py

# Build a single variant
uv run scripts/build_variants.py --variant devops

# List variants and their output paths
uv run scripts/build_variants.py --list

# Refresh the Typst template (rarely needed)
uv run scripts/fetch_template.py

# Regenerate cv.typ from cv.typ.j2 for a specific variant (debug)
uv run scripts/build_template.py --variant devops
```

---

## Future variant ideas

- **`data`** — surfaces Databricks cert, argendata project, SQL/MongoDB skills
- **`senior`** — shorter format, last 2 jobs only, top 3 certs, no projects section
- **`rust`** / **`java`** — language-specific variants for shops hiring for those stacks
