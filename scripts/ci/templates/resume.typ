#import "@preview/silver-dev-cv:1.0.2": *

#show: cv.with(
  font-type: "PT Serif",
  continue-header: "false",
  name: "Carlos Ferreyra",
  address: "San Francisco, CA, USA",
  lastupdated: "true",
  pagecount: "true",
  date: "2025-07-08",
  contacts: (
    (text: "LinkedIn", link: "https://www.linkedin.com/in/carlosferreyra"),
    (text: "Github", link: "https://www.github.com/carlosferreyra"),
    (text: "carlos.ferreyra@example.com", link: "mailto:carlos.ferreyra@example.com"),
  ),
)



// about
#section[About Me]
#descript[I'm a full-stack software engineer with expertise in Python, TypeScript, and cloud infrastructure. I love building scalable systems and leading engineering teams to deliver high-quality products.]

#sectionsep

// Experience
#section("Experience")
#job(
  position: "Senior Software Engineer",
  institution: [TechCorp],
  location: "San Francisco, CA",
  date: "2022-2025",
  description: [
    - Led development of microservices architecture serving 10M+ users with 99.9% uptime.
    - Mentored a team of 6 engineers and established code review and testing standards.
    - Reduced deployment time by 80% through implementation of CI/CD pipelines and infrastructure as code.
  ],
)

#job(
  position: "Software Engineer",
  institution: [StartupXYZ],
  location: "Remote",
  date: "2020-2022",
  description: [
    - Built full-stack web applications using React, Node.js, and PostgreSQL.
    - Implemented real-time features using WebSockets that increased user engagement by 40%.
  ],
)


#section("Skills")
#oneline-title-item(
  title: "Skills",
  content: [Python, TypeScript, React, Node.js, PostgreSQL, AWS, Docker, Kubernetes],
)

#sectionsep

#section("Education")
#education(
  institution: [University of Buenos Aires],
  major: [Software Engineering],
  date: "2015-2018",
  location: "Argentina",
)

#set document(author: "silver", title: "Silver CV Template")