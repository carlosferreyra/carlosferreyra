// Description: This file contains the main logic for the project.
import { promises as fs } from 'fs';
import { PLACEHOLDERS, REPO_FILTERS, createHeaders } from './constants.js';

const { GH_TOKEN } = process.env;

if (!GH_TOKEN) {
	console.error('GH_TOKEN (Personal Access Token) is required');
	process.exit(1);
}

const header = createHeaders(GH_TOKEN);

// Helper Functions
// IMPROVEMENT 2: Consider adding retry logic with exponential backoff
// for better reliability when checking URL status
const checkUrlStatus = async (url) => {
	try {
		const response = await fetch(url, { method: 'HEAD' });
		return response.status === 200;
	} catch (error) {
		console.error(`Failed to check URL ${url}:`, error);
		return false;
	}
};

// IMPROVEMENT 3: Add rate limiting handling and pagination support
// for better GitHub API interaction
const githubApi = async (url) => {
	const response = await fetch(url, {
		headers: url.includes('graphql') ? header.graphql : header.rest,
	});
	// IMPROVEMENT 4: Check response status and handle rate limits
	// if (response.status === 403) handle rate limiting
	return response.json();
};

// IMPROVEMENT 5: Consider caching social preview URLs to reduce API calls
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

// IMPROVEMENT 6: Consider adding fallback image URL when social preview is not available
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

// IMPROVEMENT 7: Consider making filter criteria configurable via environment variables
const filterRepositories = (repositories, owner) => {
	return repositories
		.filter((repo) => REPO_FILTERS.skipOwn(repo, owner))
		.filter(REPO_FILTERS.isPublic)
		.filter(REPO_FILTERS.hasDemo)
		.filter(REPO_FILTERS.skipSpecial)
		.filter(REPO_FILTERS.skipForks)
		.filter((repo) => REPO_FILTERS.notBlacklisted(repo, owner));
};

// IMPROVEMENT 8: Add pagination support for large organizations
const getOrgRepositories = async (org) => {
	const url = PLACEHOLDERS.ORGS_API_URL.replace('<org>', org);
	const repositories = await githubApi(url);
	const filtered = filterRepositories(repositories, org);
	const projects = [];

	for (const repo of filtered) {
		const contributors = await githubApi(repo.contributors_url);
		// IMPROVEMENT 9: Consider caching contributor data to reduce API calls
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
	// IMPROVEMENT 10: Consider implementing concurrent processing with rate limiting
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

// IMPROVEMENT 11: Add proper error handling and recovery
main().catch((error) => {
	console.error('Error in main execution:', error);
	process.exit(1);
});
