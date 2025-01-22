// Description: This file contains the main logic for the project.
// Import the required modules/functions/packages
import { promises as fs } from 'fs';

import { PLACEHOLDERS } from './constants.js';


const {
  GH_ACCESS_TOKEN,
  GITHUB_TOKEN,
} = process.env;




// Constants/Variables
if (!GH_ACCESS_TOKEN && !GITHUB_TOKEN) {
  console.error('at least GH_ACCESS_TOKEN or GITHUB_TOKEN is required');
  process.exit(1);
}
const token = GH_ACCESS_TOKEN || GITHUB_TOKEN;
const header = {
    rest: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    graphql: {
        Authorization: `Bearer ${token}`, 
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v4+json',
    }
};

// Functions
const githubApi = async (url) => {
  const response = await fetch(url,
    {
      headers: url.includes('graphql') ? header.graphql : header.rest,
    }
  )
const repositories = await response.json()
return repositories
}

const getSocialPreview = async (repo, owner) => {
  const query = `query { 
    repository(owner: "${owner}", name: "${repo.name}") { 
      openGraphImageUrl 
    }
  }`;

  try {
    const graphqlResponse = await fetch('https://api.github.com/graphql', {
      method: 'POST',
      headers: header.graphql,
      body: JSON.stringify({ query })
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
}



// Main
const projects = [];
const user_repositories = await githubApi(PLACEHOLDERS.USER_API_URL.replace('<user>', PLACEHOLDERS.USER));
const public_repositories = user_repositories.filter(repo => !repo.private);
const filtered_repos = public_repositories
    .filter(repo => repo.homepage !== null && repo.homepage !== '')
    .filter(repo => !repo.name.startsWith(".") && !repo.name === PLACEHOLDERS.USER)

for (const repo of filtered_repos) {
  
  // skip all repos without a demo
  if (repo.homepage !== null) {
    projects.push({
    repo: repo.html_url,
    name: repo.name,
    img: await getSocialPreview(repo,PLACEHOLDERS.USER),
    description: repo.description,
    stack: repo.topics,
    demo: repo.homepage,
  })  
  }
}
const orgs = await githubApi(PLACEHOLDERS.USER_ORGS);
const orgs_login = orgs.map(org => org.login)
for (const org of orgs_login) {
  
  const url = PLACEHOLDERS.ORGS_API_URL.replace('<org>', org);
  const org_repositories = await githubApi(url);
  const filtered_repos = org_repositories
  .filter(repo => repo.homepage !== null && repo.homepage !== '')
  .filter(repo => !repo.name.startsWith("."))
  
  for (const repo of filtered_repos) {
    const contributors = await githubApi(repo.contributors_url);
    if (contributors.some(contributor => contributor.login === PLACEHOLDERS.USER)) {
    projects.push({
    repo: repo.html_url,
    name: repo.name,
    img: await getSocialPreview(repo,org),
    description: repo.description,
    stack: repo.topics,
    demo: repo.homepage,
      })  
    }
  }
}

// Format projects array as pretty JSON string
const projectsJson = JSON.stringify(projects, null, 2);

// Write to projects.js
const head = 'const projects = '
const foot = '\nexport default projects;'
await fs.writeFile('./src/projects.js', head + projectsJson+ foot);



// window.addEventListener("load", () => {
//     loadProjects()})


