import { en } from './en';
import { es } from './es';
import type { Dictionary, Locale } from './types';

export const dictionaries: Record<Locale, Dictionary> = { en, es };

export const DEFAULT_LOCALE: Locale = 'en';

export function t(locale: Locale): Dictionary {
	return dictionaries[locale] ?? dictionaries[DEFAULT_LOCALE];
}

/**
 * Return the root path for a given locale — `/` for the default, `/<locale>/` for others.
 * Keeps URL composition consistent across components.
 */
export function localePath(locale: Locale, path = ''): string {
	const suffix = path.startsWith('/') ? path : `/${path}`;
	const trimmed = suffix === '/' ? '' : suffix;
	return locale === DEFAULT_LOCALE ? `${trimmed || '/'}` : `/${locale}${trimmed}`;
}

/**
 * Map current locale to the equivalent URL in the alternate locale, preserving the section hash.
 */
export function alternateLocaleHref(current: Locale, pathname: string): string {
	const other: Locale = current === 'en' ? 'es' : 'en';
	// Strip any existing /es prefix, keep only the trailing section (home has none).
	const clean = pathname.replace(/^\/es\/?/, '/').replace(/\/+$/, '') || '/';
	return localePath(other, clean);
}

export type { Dictionary, Locale };
