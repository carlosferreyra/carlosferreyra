// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
	site: 'https://carlosferreyra.com.ar',
	output: 'static',
	trailingSlash: 'ignore',
	i18n: {
		defaultLocale: 'en',
		locales: ['en', 'es'],
		routing: {
			prefixDefaultLocale: false,
			redirectToDefaultLocale: false,
		},
	},
	vite: {
		// Cast: @tailwindcss/vite builds against a newer Vite than Astro pins; plugin
		// shape is compatible at runtime, the mismatch is only in type-level generics.
		plugins: [/** @type {any} */ (tailwindcss())],
	},
});
