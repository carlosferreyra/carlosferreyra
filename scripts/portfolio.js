// Description: This file contains the main logic for the project.
import { promises as fs } from 'fs';
import { PLACEHOLDERS, REPO_FILTERS, createHeaders } from './constants.js';

const { GH_TOKEN, GITHUB_TOKEN } = process.env;

if (!GH_TOKEN && !GITHUB_TOKEN) {
	console.error('at least GH_TOKEN or GITHUB_TOKEN is required');
	process.exit(1);
}

const token = GH_TOKEN || GITHUB_TOKEN;
const header = createHeaders(token);

// Helper Functions
const checkUrlStatus = async (url) => {
	try {
		const response = await fetch(url, { method: 'HEAD' });
		return response.status === 200;
	} catch (error) {
		console.error(`Failed to check URL ${url}:`, error);
		return false;
	}
};

const githubApi = async (url) => {
	const response = await fetch(url, {
		headers: url.includes('graphql') ? header.graphql : header.rest,
	});
	return response.json();
};

const getSocialPreview = async (repo, owner) => {
	const query = `query {
    repository(owner: "${owner}", name: "${repo.name}") {
      openGraphImageUrl
    }
  }`;

	try {
		const graphqlResponse = await fetch(PLACEHOLDERS.GRAPHQL_API, {
			method: 'POST',
			headers: header.graphql,
			body: JSON.stringify({ query }),
		});

		const graphqlData = await graphqlResponse.json();
		if (graphqlData.errors) {
			console.error(`Error fetching preview for ${owner}/${repo.name}:`, graphqlData.errors);
			return null;
		}
		return graphqlData.data.repository.openGraphImageUrl;
	} catch (error) {
		console.error(`Failed to fetch preview for ${owner}/${repo.name}:`, error);
		return null;
	}
};

const processRepository = async (repo, owner) => {
	const isDemoAvailable = await checkUrlStatus(repo.homepage);
	if (isDemoAvailable) {
		return {
			repo: repo.html_url,
			name: repo.name,
			img: await getSocialPreview(repo, owner),
			description: repo.description,
			stack: repo.topics,
			demo: repo.homepage,
		};
	}
	return null;
};

const filterRepositories = (repositories, owner) => {
	return repositories
		.filter((repo) => REPO_FILTERS.skipOwn(repo, owner))
		.filter(REPO_FILTERS.isPublic)
		.filter(REPO_FILTERS.hasDemo)
		.filter(REPO_FILTERS.skipSpecial)
		.filter(REPO_FILTERS.skipForks)
		.filter((repo) => REPO_FILTERS.notBlacklisted(repo, owner));
};

const getOrgRepositories = async (org) => {
	const url = PLACEHOLDERS.ORGS_API_URL.replace('<org>', org);
	const repositories = await githubApi(url);
	const filtered = filterRepositories(repositories, org);
	const projects = [];

	for (const repo of filtered) {
		const contributors = await githubApi(repo.contributors_url);
		if (contributors.some((contributor) => contributor.login === PLACEHOLDERS.USER)) {
			const project = await processRepository(repo, org);
			if (project) projects.push(project);
		}
	}

	return projects;
};

// Main execution
const main = async () => {
	const projects = [];

	// Fetch user repositories
	const userRepos = await githubApi(PLACEHOLDERS.USER_API_URL.replace('<user>', PLACEHOLDERS.USER));
	const filteredUserRepos = filterRepositories(userRepos, PLACEHOLDERS.USER);

	// Process user repositories
	for (const repo of filteredUserRepos) {
		const project = await processRepository(repo, PLACEHOLDERS.USER);
		if (project) projects.push(project);
	}

	// Fetch and process org repositories
	const orgs = await githubApi(PLACEHOLDERS.USER_ORGS);
	const orgProjects = await Promise.all(orgs.map((org) => getOrgRepositories(org.login)));
	projects.push(...orgProjects.flat());

	// Format and write projects to file
	const projectsJson = JSON.stringify(projects, null, 2);
	const head =
		'// IMPORTANT: This file is auto-generated. DO NOT EDIT MANUALLY.\n\nconst projects = ';
	const foot = '\nexport default projects;';
	await fs.writeFile('./src/projects.js', head + projectsJson + foot);
};

main().catch((error) => {
	console.error('Error in main execution:', error);
	process.exit(1);
});
