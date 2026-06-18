# Roadmap — carlosferreyra/carlosferreyra

This repo is the single source of truth for my professional data. From one hand-edited data layer it
generates: the GitHub profile README, a portfolio site, PDF resumes, and hosted resumes on
[rxresu.me](https://rxresu.me).

For the concrete open task list, see [BACKLOG.md](BACKLOG.md). This document describes the
**architecture** and its **maintenance principles**.

---

## Architecture

```text
data/baseline.json          common core (hand-edited)
data/stacks/<stack>.json    per-stack deltas: backend, cli, devops, fullstack
data/<combo>.json           combos: { extends: [stacks], slug, ...overrides }
        │
        │  scripts/resume_build.py  (resolve + merge)
        ▼
data/resumes.json           generated — DO NOT EDIT; the stable contract
        │
        ├─ scripts/resume_pdf.py   ─▶ resume/*.pdf            (Typst + silver-dev-cv)
        ├─ scripts/resume_push.py  ─▶ rxresu.me/<user>/<slug> (hosted renderer)
        ├─ scripts/build_readme.py ─▶ README.md               (from README.md.j2)
        └─ web/ (Astro)            ─▶ portfolio site           (imports resumes.json)
```

### Merge semantics (`resume_build.py`)

Stack deltas override `baseline.json`:

- scalar / list → **replace**
- dict → **deep-merge**
- `null` → **hide** that section
- absent → **inherit** from baseline

Combos (`extends: [...]`) **union** list sections (deduped) across the extended stacks, then apply
scalar overrides on top.

### The contract

`data/resumes.json` is the only thing consumers read. PDF, rxresu.me, README, and the Astro site
never touch `baseline`/stacks directly. Lock its shape and a new output is just a new consumer of
the same JSON — no change to the data layer.

> JSON (not YAML/TOML) keeps compatibility with Typst, rxresu.me, raw fetch, and any future
> consumer. The shape mirrors [JSON Resume](https://jsonresume.org/schema) where practical.

---

## Current variants (slugs)

| Slug              | Source                                       | Output                                 |
| ----------------- | -------------------------------------------- | -------------------------------------- |
| `carlos-ferreyra` | `data/dev.json` (combo: fullstack + backend) | `resume/carlos-ferreyra.pdf`           |
| `backend`         | `data/stacks/backend.json`                   | `resume/carlos-ferreyra-backend.pdf`   |
| `fullstack`       | `data/stacks/fullstack.json`                 | `resume/carlos-ferreyra-fullstack.pdf` |
| `devops`          | `data/stacks/devops.json`                    | `resume/carlos-ferreyra-devops.pdf`    |
| `cli`             | `data/stacks/cli.json`                       | `resume/carlos-ferreyra-cli.pdf`       |

See [data/README.md](data/README.md) for the field-level reference and how to add a stack or combo.

---

## CI / CD

| Workflow                    | Trigger                                              | Does                                                              |
| --------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------- |
| `resume-data.yml`           | push to `main` touching `data/**`, scripts, template | build `resumes.json` → PDFs → push to rxresu.me, commit artifacts |
| `build-readme.yml`          | data change                                          | regenerate `README.md` from `README.md.j2`                        |
| `deploy-cloudflare.yml`     | push to `main` touching `web/**` or `resumes.json`   | deploy portfolio to Cloudflare Pages                              |
| `deploy-pages.yml.disabled` | —                                                    | GitHub Pages fallback (off)                                       |

**Secrets required:** `RXRESUME_TOKEN`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Local
credentials live in `.env` (gitignored).

---

## Local commands

```bash
uv run scripts/resume_build.py        # resolve baseline + stacks + combos -> resumes.json
uv run scripts/resume_pdf.py          # render all PDFs (Typst)
uv run scripts/resume_pdf.py --slug backend
uv run scripts/resume_push.py         # dry-run push to rxresu.me
uv run scripts/resume_push.py --apply
uv run scripts/build_readme.py        # regenerate README.md
uv run scripts/fetch_template.py      # refresh silver-dev-cv Typst template (rare)

cd web && bun install && bun dev      # portfolio dev server
```

---

## Maintenance principles

- **Edit data, never generated files.** Touch `baseline.json` / a stack / a combo; `resumes.json`,
  the PDFs, and the README are outputs.
- **rxresu.me is a renderer, not a source.** Edits made in its UI are overwritten on the next push.
  Change the repo instead.
- **Keep it boring.** New needs are a new stack, a new combo, or a new consumer of `resumes.json` —
  not a new data format or abstraction layer.
- **Pin upstream.** The `silver-dev-cv` Typst version is pinned via the template import so an
  upstream change can't silently alter every PDF.
- **Validate before publish.** A malformed delta should fail CI, not produce a silently-wrong resume
  (see BACKLOG §5 — schema + validation).

---

## Reference

| Resource      | URL                                                |
| ------------- | -------------------------------------------------- |
| This repo     | <https://github.com/carlosferreyra/carlosferreyra> |
| Portfolio     | <https://carlosferreyra.com.ar>                    |
| rxresu.me     | <https://rxresu.me/carlosferreyra/carlos-ferreyra> |
| LinkedIn      | <https://linkedin.com/in/eduferreyraok>            |
| Astro docs    | <https://docs.astro.build>                         |
| Typst docs    | <https://typst.app/docs>                           |
| silver-dev-cv | <https://typst.app/universe/package/silver-dev-cv> |
