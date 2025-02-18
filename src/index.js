import projects from "./projects.js"

const projectsDiv = document.getElementById("projects-list")

const loadMoreButton = document.getElementById("loadMoreProjects")

let projectsToShow = projects.slice(0, 4)
if (projectsToShow.length === projects.length || projects.length < 5) {
  loadMoreButton.style = "display:none"
}

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