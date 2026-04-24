# Roadmap — carlosferreyra/carlosferreyra

This document tracks the setup and evolution of my GitHub profile repo, GitHub Pages portfolio, and
the shared CV data layer used across projects.

---

## Priority Order

1. **Phase 1** — GitHub Profile README (ship first)
2. **Phase 3** — `resume.json` schema + CV PDF generation
3. **Phase 2** — Portfolio site
4. **Phase 4** — Ongoing maintenance

---

## Phase 1 — GitHub Profile README

**Goal:** Clean & minimal profile that lets backend/data/devops work speak for itself.

- [x] Promote `docs/README.md` to root `README.md`
  - GitHub renders root `README.md` as the public profile page
  - Structure: brief intro → skills table → pinned projects → stats → contact
  - Keep prose minimal — let badges, stats, and pinned repos carry the weight
- [x] Add GitHub Stats widgets (top-right or bottom section)
  - [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) — general stats card
  - Activity graph — contribution history
  - Use `&theme=dark` with `hide_border=true` for a clean monochrome palette
- [x] Verify profile view counter badge is active (komarev)
- [ ] Pin 4–6 repos that best represent backend, data, and devops work _(account-level setting, not tracked in repo)_
- [x] Keep `CNAME` pointing to `carlosferreyra.com.ar`

---

## Phase 2 — Portfolio Site

