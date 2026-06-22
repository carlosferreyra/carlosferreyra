export type GitHubMetadata = {
	url: string;
	demo?: string;
	thumbnail?: string;
	tags: string[];
};

type RepositoryResponse = {
	data?: {
		repository: {
			url: string;
			homepageUrl: string | null;
			openGraphImageUrl: string;
			repositoryTopics: { nodes: Array<{ topic: { name: string } }> };
		} | null;
	};
};

const repositoryPath = (url: string): [string, string] | undefined => {
	const match = /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/?$/.exec(url);
	return match ? [match[1], match[2]] : undefined;
};

export async function githubMetadata(url: string): Promise<GitHubMetadata | undefined> {
	const path = repositoryPath(url);
	const token = process.env.GITHUB_TOKEN;
	if (!path || !token) return undefined;

	const [owner, name] = path;
	const response = await fetch('https://api.github.com/graphql', {
		method: 'POST',
		headers: {
			accept: 'application/vnd.github+json',
			authorization: `Bearer ${token}`,
			'content-type': 'application/json',
			'user-agent': 'carlosferreyra-portfolio',
		},
		body: JSON.stringify({
			query: `query($owner: String!, $name: String!) {
				repository(owner: $owner, name: $name) {
					url
					homepageUrl
					openGraphImageUrl
					repositoryTopics(first: 20) { nodes { topic { name } } }
				}
			}`,
			variables: { owner, name },
		}),
	});

	if (!response.ok) throw new Error(`GitHub metadata request failed (${response.status})`);
	const repository = ((await response.json()) as RepositoryResponse).data?.repository;
	if (!repository) return undefined;

	return {
		url: repository.url,
		demo: repository.homepageUrl ?? undefined,
		thumbnail: repository.openGraphImageUrl,
		tags: repository.repositoryTopics.nodes.map(({ topic }) => topic.name),
	};
}
