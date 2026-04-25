/**
 * Inline <head> script — runs before first paint to apply the resolved theme
 * and the user's preference, eliminating FOUC.
 *
 * Storage contract (see web/src/scripts/theme.ts for the typed runtime helpers):
 *   - localStorage['theme'] === 'light'  → user pinned light
 *   - localStorage['theme'] === 'dark'   → user pinned dark
 *   - absent / anything else             → follow system (prefers-color-scheme)
 *
 * Two attributes land on <html>:
 *   - data-theme       resolved value ('light' | 'dark') — read by global.css
 *   - data-theme-pref  user preference ('light' | 'dark' | 'system') — read by ThemePicker
 */
export const themeInit = `
	(function () {
		var root = document.documentElement;
		try {
			var stored = localStorage.getItem('theme');
			var pref = stored === 'light' || stored === 'dark' ? stored : 'system';
			var resolved = pref === 'system'
				? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
				: pref;
			root.setAttribute('data-theme', resolved);
			root.setAttribute('data-theme-pref', pref);
		} catch (e) {
			root.setAttribute('data-theme', 'dark');
			root.setAttribute('data-theme-pref', 'system');
		}
	})();
`;
