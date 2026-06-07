# Plan: Reactive Resume (RxResume) as the source of truth for `data/resume.json`

## Goal

Stop hand-editing [`data/resume.json`](data/resume.json). Instead, edit the
resume once in [Reactive Resume](https://rxresu.me) (the visual editor) and let a
**GitHub Action** pull it from the RxResume API, transform it into our existing
schema, and commit it back to the repo on a schedule.

Everything downstream of `resume.json` stays unchanged.

## Why this is a transform, not a swap

RxResume has its **own** JSON schema (`basics`, `sections.{summary,profiles,
experience,education,skills,projects,certifications,…}`, `metadata`). Our repo
uses a **custom** schema:

```
personalInfo, summaries, githubUsername, links, skills,
experience, education, certifications, projects, variants
```

These do **not** line up field-for-field. So the source of truth becomes
RxResume, but `data/resume.json` remains the **canonical contract** — produced
by an adapter rather than by hand. This keeps the blast radius to a single new
script + workflow.

## The contract we must NOT break

`data/resume.json` (this exact path, on `main`, with this exact shape) is
consumed by **five** things — three in-repo and one external:

| Consumer | How it reads | Repo |
| --- | --- | --- |
| Portfolio site | `import '@data/resume.json'` → [`web/src/lib/resume.ts`](web/src/lib/resume.ts) | this repo |
| Typst CV builder | [`scripts/build_variants.py`](scripts/build_variants.py) + `silver-dev-cv/cv.typ.j2` | this repo |
| Profile README builder | [`scripts/build_readme.py`](scripts/build_readme.py) | this repo |
| **business-card** | `fetch('https://raw.githubusercontent.com/carlosferreyra/carlosferreyra/main/data/resume.json')` | **carlosferreyra/business-card** |

The external consumer is the migration constraint. As long as the **raw URL,
file path, and JSON schema stay identical**, business-card needs **zero
changes**. That is the whole migration strategy: *change how `resume.json` is
produced, not what it is.*

The schema is enforced by [`data/resume.schema.json`](data/resume.schema.json) —
the adapter's output MUST validate against it. That schema is the safety net.

---

## Architecture

```
RxResume (rxresu.me editor)
        │  GET resume JSON via API  (RxResume schema)
        ▼
.github/workflows/sync-resume.yml   (scheduled + manual)
        │  scripts/sync_resume.py
        │    1. fetch RxResume JSON
        │    2. map → our schema (adapter)
        │    3. merge repo-only fields (summaries, variants, githubUsername)
        │    4. validate against resume.schema.json
        │    5. write data/resume.json
        ▼
data/resume.json  ──▶ site / Typst CV / README / business-card (unchanged)
        │  on change, existing build-resume.yml & build-readme.yml fire
        ▼
git auto-commit  ──▶ raw.githubusercontent .../main/data/resume.json
```

---

## Open questions to confirm before building (Section 1 of CLAUDE.md)

1. **Which RxResume?** Cloud (`rxresu.me`) or a self-hosted instance? This
   decides the base URL and auth mechanism. **Assumption: cloud.**
2. **Auth / endpoint.** Confirm the exact way to pull the resume JSON. Likely
   one of:
   - Public resume export: `GET /api/resume/public/{username}/{slug}` (no auth,
     but only exposes published fields), or
   - Authenticated fetch with an API token / cookie for the private resume.

   This is the single biggest unknown — **verify the real endpoint + auth before
   writing the adapter**, because it determines which fields are even available.
3. **Field coverage.** RxResume has no native concept of our `summaries`
   (devops/backend/fullstack/cli variants), `variants`, or `githubUsername`.
   Decision: keep these as **repo-managed fields** the adapter preserves from the
   existing `resume.json` (read-merge), OR encode them in RxResume custom
   sections. **Recommendation: repo-managed merge** — simpler, no abuse of the
   editor.

---

## Field mapping (RxResume → our schema)

| Our field | RxResume source | Notes |
| --- | --- | --- |
| `personalInfo.name` | `basics.name` | |
| `personalInfo.title` | `basics.headline` | |
| `personalInfo.email` | `basics.email` | |
| `personalInfo.location` | `basics.location` | |
| `personalInfo.summary` | `sections.summary.content` | strip HTML → plain text |
| `links[]` | `basics.url` + `sections.profiles.items[]` | map to our `{id,label,url}`; derive stable `id` from network name |
| `skills[]` | `sections.skills.items[]` | group into our `{category,items[]}` shape |
| `experience[]` | `sections.experience.items[]` | `company`, `title=position`, `period` from date range, `highlights` from summary bullets |
| `education[]` | `sections.education.items[]` | `degree=studyType/area`, `institution`, `period`, `highlights` |
| `certifications[]` | `sections.certifications.items[]` | `name`, `year`, `url` |
| `projects[]` | `sections.projects.items[]` | `name`, `description`, `url`, optional `tags` |
| `githubUsername` | — | **repo-managed**, preserved from existing file |
| `summaries` | — | **repo-managed**, preserved from existing file |
| `variants` | — | **repo-managed**, preserved from existing file |

**HTML handling:** RxResume stores rich text as HTML. The adapter must convert
to the plain strings / bullet arrays our schema expects.

---

## Build steps → verification (Section 4 of CLAUDE.md)

1. **Confirm the API contract** (endpoint + auth + sample payload).
   → verify: `curl` the endpoint, save a real `fixtures/rxresume.sample.json`.

2. **Write `scripts/sync_resume.py`** — fetch, map, merge repo-only fields,
   validate, write. Use `uv` (matches existing scripts) + `jsonschema`.
   → verify: run against the fixture offline; output validates against
   `data/resume.schema.json` and diffs cleanly against today's `resume.json`
   (semantically equal modulo intended changes).

3. **Snapshot/regression guard.** Run the adapter on current RxResume data; the
   produced `resume.json` must reproduce today's hand-written file (or the diff
   must be reviewed and accepted as the new baseline).
   → verify: `git diff data/resume.json` is empty or intentional.

