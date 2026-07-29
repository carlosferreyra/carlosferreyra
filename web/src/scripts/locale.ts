import type { Locale } from '~/i18n';

export const LOCALE_STORAGE_KEY = 'locale';

export function isLocale(value: string | null): value is Locale {
	return value === 'en' || value === 'es';
}

export function detectBrowserLocale(languages: readonly string[]): Locale {
	for (const language of languages) {
		const primary = language.toLowerCase().split('-')[0];
		if (primary === 'en' || primary === 'es') return primary;
	}
	return 'en';
}

export function selectLocale(
	savedLocale: string | null,
	languages: readonly string[],
): Locale {
	return isLocale(savedLocale) ? savedLocale : detectBrowserLocale(languages);
}

export function getSavedLocale(): Locale | null {
	try {
		const savedLocale = localStorage.getItem(LOCALE_STORAGE_KEY);
		return isLocale(savedLocale) ? savedLocale : null;
	} catch {
		return null;
	}
}

export function saveLocale(locale: Locale): void {
	try {
		localStorage.setItem(LOCALE_STORAGE_KEY, locale);
	} catch {
		/* private mode / quota — navigation still works */
	}
}
