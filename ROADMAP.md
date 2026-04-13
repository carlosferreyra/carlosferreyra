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

- [ ] Promote `docs/README.md` to root `README.md`
  - GitHub renders root `README.md` as the public profile page
  - Structure: brief intro → skills table → pinned projects → stats → contact
  - Keep prose minimal — let badges, stats, and pinned repos carry the weight
- [ ] Add GitHub Stats widgets (top-right or bottom section)
  - [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) — general stats card
  - Streak stats — contribution streak
  - GitHub trophies — optional, only if they don't clutter
  - Use `&theme=` to match a clean dark or monochrome palette
- [ ] Verify profile view counter badge is active (komainu)
- [ ] Pin 4–6 repos that best represent backend, data, and devops work
- [ ] Keep `CNAME` pointing to `carlosferreyra.com.ar`

---

## Phase 2 — GitHub Pages Portfolio

**Stack recommendation:** [Astro](https://astro.build/) with Tailwind CSS

**Why Astro over Angular for a portfolio:**

- Ships zero JS by default — fast, SEO-friendly, ideal for static portfolio content
- Component islands allow interactive sections (e.g. contact form, filters) without a full SPA
- Native Markdown/MDX support — easy to add case studies or blog posts later
- Angular is better suited for app-like projects; for a content-first portfolio, Astro wins

**If you later want Angular components** (e.g. a live dashboard or interactive project demo), embed
them as Astro islands using `@analogjs/astro-angular`.

- [ ] Scaffold Astro project

  ```bash
  npm create astro@latest -- --template minimal
  npx astro add tailwind
  ```

- [ ] Build portfolio sections (all data-driven from `resume.json`):
  - Hero — name, title, one-line positioning (backend / data / devops)
  - About — short bio, no fluff
  - Skills — grouped by domain (Backend, Data, DevOps/Cloud, Languages)
  - Experience — timeline, fetched from `resume.json`
  - Projects — filterable by tag (backend / data / devops / OSS)
  - Certifications — from `resume.json`
  - Contact — links from `resume.json`
- [ ] At build time, fetch `resume.json` from raw GitHub URL and inject into Astro content layer

  ```ts
  // astro.config.mjs or a content loader
  const resume = await fetch(
  	'https://raw.githubusercontent.com/carlosferreyra/carlosferreyra/main/resume.json'
  ).then((r) => r.json());
  ```

- [ ] Implement design system — "devops professional" aesthetic:
  - **Theme:** Dark background (`#0d1117` GitHub-dark or similar), not pure black
  - **Accent:** Single color — cold cyan (`#00b4d8`) or terminal green (`#39ff14`), used sparingly
  - **Typography:** Monospace for labels, code snippets, and section headers (e.g. `JetBrains Mono`,
    `IBM Plex Mono`); clean sans-serif for body (e.g. `Inter`, `DM Sans`)
  - **Motion:** Subtle only — fade-in on scroll, no parallax, no flashy transitions
  - **UI motifs:** Terminal-style command prompt for the hero tagline, pipeline/flow diagrams for
    the skills section, grid layout for projects (not cards with heavy shadows)
  - **No:** gradients, illustrations, stock icons, purple anything
- [ ] Configure custom domain via existing `CNAME` (`carlosferreyra.com.ar`)
- [ ] Set up GitHub Actions for auto-deploy on push to `main`

  ```yaml
  # .github/workflows/deploy.yml
  uses: withastro/action@v2
  # then: actions/deploy-pages
  ```

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