**Stack:** [Astro](https://astro.build/) 5 + Tailwind CSS 4 + TypeScript, static output.
**Location:** `web/` (monorepo-style, co-lives with profile README + `data/resume.json`).
**Deploy target:** Cloudflare Pages (primary) — enables future Workers/KV/R2/cache extensions.
GitHub Pages workflow is shipped disabled as a fallback.

**Why Astro over Angular for a portfolio:**

- Ships zero JS by default — fast, SEO-friendly, ideal for static portfolio content
- Component islands allow interactive sections without a full SPA
- Native Markdown/MDX support — easy to add case studies or blog posts later

**Angular-ready:** when an interactive demo is needed, drop `@analogjs/astro-angular` per
`web/docs/adding-angular.md`. Islands live under `src/components/islands/`.

### MVP scaffold (shipped in this phase)

- [x] Scaffold Astro + Tailwind + TS in `web/`
- [x] Design system tokens (GitHub-dark bg `#0d1117`, cold-cyan accent `#00b4d8`,
      JetBrains Mono + Inter) via Tailwind theme + CSS custom properties
- [x] Light/dark theme toggle with OS preference + localStorage persistence
- [x] i18n: English default at `/`, Spanish at `/es/`, shared dictionary in `src/i18n/`
- [x] Layout primitives: `Header` (logo, nav, theme toggle, lang toggle), `Footer`,
      `Button`, `Section`, `SkillGroup`, `ExperienceItem`, `ProjectCard`, `CertificationItem`
- [x] Sections wired to `data/resume.json`: Hero, About, Skills, Experience, Projects,
      Certifications, Contact
- [x] `ProjectCard` renders optional `thumbnail` / `demo` (schema extension — see below);
      falls back to monospace card when absent
- [x] `data/resume.schema.json` — JSON Schema documenting required fields + the new
      optional `projects[].thumbnail` and `projects[].demo` (non-breaking)
- [x] Cloudflare Pages workflow (`.github/workflows/deploy-cloudflare.yml`)
- [x] GitHub Pages workflow shipped disabled
      (`.github/workflows/deploy-pages.yml.disabled`)
- [x] `web/README.md` — dev, build, deploy instructions
- [x] `web/docs/adding-angular.md` — Analog.js migration path

### Post-MVP (follow-ups)

- [ ] Populate `projects[].thumbnail` / `projects[].demo` for existing entries
- [ ] Switch data source to raw GitHub URL once Phase 3 publishes canonical `resume.json`
- [ ] Configure `carlosferreyra.com.ar` DNS → Cloudflare Pages project
- [ ] Add contact form as an island (Turnstile + Cloudflare Worker or Formspree)
- [ ] Add tag filter on projects (backend / devops / fullstack / cli)
- [ ] Blog/case-studies (MDX under `src/content/blog/`)

---

## Phase 3 — `resume.json` as Single Source of Truth + PDF Generation

The file `resume.json` is the **canonical source** for all personal/professional data. Consumer
projects sync from it — nothing maintains its own copy.

### `resume.json` location

```
carlosferreyra/carlosferreyra/resume.json
```

### Schema (document in `resume.schema.json`)

```jsonc
{
  "basics": { "name", "title", "email", "location", "links" },
  "skills": [{ "domain", "items": [] }],
  "experience": [{ "company", "role", "start", "end", "highlights": [] }],
  "education": [{ "institution", "degree", "year" }],
  "certifications": [{ "name", "issuer", "year", "url" }],
  "projects": [{ "name", "description", "tags": [], "url" }]
}
```

> Keeping JSON (not YAML/TOML) ensures compatibility with Typst, rxresume, raw fetch, and any future
> consumer. The schema intentionally mirrors the [JSON Resume](https://jsonresume.org/schema)
> standard for maximum interoperability.

### Sync strategy

| Consumer project  | Strategy                     | Trigger                                   |
| ----------------- | ---------------------------- | ----------------------------------------- |
| `business-card`   | Raw URL fetch at build time  | `repository_dispatch` from this repo's CI |
| Portfolio (Astro) | Raw URL fetch at build time  | `repository_dispatch` from this repo's CI |
| CV PDF (Typst)    | Local copy + CI regeneration | Push to `resume.json` in this repo        |
| rxresume          | Manual import or API push    | JSON maps directly to rxresume schema     |

### Downstream propagation via `repository_dispatch`

When `resume.json` changes, this repo's CI fires a `repository_dispatch` event to trigger rebuilds
in downstream repos automatically — no manual intervention needed.

```yaml
# .github/workflows/notify-consumers.yml
on:
  push:
    paths:
      - resume.json

jobs:
  dispatch:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo: [business-card, carlosferreyra.github.io] # add consumers here
    steps:
      - name: Trigger downstream rebuild
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.DISPATCH_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/carlosferreyra/${{ matrix.repo }}/dispatches \
            -d '{"event_type":"resume-updated"}'
```

Each consumer repo listens with:

```yaml
on:
  repository_dispatch:
    types: [resume-updated]
```

> **Required:** Create a `DISPATCH_TOKEN` secret (PAT with `repo` scope) in
> `carlosferreyra/carlosferreyra` settings.

### CV PDF Generation (Typst + rxresume)

**Typst** is the primary PDF engine — fast, version-controllable, scriptable. **rxresume** is a
secondary option for visual editing and hosted export.

#### Local workflow (manual trigger)

```bash
# scripts/generate-cv.sh
curl -s https://raw.githubusercontent.com/carlosferreyra/carlosferreyra/main/resume.json \
  -o cv/resume.json
typst compile cv/template.typ cv/carlosferreyra-cv.pdf
```

#### CI workflow (GitHub Actions, triggers on push to `main` when `resume.json` changes)

```yaml
# .github/workflows/cv.yml
on:
  push:
    paths:
      - resume.json

jobs:
  generate-cv:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Typst
        run: curl -fsSL https://typst.app/install.sh | sh
      - name: Compile CV
        run: typst compile cv/template.typ cv/carlosferreyra-cv.pdf
      - name: Commit PDF artifact
        run: |
          git config user.name github-actions
          git add cv/carlosferreyra-cv.pdf
          git commit -m "chore: regenerate CV [skip ci]" || echo "No changes"
          git push
```

### Steps

- [ ] Define and commit `resume.json` with full schema
- [ ] Commit `resume.schema.json` for validation
- [ ] Write `cv/template.typ` — Typst template consuming `resume.json`
- [ ] Write `scripts/generate-cv.sh` for local generation
- [ ] Add `.github/workflows/cv.yml` — CI PDF generation on `resume.json` change
- [ ] Add `.github/workflows/notify-consumers.yml` — `repository_dispatch` to downstream repos
- [ ] Add `DISPATCH_TOKEN` secret (PAT, `repo` scope) to this repo's settings
- [ ] Update `business-card` to fetch from raw GitHub URL and listen for `repository_dispatch`
- [ ] Evaluate rxresume JSON mapping — document any field translation needed
- [ ] For each new consumer project: add a fetch/sync step + `repository_dispatch` listener

---

## Phase 4 — Ongoing Maintenance

- [ ] Keep `resume.json` up to date when experience, skills, or certifications change
- [ ] GitHub Action to validate `resume.json` against `resume.schema.json` on every push
  - Use `ajv-cli` or a simple Node script
- [ ] Pin profile README stats widget URLs with `&cache_seconds=` to avoid stale cache
- [ ] Periodically review and archive old projects from the portfolio
- [ ] Tag `resume.json` versions (e.g. `cv-2025-q2`) before major changes

---

## Reference

| Resource              | URL                                                  |
| --------------------- | ---------------------------------------------------- |
| This repo             | <https://github.com/carlosferreyra/carlosferreyra>   |
| Portfolio             | <https://carlosferreyra.com.ar>                      |
| business-card project | `~/Development/carlosferreyra/business-card`         |
| LinkedIn              | <https://linkedin.com/in/eduferreyraok>              |
| Astro docs            | <https://docs.astro.build>                           |
| Typst docs            | <https://typst.app/docs>                             |
| rxresume              | <https://rxresu.me>                                  |
| github-readme-stats   | <https://github.com/anuraghazra/github-readme-stats> |
