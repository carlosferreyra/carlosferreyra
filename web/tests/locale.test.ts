import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { alternateLocaleHref, localePath } from '../src/i18n';
import { detectBrowserLocale, selectLocale } from '../src/scripts/locale';

describe('locale selection', () => {
	it('selects Spanish from Spanish browser languages', () => {
		assert.equal(detectBrowserLocale(['es']), 'es');
		assert.equal(detectBrowserLocale(['es-AR', 'en-US']), 'es');
	});

	it('selects the first supported browser language', () => {
		assert.equal(detectBrowserLocale(['fr-FR', 'es-ES', 'en-US']), 'es');
		assert.equal(detectBrowserLocale(['en-US', 'es-ES']), 'en');
	});

	it('falls back to English', () => {
		assert.equal(detectBrowserLocale([]), 'en');
		assert.equal(detectBrowserLocale(['fr-FR']), 'en');
	});

	it('gives a saved preference priority', () => {
		assert.equal(selectLocale('en', ['es-AR']), 'en');
		assert.equal(selectLocale('es', ['en-US']), 'es');
		assert.equal(selectLocale('fr', ['es-AR']), 'es');
	});
});

describe('locale URLs', () => {
	it('prefixes both locale roots', () => {
		assert.equal(localePath('en'), '/en/');
		assert.equal(localePath('es'), '/es/');
	});

	it('switches between equivalent localized paths', () => {
		assert.equal(alternateLocaleHref('en', '/en/'), '/es/');
		assert.equal(alternateLocaleHref('es', '/es/'), '/en/');
		assert.equal(alternateLocaleHref('en', '/en/projects'), '/es/projects');
	});
});
