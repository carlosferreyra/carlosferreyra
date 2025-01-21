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



const projectsTemplate = await fs.readFile('./src/projects.js.tpl', { encoding: 'utf-8' })
const projects = [];
const user_repositories = await githubApi(PLACEHOLDERS.USER_API_URL.replace('<user>', PLACEHOLDERS.USER));
const public_repositories = user_repositories.filter(repo => !repo.private);
for (const repo of public_repositories) {
  projects.push({
    name: repo.name,
    img: await getSocialPreview(repo,PLACEHOLDERS.USER),
    description: repo.description,
    stack: repo.topics,
    demo: repo.homepage,
  })
  
}
const orgs = await githubApi(PLACEHOLDERS.USER_ORGS);
const orgs_login = orgs.map(org => org.login)
for (const org of orgs_login) {
  
  const url = PLACEHOLDERS.ORGS_API_URL.replace('<org>', org);
  const org_repositories = await githubApi(url);
  const publicRepos = org_repositories.filter(repo => !repo.private);
  
  for (const repo of publicRepos) {
    const contributors = await githubApi(repo.contributors_url);
    if (contributors.some(contributor => contributor.login === PLACEHOLDERS.USER)) {
        
        projects.push({
            name: repo.name,
            img: await getSocialPreview(repo,org), 
            description: repo.description,
            stack: repo.topics,
            demo: repo.homepage,
            repo: repo.html_url
        });   
    }
  }
}

// Format projects array as pretty JSON string
const projectsJson = JSON.stringify(projects, null, 2);

// Replace template placeholder and format output
const outputContent = projectsTemplate.replace('%{{PROJECTS}}', projectsJson);

// Write to projects.js
await fs.writeFile('./src/projects.js', outputContent, 'utf-8');



// window.addEventListener("load", () => {
//     loadProjects()})


// codigo de Lucas

import { projects as proyectList } from "./projects.js";

const projectsDiv = document.getElementById("projects-list")

const loadMoreButton = document.getElementById("loadMoreProjects")

let projectsToShow = proyectList.slice(0, 4)

function loadProjects() {
  let html = ""

  projectsToShow.forEach((project) => {
    let stack = ""
    project.stack.forEach((tech) => {
      stack += `<span>${tech}</span> `
    })

    html += `
        <article class="project">        
          <div>
            <div class="project__img">
             <a href="${project.demo && project.demo}">
              <img loading="lazy" src="${project.img}" alt="${project.name}">
             </a>
            </div>
            <div class="project__info">
                  <h3>${project.name}</h3>
                  <div class="project__stack">
                  ${stack}
                  </div>
                  <p class="project__description">${project.description.replace(
                    /(?:\r\n|\r|\n)/g,
                    "<br>"
                  )}</p>
              </div>
          </div>
          <div class="project__links">
              ${project.demo ? `<a href="${project.demo}">Demo</a>` : ""}
              ${project.repo ? `<a href="${project.repo}">Code</a>` : ""}
          </div>
        </article>
    `
  })

  projectsDiv.innerHTML = html
}

loadProjects()

loadMoreButton.addEventListener("click", () => {
  projectsToShow = projects
  loadProjects()
  loadMoreButton.style = "display:none"
})