4. **Add `.github/workflows/sync-resume.yml`** — `workflow_dispatch` +
   `schedule` (e.g. daily) + `permissions: contents: write`. Steps: checkout →
   setup-uv → `uv run scripts/sync_resume.py` → `git-auto-commit-action` on
   `data/resume.json` (commit message **without** `[skip ci]` so the existing
   `build-resume.yml` / `build-readme.yml` chain fires on change).
   → verify: manual `workflow_dispatch` run produces a clean commit and triggers
   the downstream PDF/README builds.

5. **Secrets.** Store the RxResume token as `RXRESUME_TOKEN` (and base URL /
   username as needed) in repo Actions secrets.
   → verify: workflow reads them; no secret is printed in logs.

---

## Migration sequence (zero-downtime for business-card)

1. **Phase 0 — adapter parity.** Build `sync_resume.py` and prove it reproduces
   the current `data/resume.json` byte-for-byte (or with reviewed diff). Nothing
   is wired up yet. *business-card unaffected.*

2. **Phase 1 — shadow run.** Add `sync-resume.yml` as `workflow_dispatch`-only.
   Run manually, inspect the committed diff. The raw URL keeps serving the same
   schema. *business-card unaffected.*

3. **Phase 2 — go live.** Enable the `schedule`. RxResume becomes the editing
   surface; `resume.json` is now generated. *business-card still hits the same
   raw URL, same schema — no change required there.*

4. **Phase 3 — stop hand-edits.** Add a note to [`data/resume.json`](data/resume.json)'s
   docs ([`web/src/lib/README.md`](web/src/lib/README.md)) that it is now
   **generated** — edit in RxResume, not here. Optionally add a CI check that
   fails if `resume.json` is edited by hand in a PR (drift guard).

**business-card never migrates.** It depends on the *output contract*, which is
deliberately held constant. The only thing that would force a business-card
change is a schema change — which this plan explicitly avoids.

### Fallback / safety

- If the RxResume API is down or returns malformed data, `sync_resume.py` exits
  non-zero **before** writing — the last good `resume.json` stays committed.
- Schema validation is a hard gate: an output that fails `resume.schema.json` is
  never committed.
- `resume.json` stays version-controlled, so every sync is a reviewable diff and
  trivially revertible.

---

## Files to add / change

| File | Change |
| --- | --- |
| `scripts/sync_resume.py` | **new** — fetch + adapter + merge + validate + write |
| `tests/fixtures/rxresume.sample.json` | **new** — captured API payload for offline tests |
| `.github/workflows/sync-resume.yml` | **new** — scheduled + manual sync |
| Repo Actions secrets | **new** — `RXRESUME_TOKEN`, base URL/username |
| `web/src/lib/README.md` | **edit** — note `resume.json` is now generated |
| `data/resume.json` | unchanged shape; now produced by the action |

No changes to `resume.ts`, the Typst builder, the README builder, or
business-card.
