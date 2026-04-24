/**
 * Inline script loaded in <head> before paint to set data-theme before first paint.
 * Keeps the site FOUC-free when toggling light/dark.
 */
export const themeInit = `
	(function(){
		try {
			var stored = localStorage.getItem('theme');
			var prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
			var theme = stored || (prefersLight ? 'light' : 'dark');
			document.documentElement.setAttribute('data-theme', theme);
		} catch (e) {
			document.documentElement.setAttribute('data-theme', 'dark');
		}
	})();
`;
