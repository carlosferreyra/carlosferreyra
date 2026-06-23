import catalog from '../../../resume.json';
import portfolio from '@data/github-portfolio.json';

const PROFILE = 'default';
const profile = catalog.profiles[PROFILE];

type Labeled = { labels: string[] };
const select = <T extends Labeled>(items: T[]): Omit<T, 'labels'>[] =>
	items
		.filter((item) => item.labels.includes(PROFILE))
		.map(({ labels: _labels, ...item }) => item);

export type Link = { id: string; label: string; url: string };
export type Project = {
	name: string;
	nameWithOwner?: string;
	owner?: string;
	description: string;
	url?: string;
	demo?: string;
	thumbnail?: string;
	tags?: string[];
	stars?: number;
	pushedAt?: string;
	updatedAt?: string;
	primaryLanguage?: string;
};
export type Experience = { title: string; company: string; period: string; highlights: string[] };
export type Education = { degree: string; institution: string; location: string; period: string; highlights: string[] };
export type Certification = { name: string; year: number; url: string };
export type SkillGroup = { category: string; items: string[] };

const nested = <T extends Labeled & { highlights: Array<Labeled & { text: string }> }>(items: T[]) =>
	select(items).map((item) => ({
		...item,
		highlights: item.highlights
			.filter((highlight) => highlight.labels.includes(PROFILE))
			.map((highlight) => highlight.text),
	}));

export const resume = {
	personalInfo: { ...catalog.personalInfo, title: profile.title, summary: profile.summary },
	githubUsername: catalog.githubUsername,
	links: select(catalog.links) as Link[],
	skills: select(catalog.skills) as SkillGroup[],
	experience: nested(catalog.experience) as Experience[],
	education: nested(catalog.education) as Education[],
	certifications: select(catalog.certifications) as Certification[],
	projects: portfolio.projects as Project[],
};

export type Resume = typeof resume;

export function linkById(id: string): Link | undefined {
	return resume.links.find((link) => link.id === id);
}
