# Unified Labeled Resume

`resume.json` is the single hand-edited source for every resume surface. It contains shared
identity data, named profiles, and explicitly labeled content. Profiles use exact matching:
`default` does not implicitly flow into `backend`, `devops`, or any other profile.

## Data contract

- `profiles` declares each label's slug, headline, summary, and output targets.
- Every link, skill group, job, education entry, certification, and project has `labels`.
- Experience and education highlights have their own labels for fine-grained tailoring.
- Shared records list every profile that should receive them.
- `resume.schema.json` documents the public shape; `scripts/resume/core.py` enforces cross-field
  rules such as declared labels and unique slugs.
- `data/themes.json` remains separate because it is RxResume presentation configuration.

The external contract for the business card is:

```text
https://raw.githubusercontent.com/carlosferreyra/carlosferreyra/main/resume.json
```

The business-card consumer should resolve the exact `business-card` label and must not assume that
`default` content is inherited.

## Commands

```bash
uv run scripts/resume validate
uv run scripts/resume list
uv run scripts/resume resolve --profile backend
uv run scripts/resume readme
uv run scripts/resume pdf [--profile backend]
uv run scripts/resume rxresume [--profile backend] [--apply]
uv run scripts/resume build
uv run scripts/resume check
```

Resolved profiles and RxResume request bodies are ephemeral. Only `README.md` and profiles targeting
`pdf` are generated and committed. RxResume is dry-run by default; `--apply` is required to mutate
remote resumes.

## Consumer mapping

| Consumer | Selection |
| --- | --- |
| Website | `default` |
| README | `default` |
| Typst | Every profile targeting `pdf`, or explicit `--profile` |
| RxResume | Every profile targeting `rxresume`, or explicit `--profile` |
| Business card | `business-card` from the public raw JSON |

## Completion checklist

- [x] One canonical, labeled `resume.json` replaces baseline, stacks, combos, and `resumes.json`.
- [x] Shared validation and resolution power local commands and GitHub Actions.
- [x] README, Typst, RxResume, and Astro consume resolved canonical profiles.
- [x] Consumer-specific JSON files are not generated or committed.
- [x] CI validates before rendering and uses the same orchestration command as local builds.
- [ ] Refactor `carlosferreyra/business-card` to fetch the public contract and select its label.
