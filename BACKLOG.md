# Backlog

Pending work to deploy the portfolio, keep resumes in sync (repo + rxresu.me), and
stabilize the resume-generation architecture so it doesn't need rework over time.

Current branch: `migrate-to-rxresume`. The data layer uses a
`baseline + stacks + combos → resumes.json` pipeline (commits `8966a22`, `299a80e`).
The roadmap and data/web documentation now describe that current architecture.

---

## How the system works today (ground truth)

```
data/baseline.json          common core (hand-edited)
data/stacks/<stack>.json    per-stack deltas: backend, cli, devops, fullstack
data/<combo>.json           combos: extends[] + slug + overrides (e.g. dev.json)
        │
        ├─ scripts/resume_build.py ─▶ data/resumes.json   (generated, do not edit)
        │
        ├─ scripts/resume_pdf.py   ─▶ resume/*.pdf         (Typst + silver-dev-cv)
        ├─ scripts/resume_push.py  ─▶ rxresu.me/<user>/<slug>
        └─ scripts/build_readme.py ─▶ README.md            (from README.md.j2)

web/ (Astro) imports data/resumes.json via web/src/lib/resume.ts
```

CI:
- `.github/workflows/resume-data.yml` — build resumes.json, PDFs, push to rxresu.me on data change
- `.github/workflows/build-readme.yml` — regenerate README
- `.github/workflows/deploy-cloudflare.yml` — deploy `web/` to Cloudflare Pages
- `.github/workflows/deploy-pages.yml.disabled` — GitHub Pages fallback (off)

Slugs currently produced: `backend`, `cli`, `devops`, `fullstack`, `carlos-ferreyra` (combo).

---

## 1. Deploy the portfolio website

- [ ] Finish and merge the `migrate-to-rxresume` branch into `main` (the deploy
      workflow only triggers on `main`).
- [ ] Confirm Cloudflare Pages project exists and required secrets are set
      (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`) in repo settings →
      verify `deploy-cloudflare.yml` runs green end-to-end.
- [ ] Point `carlosferreyra.com.ar` DNS at the Cloudflare Pages project
      (ROADMAP Phase 2 "Configure DNS" item, still open).
- [ ] Verify `CNAME` (`carlosferreyra.com.ar`) is consistent with the chosen host —
      `CNAME` is a GitHub Pages artifact; if Cloudflare is primary, decide whether
      it's still needed or should move under `web/public/`.
- [ ] Smoke-test the deployed site: EN at `/`, ES at `/es/`, theme picker, and that
      every section renders from `resumes.json` (Hero, About, Skills, Experience,
      Projects, Certifications, Contact).
- [ ] Decide: keep GitHub Pages workflow as a real fallback (and test enabling it)
      or delete `deploy-pages.yml.disabled` to remove dead config.

**Verify:** pushing to `main` deploys; `https://carlosferreyra.com.ar` serves the
current portfolio with live data.

---

## 2. Resumes available in repo + rxresu.me

- [ ] Confirm `RXRESUME_TOKEN` (and `RXRESUME_BASE_URL`, `RXRESUME_USERNAME`) are set
      as repo secrets so `resume-data.yml`'s push step works in CI (locally they live
      in `.env`, which is gitignored — good).
- [ ] Run a full pipeline dry-run end-to-end and confirm all 5 slugs land at
      `rxresu.me/<username>/<slug>` and `resume/*.pdf` are regenerated.
- [ ] Verify the README "Resume: PDF" link still resolves to
      `resume/carlos-ferreyra.pdf` after the combo rename.
- [ ] Document the rxresu.me ↔ repo relationship in one place: repo is the source of
      truth, rxresu.me is a renderer, edits made in the rxresu.me UI are **not** synced
      back and will be overwritten on next push (call this out to avoid surprise).

**Verify:** `resume/` PDFs and rxresu.me pages match `data/resumes.json` after CI.

---

## 3. CRUD resumes

Today this is a build pipeline, not true CRUD. Map each operation explicitly:

- [x] **Create** a new variant: `data/README.md` documents the stack/combo workflow.
- [x] **Read/List**: add a `--list` command to `resume_build.py` so you
      can see all resolved slugs and their output paths without opening `resumes.json`.
- [ ] **Update**: confirm editing `baseline.json` / a stack file rebuilds every affected
      resume (deep-merge + list-union semantics) — add a quick test/fixture.
- [ ] **Delete**: define what removing a stack/combo does — does the rxresu.me push
      delete the stale remote resume, or leave an orphan? `resume_push.py` currently
      creates/updates; add (or document the absence of) a prune step for removed slugs.
- [ ] Decide whether a thin `scripts/resume.py` CLI wrapping build/pdf/push/list is
      worth it, or whether `uv run` per-script is enough. (Lean toward not adding it
      unless the per-script UX actually hurts.)

