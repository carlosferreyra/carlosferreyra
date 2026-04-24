# carlosferreyra · web

Personal portfolio at [carlosferreyra.com.ar](https://carlosferreyra.com.ar).

Astro 5 + Tailwind 4 + TypeScript, static output. Content is sourced from
[`../data/resume.json`](../data/resume.json) (validated by
[`../data/resume.schema.json`](../data/resume.schema.json)). Angular-ready —
see [`docs/adding-angular.md`](docs/adding-angular.md).

## Stack

| Concern     | Choice                                                           |
| ----------- | ---------------------------------------------------------------- |
| Framework   | [Astro 5](https://astro.build/) (zero JS by default, SSG)        |
| Styles      | [Tailwind CSS 4](https://tailwindcss.com/) via `@tailwindcss/vite` |
| Language    | TypeScript (strict)                                              |
| i18n        | Astro's built-in i18n routing (`en` default, `/es/` Spanish)     |
| Deploy      | Cloudflare Pages (primary) — GitHub Pages fallback shipped disabled |

## Local development

```bash
cd web
npm install
npm run dev         # http://localhost:4321
npm run build       # typecheck + static build → web/dist
npm run preview     # preview the built site
```

Dev requires Node 20+.

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
npm run typecheck     # astro check
npm run build         # also runs astro check
```

No test runner is wired yet; `astro check` covers the static surface.

## Adding Angular components

See [`docs/adding-angular.md`](docs/adding-angular.md). Short version:

```bash
npx astro add @analogjs/astro-angular
```

Drop `.component.ts` files into `src/components/islands/` and import them
into `.astro` pages with a client directive. No other changes required.
