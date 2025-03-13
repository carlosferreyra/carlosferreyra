import fs from 'fs/promises';

const PLACEHOLDERS = {
	USER: await fs
		.readFile('./package.json', { encoding: 'utf-8' })
		.then((data) => JSON.parse(data).name),
	USER_ORGS: 'https://api.github.com/user/orgs',
	USER_API_URL: 'https://api.github.com/users/<user>/repos',
	ORGS_API_URL: 'https://api.github.com/orgs/<org>/repos',
	REPOS: '%{{REPOS}}',
	PROJECTS: '%{{PROJECTS}}',
	GRAPHQL_API: 'https://api.github.com/graphql',
};

// List of repositories to ignore in the format "owner/repo"
const IGNORED = [
	'carlosferreyra/carlosferreyra', // Example: Ignore the profile
	'carlosferreyra/Portfolio', // Example: Ignore the portfolio
	// repository
	// Add more repositories to ignore here
];

const REPO_FILTERS = {
	skipOwn: (repo, owner) => repo.name !== owner,
	isPublic: (repo) => !repo.private,
	hasDemo: (repo) => repo.homepage !== null && repo.homepage !== '',
	skipSpecial: (repo) => !repo.name.startsWith('.'),
	notBlacklisted: (repo, owner) => !IGNORED.includes(`${owner}/${repo.name}`),
	skipForks: (repo) => !repo.fork,
};

const createHeaders = (token) => ({
	rest: {
		'Authorization': `Bearer ${token}`,
		'Content-Type': 'application/json',
	},
	graphql: {
		'Authorization': `Bearer ${token}`,
		'Content-Type': 'application/json',
		'Accept': 'application/vnd.github.v4+json',
	},
});

export { createHeaders, IGNORED, PLACEHOLDERS, REPO_FILTERS };
