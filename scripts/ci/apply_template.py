# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import json
import pathlib
from datetime import datetime
from typing import Any


def load_data() -> dict:
    """Load data from JSON file."""
    data_path = pathlib.Path(__file__).parent / "data" / "data.json"
    with open(data_path, "r") as f:
        return json.load(f)


class TypstCVGenerator:
    """Generator class that creates Typst CV code using Python functions that map to Typst functions."""

    def __init__(self):
        self.content: list[str] = []

    def import_package(self, package: str, version: str) -> None:
        """Import the CV package."""
        self.content.append(f'#import "@preview/{package}:{version}": *')
        self.content.append("")

    def cv_header(self, font_type: str = "PT Serif", continue_header: str = "false",
                  name: str = "", address: str = "", lastupdated: str = "true",
                  pagecount: str = "true", date: str = "", contacts: list[dict[str, str]]| None = None) -> None:
        """Create the CV header with show rule."""
        contacts = contacts or []

        self.content.append("#show: cv.with(")
        self.content.append(f'  font-type: "{font_type}",')
        self.content.append(f'  continue-header: "{continue_header}",')
        self.content.append(f'  name: "{name}",')
        self.content.append(f'  address: "{address}",')
        self.content.append(f'  lastupdated: "{lastupdated}",')
        self.content.append(f'  pagecount: "{pagecount}",')
        self.content.append(f'  date: "{date}",')
        self.content.append("  contacts: (")

        for contact in contacts:
            self.content.append(f'    (text: "{contact["text"]}", link: "{contact["link"]}"),')

        self.content.append("  ),")
        self.content.append(")")
        self.content.append("")

    def add_section(self, name: str, use_brackets: bool = False) -> None:
        """Add a new section with the given name."""
        if use_brackets:
            self.content.append(f'#section[{name}]')
        else:
            self.content.append(f'#section("{name}")')

    def add_sectionsep(self) -> None:
        """Add a section separator."""
        self.content.append("#sectionsep")
        self.content.append("")

    def add_oneline_title_item(self, title: str, content: str) -> None:
        """Add a one-line item with title and content."""
        self.content.append("#oneline-title-item(")
        self.content.append(f'  title: "{title}",')
        self.content.append(f'  content: [{content}],')
        self.content.append(")")

    def add_oneline_two(self, entry1: str, entry2: str) -> None:
        """Add a one-line item with two entries, aligned left and right."""
        self.content.append("#oneline-two(")
        self.content.append(f'  entry1: "{entry1}",')
        self.content.append(f'  entry2: "{entry2}",')
        self.content.append(")")

    def add_descript(self, description: str) -> None:
        """Add a description for self-introduction."""
        self.content.append(f"#descript[{description}]")
        self.content.append("")

    def add_award(self, award: str, date: str, institution: str) -> None:
        """Add an award entry."""
        self.content.append("#award(")
        self.content.append(f'  award: "{award}",')
        self.content.append(f'  date: "{date}",')
        self.content.append(f'  institution: "{institution}",')
        self.content.append(")")

    def add_education(self, institution: str, major: str, date: str,
                     location: str, core_modules: str | None = None) -> None:
        """Add an education experience."""
        self.content.append("#education(")
        self.content.append(f'  institution: [{institution}],')
        self.content.append(f'  major: [{major}],')
        self.content.append(f'  date: "{date}",')
        self.content.append(f'  location: "{location}",')
        if core_modules:
            self.content.append(f'  core-modules: "{core_modules}",')
        self.content.append(")")

    def add_job(self, position: str, institution: str, location: str,
               date: str, description: list[str] | None = None) -> None:
        """Add a job experience."""
        self.content.append("#job(")
        self.content.append(f'  position: "{position}",')
        self.content.append(f'  institution: [{institution}],')
        self.content.append(f'  location: "{location}",')
        self.content.append(f'  date: "{date}",')

        if description:
            self.content.append("  description: [")
            for desc in description:
                self.content.append(f"    - {desc}")
            self.content.append("  ],")

        self.content.append(")")
        self.content.append("")

    def add_project(self, title: str, date: str, description: str) -> None:
        """Add a project entry using the proper #project function."""
        self.content.append("#project(")
        self.content.append(f'    title: [{title}],')
        self.content.append(f'    date: [{date}],')
        self.content.append(f'    description: [{description}]')
        self.content.append(")")
        self.content.append("")

    def add_twoline_item(self, entry1: str, entry2: str, entry3: str, entry4: str) -> None:
        """Add a two-line item."""
        self.content.append("#twoline-item(")
        self.content.append(f'  entry1: "{entry1}",')
        self.content.append(f'  entry2: "{entry2}",')
        self.content.append(f'  entry3: "{entry3}",')
        self.content.append(f'  entry4: "{entry4}",')
        self.content.append(")")

    def add_document_metadata(self, author: str = "silver", title: str = "Silver CV Template") -> None:
        """Add document metadata."""
        self.content.append(f'#set document(author: "{author}", title: "{title}")')

    def add_comment(self, comment: str) -> None:
        """Add a comment to the document."""
        self.content.append(f"// {comment}")

    def add_empty_line(self) -> None:
        """Add an empty line."""
        self.content.append("")

    def get_content(self) -> str:
        """Get the generated Typst content as a string."""
        return "\n".join(self.content)


