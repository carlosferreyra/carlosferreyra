import { en } from './en';
import { es } from './es';
import type { Dictionary, Locale } from './types';

export const dictionaries: Record<Locale, Dictionary> = { en, es };

export const DEFAULT_LOCALE: Locale = 'en';

export function t(locale: Locale): Dictionary {
	return dictionaries[locale] ?? dictionaries[DEFAULT_LOCALE];
}

/**
 * Return a locale-prefixed path.
 */
export function localePath(locale: Locale, path = ''): string {
	const suffix = path.startsWith('/') ? path : `/${path}`;
	return `/${locale}${suffix}`;
}

/**
 * Map current locale to the equivalent URL in the alternate locale, preserving the section hash.
 */
export function alternateLocaleHref(current: Locale, pathname: string): string {
	const other: Locale = current === 'en' ? 'es' : 'en';
	const clean = pathname.replace(/^\/(?:en|es)(?=\/|$)/, '') || '/';
	return localePath(other, clean);
}

export type { Dictionary, Locale };
