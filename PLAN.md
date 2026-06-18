# Resume Pipeline Plan

## Goal

Keep the current multi-file resume model simple, documented, and reproducible:

```text
data/baseline.json
data/stacks/*.json
data/dev.json
        |
        | scripts/resume_build.py
        v
data/resumes.json
        |
        +-- scripts/resume_pdf.py   -> resume/*.pdf
        +-- scripts/resume_push.py  -> rxresu.me
        +-- scripts/build_readme.py -> README.md
        +-- web/src/lib/resume.ts   -> Astro portfolio
```

`data/resumes.json` is the generated contract shared by every renderer. It is committed for
downstream consumers, but it must not be edited by hand.

## Current Sources

- `data/baseline.json`: shared identity, contact, and professional data.
- `data/stacks/*.json`: stack-specific overrides for `backend`, `cli`, `devops`, and `fullstack`.
- `data/dev.json`: combo extending backend and fullstack; publishes as `carlos-ferreyra`.
- `data/themes.json`: RxResume presentation settings.

## Supported Commands

```bash
uv run scripts/resume_build.py
uv run scripts/resume_build.py --list
uv run scripts/build_readme.py
uv run scripts/resume_pdf.py
uv run scripts/resume_pdf.py --slug backend
uv run scripts/resume_push.py
uv run scripts/resume_push.py --slug backend
uv run scripts/resume_push.py --apply
cd web && bun run build
```

RxResume is dry-run by default. `--apply` is the only command that changes remote resumes.

## Completion Criteria

- [x] Five resolved slugs are generated: `backend`, `cli`, `devops`, `fullstack`, and
      `carlos-ferreyra`.
- [x] README, PDF, RxResume, and Astro consumers read `data/resumes.json`.
- [x] RxResume presentation is owned by `data/themes.json`.
- [x] Local commands support listing and targeted PDF/RxResume operations.
- [x] Workflow names and triggers match the current pipeline.
- [x] Documentation describes the multi-file source model.
- [ ] Add schemas and validation for source files and `data/resumes.json`.
- [ ] Add regression tests for stack override, combo union, and deduplication behavior.
- [ ] Decide whether deleting a local slug should prune its remote RxResume entry.
- [ ] Add a single command that runs build, README, PDF, and web verification.

## Operating Rules

- Edit source files, never `data/resumes.json`, generated PDFs, or `README.md`.
- Run `resume_build.py` before every renderer.
- Treat RxResume as a renderer; UI edits are overwritten by the next `--apply`.
- Add new variants as a stack or combo without introducing another data format.
- Keep credentials in `.env` locally and GitHub Actions secrets in CI.
