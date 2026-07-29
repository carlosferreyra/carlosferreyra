import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { nextThemePref } from '../src/scripts/theme';

describe('nextThemePref', () => {
	it('cycles system → light → dark → system', () => {
		assert.equal(nextThemePref('system'), 'light');
		assert.equal(nextThemePref('light'), 'dark');
		assert.equal(nextThemePref('dark'), 'system');
	});
});
