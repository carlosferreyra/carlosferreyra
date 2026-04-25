/**
 * Theme runtime — used by ThemePicker.astro on the client.
 * Pre-paint logic (no FOUC) lives in theme-init.ts as an inline string.
 *
 * Preference model:
 *   localStorage['theme'] is set ONLY when the user pins a value. Absence of
 *   the key means "follow the OS". This way users who never click the picker
 *   leave no trace, and clearing site data resets cleanly to system.
 */

export type ThemePref = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

const STORAGE_KEY = 'theme';

function systemMql(): MediaQueryList | null {
	if (typeof window === 'undefined' || !window.matchMedia) return null;
	return window.matchMedia('(prefers-color-scheme: dark)');
}

export function getPref(): ThemePref {
	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		return stored === 'light' || stored === 'dark' ? stored : 'system';
	} catch {
		return 'system';
	}
}

export function resolve(pref: ThemePref): ResolvedTheme {
	if (pref !== 'system') return pref;
	return systemMql()?.matches ? 'dark' : 'light';
}

export function apply(pref: ThemePref): void {
	const resolved = resolve(pref);
	const root = document.documentElement;
	root.setAttribute('data-theme', resolved);
	root.setAttribute('data-theme-pref', pref);
	try {
		if (pref === 'system') localStorage.removeItem(STORAGE_KEY);
		else localStorage.setItem(STORAGE_KEY, pref);
	} catch {
		/* private mode / quota — ignore */
	}
}

/**
 * Re-resolve when the OS theme changes — only matters when pref is 'system',
 * but cheap to keep wired regardless. Returns an unsubscribe fn.
 */
export function watchSystem(): () => void {
	const mql = systemMql();
	if (!mql) return () => {};
	const onChange = () => {
		if (getPref() === 'system') apply('system');
	};
	mql.addEventListener('change', onChange);
	return () => mql.removeEventListener('change', onChange);
}

/**
 * Sync across tabs: if another tab changes localStorage, mirror it here.
 * Returns an unsubscribe fn.
 */
export function watchStorage(): () => void {
	const onStorage = (e: StorageEvent) => {
		if (e.key === STORAGE_KEY || e.key === null) apply(getPref());
	};
	window.addEventListener('storage', onStorage);
	return () => window.removeEventListener('storage', onStorage);
}
