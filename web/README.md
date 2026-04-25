# carlosferreyra · web

Personal portfolio at [carlosferreyra.com.ar](https://carlosferreyra.com.ar).

Astro 5 + Tailwind 4 + TypeScript, static output, **[Bun](https://bun.sh) as the
default runtime / package manager**. Content is sourced from
[`../data/resume.json`](../data/resume.json) (validated by
[`../data/resume.schema.json`](../data/resume.schema.json)). Angular-ready —
see [`docs/adding-angular.md`](docs/adding-angular.md).

## Stack

| Concern     | Choice                                                              |
| ----------- | ------------------------------------------------------------------- |
| Runtime / PM | [Bun](https://bun.sh) ≥ 1.2 — committed `bun.lock`, pinned via `packageManager` |
| Framework   | [Astro 5](https://astro.build/) (zero JS by default, SSG)           |
| Styles      | [Tailwind CSS 4](https://tailwindcss.com/) via `@tailwindcss/vite`  |
| Language    | TypeScript (strict)                                                 |
| i18n        | Astro's built-in i18n routing (`en` default, `/es/` Spanish)        |
| Deploy      | Cloudflare Pages (primary) — GitHub Pages fallback shipped disabled |

## Prerequisites

- [Bun](https://bun.sh) ≥ 1.2 — install with `curl -fsSL https://bun.sh/install | bash`
- Node 20+ is **only** needed if you fall back to npm (see below). Bun ships its own runtime,
  but a couple of upstream tools (e.g. `astro check`'s language server) still expect a Node-compatible env, which Bun provides transparently.

## Local development

```bash
cd web
bun install
bun run dev          # http://localhost:4321
bun run build        # typecheck + static build → web/dist
bun run preview      # preview the built site
bun run typecheck    # astro check only
```

You can also use Bun's shorter aliases:

```bash
bun dev              # same as `bun run dev`
bun build            # ⚠ NOT the same — `bun build` is Bun's bundler. Use `bun run build`.
```

> **Heads up:** `bun build` (no `run`) invokes Bun's bundler directly and bypasses Astro.
> Always use `bun run build` for the project build.

### npm fallback

The project is bun-first but stays compatible with npm if needed:

```bash
cd web
npm install          # regenerates package-lock.json — do NOT commit it
npm run dev
```

`bun.lock` is the canonical lockfile; `package-lock.json` is intentionally **not** committed.
If you must use npm in CI, regenerate the lock locally and pass `--package-lock-only`.

## Project layout

```
web/
├── astro.config.mjs     Astro + Tailwind + i18n config
├── public/              Static assets served as-is
├── src/
│   ├── components/      Layout primitives + sections
│   │   ├── islands/     Reserved for interactive frameworks (Angular, etc.)
│   │   └── sections/    Hero, About, Skills, Experience, Projects, …
│   ├── i18n/            Shared dictionary (en, es) + helpers
│   ├── layouts/         BaseLayout wraps every page
│   ├── lib/resume.ts    Typed reader for ../data/resume.json
│   ├── pages/           Route files (/, /es/)
│   ├── scripts/         Inline browser scripts (theme bootstrap, …)
│   └── styles/          Tailwind entry + design tokens
└── tsconfig.json
```

## Design system

Dark-first palette inspired by GitHub dark, with a single cold-cyan accent.

| Token              | Dark      | Light     |
| ------------------ | --------- | --------- |
| `--color-bg`       | `#0d1117` | `#ffffff` |
| `--color-bg-elev`  | `#161b22` | `#f6f8fa` |
| `--color-fg`       | `#e6edf3` | `#1f2328` |
| `--color-fg-muted` | `#9198a1` | `#59636e` |
| `--color-accent`   | `#00b4d8` | `#0969da` |

Theme toggle persists to `localStorage` under `theme`; initial value respects
`prefers-color-scheme`. An inline script in `<head>` applies it before paint
to avoid FOUC.

Typography: `JetBrains Mono` for labels/headings, `Inter` for body — loaded
once from Google Fonts with `preconnect`.

## i18n

Routes are generated from a single dictionary:

- `src/i18n/en.ts` — English (default, served at `/`)
- `src/i18n/es.ts` — Spanish (served at `/es/`)

Each page imports the dictionary via `t(locale)`. The language toggle in the
header uses `alternateLocaleHref(...)` to stay on the current section when
switching languages.

Adding a locale: add `fr.ts`, register it in `src/i18n/index.ts`, add the code
to `astro.config.mjs#i18n.locales`, and create `src/pages/fr/index.astro`.

## Data source

Imported at build time from `../data/resume.json` via a TypeScript path alias:

```ts
// web/src/lib/resume.ts
import resumeJson from '../../../data/resume.json';
```

Schema lives at `data/resume.schema.json`. The portfolio adds two **optional**
fields to `projects[]` (see schema): `thumbnail` (preview image) and `demo`
(live URL). Existing consumers (profile README builder, Typst CV) ignore them.

When [Phase 3](../ROADMAP.md) publishes the canonical resume, swap the import
for a raw GitHub fetch at build time — the `Resume` type stays the same.

## Deploy

### Cloudflare Pages (primary)

Workflow: [`.github/workflows/deploy-cloudflare.yml`](../.github/workflows/deploy-cloudflare.yml)

Required repo secrets:

- `CLOUDFLARE_API_TOKEN` — token with `Account > Cloudflare Pages:Edit`
- `CLOUDFLARE_ACCOUNT_ID`

Required Cloudflare setup:

1. Create a Pages project named `carlosferreyra` (or edit the workflow).
2. Point `carlosferreyra.com.ar` at the Pages project under *Custom domains*.

Triggers on pushes to `main` that touch `web/**` or `data/resume*.json`.

### GitHub Pages (fallback)

Rename `.github/workflows/deploy-pages.yml.disabled` → `deploy-pages.yml`
and disable the Cloudflare workflow. Instructions at the top of that file.

## Quality

```bash
bun run typecheck     # astro check
bun run build         # also runs astro check
```

No test runner is wired yet; `astro check` covers the static surface.

## Adding Angular components

See [`docs/adding-angular.md`](docs/adding-angular.md). Short version:

```bash
bunx astro add @analogjs/astro-angular
```

Drop `.component.ts` files into `src/components/islands/` and import them
into `.astro` pages with a client directive. No other changes required.

## Why Bun

- Single-binary runtime, package manager, and script runner — fewer moving parts than
  Node + npm/pnpm/yarn.
- Bun's installer is **5–10× faster** than npm on cold cache; matters every time CI cold-starts.
- `bun.lock` is text-readable and merge-friendly (unlike older binary `bun.lockb`).
- Astro and Tailwind 4 both support Bun out of the box; the toolchain stays vanilla.
- Cloudflare Workers (likely Phase 2 follow-up: contact form, edge cache APIs) are
  Bun-friendly via `wrangler dev` — keeping the local runtime aligned with the edge target
  reduces surprise bugs.