**Verify:** each CRUD action has one documented command and a predictable effect on
both `resume/` and rxresu.me.

---

## 4. Clear stalled / outdated files

- [x] **`ROADMAP.md`** — rewritten around the current multi-file source model and generated
      `resumes.json` contract.
- [x] **`data/README.md`** — rewritten around `resume_build.py`, stacks, combos, and merge rules.
- [x] **`RXRESUME.md`** — removed; current RxResume behavior is documented with the pipeline.
- [x] **`docs/README_ARCHIVE.md`** — removed as a stale duplicate.
- [x] **`QUICKSTART.md`** — removed because it was unrelated to the repository.
- [ ] **`data/dev.json`** — combo named `dev` producing slug `carlos-ferreyra`; the
      filename/slug mismatch is confusing. Rename the file to match its slug/intent.
- [ ] Audit `silver-dev-cv/cv.typ` (committed) vs `cv.typ.j2` — confirm the compiled
      `cv.typ` is a generated artifact that shouldn't be hand-edited (gitignore it) or
      a needed checked-in template.
- [ ] Sweep for other orphans: confirm `README.md.j2`, `scripts/fetch_template.py`, and
      `silver-dev-cv/template/` are all still on the live path.

**Verify:** every remaining operational doc describes the current pipeline and no active
instructions reference a script or source file that does not exist.

---

## 5. Simplify generation (no resume from scratch)

The central-JSON goal is already largely met — `baseline.json` is the single core and
stacks/combos are deltas (override/merge/union), so you never start from scratch. Close
the gaps:

- [ ] Document the merge semantics precisely (scalar/list → replace, dict → deep-merge,
      `null` → hide section, absent → inherit; combos union lists) in `data/README.md`
      with a worked example, so adding a stack is copy-paste, not archaeology.
- [ ] Add a single command that rebuilds **everything** locally
      (`resumes.json` → PDFs → README) for a fast edit-preview loop.
- [ ] Add a JSON Schema for `baseline.json` / stack / combo files plus a validation step
      in `resume-data.yml`, so a malformed delta fails fast instead of producing a
      silently-wrong resume. (ROADMAP Phase 4 had this intent against the old schema.)
- [ ] Add `--dry-run`/diff output to `resume_build.py` so you can see what a stack edit
      changes across all resumes before committing.

**Verify:** editing one field in `baseline.json` updates all resumes with one command;
invalid input is rejected by CI.

---

## 6. Architecture changes for long-term consistency

- [ ] **Single rendering contract.** PDF (Typst), rxresu.me, README, and the Astro site
      all consume `resumes.json`. Lock its shape with a schema and treat it as the
      stable interface; consumers should never read `baseline`/stacks directly. (Astro
      already imports `resumes.json` via `web/src/lib/resume.ts` — keep it that way.)
- [ ] **Idempotent, ordered pipeline.** Ensure the canonical order is
      `build → validate → pdf → push → readme`, each step pure and re-runnable, so CI and
      local runs are identical. Document it once.
- [ ] **rxresu.me as a pure renderer.** Make the push reconcile state (create / update /
      prune) from `resumes.json` so the remote can never drift from the repo. Decide the
      policy for UI-side edits (overwrite vs. protect) and enforce it in `resume_push.py`.
- [ ] **Decouple the Typst template.** `fetch_template.py` pulls `silver-dev-cv` from
      Typst Universe; pin a version so an upstream change can't silently alter every PDF.
- [ ] **One source of truth for shared identity.** Name, links, and summary feed README +
      site + every resume from `baseline.json`. Verify nothing (web i18n strings, README
      template) hardcodes values that should come from data; centralize any stragglers.
- [ ] **Versioning/changelog.** Tag resume snapshots (e.g. `cv-2026-q2`) before major
      edits so a regression in a generated PDF is traceable to a data change.
- [ ] **Keep it boring.** Resist per-consumer config and extra abstraction layers — the
      `baseline + delta → one JSON → many renderers` shape is the simplification; new
      needs should be a new stack/combo or a new renderer reading the same JSON, not a
      new data format.

**Verify:** adding a new output (e.g. a new site, a new PDF theme) requires only a new
consumer of `resumes.json` — no changes to the data layer or existing consumers.

---

## Suggested sequencing

1. **Unblock deploy** (§1) + confirm rxresu.me secrets (§2) — get the public surfaces live.
2. **Clean stale docs/files** (§4) — cheap, removes confusion before further work.
3. **Schema + validation + one-shot rebuild** (§5) — hardens the pipeline.
4. **CRUD semantics + prune** (§3) — makes day-to-day edits safe.
5. **Architecture hardening** (§6) — version pinning, reconcile push, tagging.