def generate_cv_from_data(data: dict[str, Any]) -> str:
    """Generate the CV content by mapping JSON data to Typst functions."""
    cv = TypstCVGenerator()

    # Import the CV package
    cv.import_package("silver-dev-cv", "1.0.2")

    # Create CV header with personal info
    personal_info = data.get("personal_info", {})
    # Use current date instead of the date from JSON
    current_date = datetime.now().strftime("%Y-%m-%d")
    cv.cv_header(
        name=personal_info.get("name", ""),
        address=personal_info.get("address", ""),
        date=current_date,
        contacts=personal_info.get("contacts", [])
    )

    # About Section
    if data.get("about"):
        cv.add_empty_line()
        cv.add_empty_line()
        cv.add_comment("about")
        cv.add_section("About Me", use_brackets=True)
        cv.add_descript(data["about"])
        cv.add_sectionsep()

    # Experience Section
    if data.get("experience"):
        cv.add_comment("Experience")
        cv.add_section("Experience")
        for job in data["experience"]:
            cv.add_job(
                position=job.get("position", ""),
                institution=job.get("institution", ""),
                location=job.get("location", ""),
                date=job.get("date", ""),
                description=job.get("description", [])
            )
        cv.add_empty_line()

    # Skills Section
    if data.get("skills"):
        cv.add_section("Skills")
        if isinstance(data["skills"], str):
            cv.add_oneline_title_item("Skills", data["skills"])
        elif isinstance(data["skills"], list):
            for skill_category in data["skills"]:
                cv.add_oneline_title_item(
                    skill_category.get("category", ""),
                    ", ".join(skill_category.get("items", []))
                )
        cv.add_empty_line()
        cv.add_sectionsep()

    # Projects Section
    if data.get("projects"):
        cv.add_section("Projects")
        for project in data["projects"]:
            cv.add_project(
                title=project.get("title", ""),
                date=project.get("date", ""),
                description=project.get("description", "")
            )
        cv.add_empty_line()
        cv.add_empty_line()
        cv.add_sectionsep()

    # Education Section
    if data.get("education"):
        cv.add_section("Education")
        for edu in data["education"]:
            cv.add_education(
                institution=edu.get("institution", ""),
                major=edu.get("major", ""),
                date=edu.get("date", ""),
                location=edu.get("location", "")
            )
        cv.add_empty_line()

    # Add document metadata
    cv.add_document_metadata()

    return cv.get_content()


def main() -> None:
    """Generate the resume in Typst format."""
    # Load data from JSON
    data = load_data()

    # Generate CV content using the new approach
    cv_content = generate_cv_from_data(data)

    # Write to cv.typ file
    cv_path = pathlib.Path(__file__).parent /"templates" / "resume.typ"

    with open(cv_path, "w") as f:
        f.write(cv_content)

    print(f"CV generated successfully at {cv_path}")


if __name__ == "__main__":
    main()
