# Adding Angular components (via Analog.js)

The portfolio is Astro-first and ships zero JS. When an Angular-powered
interactive feature is needed (live dashboard, filterable project explorer,
animated canvas demo, …), embed it as an **island** using
[`@analogjs/astro-angular`](https://analogjs.org/docs/packages/astro-angular/overview).
Islands hydrate on demand, so the rest of the page stays static.

## One-time setup

From `web/`:

```bash
bunx astro add @analogjs/astro-angular
```

The integration writes `tsconfig.app.json` and updates `astro.config.mjs` to
include the Angular Vite plugin. Accept the prompts.

If you prefer a manual install:

```bash
bun add -d @analogjs/astro-angular @angular/common @angular/compiler @angular/core @angular/platform-browser @angular-devkit/build-angular
```

Then register the integration in `astro.config.mjs`:

```js
import angular from '@analogjs/astro-angular';

export default defineConfig({
  integrations: [angular()],
  // ...existing i18n + Tailwind config
});
```

## Authoring an Angular island

Create the component under `src/components/islands/`:

```ts
// src/components/islands/ProjectsExplorer.component.ts
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

@Component({
  selector: 'app-projects-explorer',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="font-mono text-sm">
      <button (click)="count.update((n) => n + 1)">
        tapped {{ count() }} times
      </button>
    </section>
  `,
})
export class ProjectsExplorerComponent {
  count = signal(0);
}
```

Then import it into any `.astro` page with a client directive:

```astro
---
import { ProjectsExplorerComponent } from '~/components/islands/ProjectsExplorer.component';
---

<ProjectsExplorerComponent client:visible />
```

Client directives: `client:load`, `client:idle`, `client:visible`,
`client:media`, `client:only="angular"`. Prefer `client:visible` for
below-the-fold demos to keep the initial payload small.

## Styling

Reuse the existing Tailwind design tokens inside the Angular template — they
resolve through the global stylesheet:

```html
<div class="border border-border-muted bg-elev p-4 text-accent">…</div>
```

Component-scoped `styles: [...]` also work; don't duplicate tokens there.

## What to keep in Astro

Anything purely presentational (`Hero`, `About`, `Skills`, `ProjectCard`, …)
stays in Astro. Move to Angular only when you need:

- Stateful UI that survives navigation (carts, editors, multi-step wizards)
- Real-time data (WebSockets, SSE) bound to many DOM nodes
- Complex form handling with reactive validation
- Charting/animation libraries that expect an Angular context

## Gotchas

- Angular bumps the client payload — **never** set `client:load` on an
  Angular island unless it's above the fold and genuinely needed on first
  paint.
- Angular's zone.js can conflict with Astro's islands on older versions;
  `@analogjs/astro-angular` 1.x targets Angular 18+ with zoneless signals —
  stay on that track.
- The Cloudflare Pages workflow already runs `bun run build`, which invokes
  `astro build` — no extra Angular-specific step is required.
