export type Locale = 'en' | 'es';

export type Dictionary = {
	nav: {
		about: string;
		skills: string;
		experience: string;
		projects: string;
		certifications: string;
		contact: string;
	};
	hero: {
		prompt: string;
		tagline: string;
		cta: { projects: string; contact: string };
	};
	sections: {
		about: string;
		skills: string;
		experience: string;
		projects: string;
		certifications: string;
		contact: string;
	};
	projects: {
		viewCode: string;
		viewDemo: string;
		noThumbnail: string;
	};
	contact: {
		intro: string;
	};
	footer: {
		builtWith: string;
		rights: string;
	};
	meta: {
		langLabel: string;
		langSwitchTitle: string;
		themeToggleTitle: string;
	};
};
