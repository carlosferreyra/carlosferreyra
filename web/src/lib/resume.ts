import resumesData from '@data/resumes.json';

// The public site renders the `carlos-ferreyra` combo (see data/dev.json) —
// resolved by scripts/resume_build.py into data/resumes.json. Selecting it here
// keeps git as the single source of truth (no hand-edited generated contract).
const PUBLIC_SLUG = 'carlos-ferreyra';
const resumeData = resumesData.resumes.find((r) => r.slug === PUBLIC_SLUG);
if (!resumeData) {
	throw new Error(`resumes.json missing required resume slug "${PUBLIC_SLUG}"`);
}

export type Link = {
	id: string;
	label: string;
	url: string;
};

export type Project = {
	name: string;
	description: string;
	url?: string;
	demo?: string;
	thumbnail?: string;
	tags?: string[];
};

export type Experience = {
	title: string;
	company: string;
	period: string;
	highlights: string[];
	tags?: string[];
};

export type Education = {
	degree: string;
	institution: string;
	location: string;
	period: string;
	highlights: string[];
	tags?: string[];
};

export type Certification = {
	name: string;
	year: number;
	url: string;
	tags?: string[];
};

export type SkillGroup = {
	category: string;
	items: string[];
	tags?: string[];
};

export type Resume = NonNullable<typeof resumeData>;

export const resume = resumeData as unknown as {
	personalInfo: {
		name: string;
		title: string;
		email: string;
		location: string;
		summary: string;
	};
	githubUsername: string;
	links: Link[];
	skills: SkillGroup[];
	experience: Experience[];
	education: Education[];
	certifications: Certification[];
	projects: Project[];
};

export function linkById(id: string): Link | undefined {
	return resume.links.find((l) => l.id === id);
}
