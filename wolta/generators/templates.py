"""Templates generator for note creation patterns."""

from datetime import datetime
from pathlib import Path


class TemplateGenerator:
    """Generates standardized note templates respecting T0.1.1 specification."""

    # Template definitions: name, type, description
    TEMPLATES = {
        "Person.md": {
            "type": "identity",
            "description": "To capture information about contacts and collaborators",
            "tags": ["person", "professional", "active"],
        },
        "Project.md": {
            "type": "project",
            "description": "To document ongoing or completed projects",
            "tags": ["project", "active"],
        },
        "Technical-Concept.md": {
            "type": "knowledge",
            "description": "To explain technologies, architectures, and patterns",
            "tags": ["knowledge", "active"],
        },
        "Decision.md": {
            "type": "project",
            "description": "To document architectural and technical decisions (ADR)",
            "tags": ["decision", "architecture", "active"],
        },
        "General-Note.md": {
            "type": "knowledge",
            "description": "To capture reflections and miscellaneous information",
            "tags": ["note", "active"],
        },
    }

    def __init__(self, vault_path: str):
        """
        Initialize the template generator.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)

    def generate(self) -> None:
        """Generate all template files in TEMPLATES/ folder."""
        templates_path = self.vault_path / "TEMPLATES"
        templates_path.mkdir(parents=True, exist_ok=True)

        # Generate each template
        for filename, config in self.TEMPLATES.items():
            template_file = templates_path / filename
            if not template_file.exists():
                content = self._generate_template_content(
                    filename,
                    config["type"],
                    config["tags"],
                )
                template_file.write_text(content, encoding="utf-8")

        # Generate README.md with instructions
        self._create_templates_readme(templates_path)

    def _generate_template_content(
        self,
        filename: str,
        note_type: str,
        tags: list,
    ) -> str:
        """
        Generate template content with proper frontmatter.

        Args:
            filename: Template filename
            note_type: YAML type field value
            tags: List of tags for the template

        Returns:
            Template content as string
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        tags_str = ", ".join(tags)

        if filename == "Person.md":
            return f"""---
title: "Person's name"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
identity_aspect: "professional"
related_notes: []
context_for_claude: false
---

# [[Person's name]]

## TL;DR
[1-2 line summary: name, main role, and why they matter in your KB.]

## Basic information
- **Role/Function:** [Description of the role or function]
- **Organization:** [Company, team, or context]
- **Location:** [City, country, or remote context]
- **Contact:** [Email, phone, or contact link]

## Description
[Descriptive paragraph about the person: who they are, what they do, relevance in current projects.]

## Relationships and context
- Participates in: [[project-example]], [[project-volta]]
- Reports to: [[identity-person-name]]
- Collaborates with: [[identity-person-a]], [[identity-person-b]]
- Expertise: [[knowledge-technical-skill]], [[knowledge-domain]]

## Notes
[Observations, communication preferences, relevant background, or additional context.]

## Relationships with other modules
- [[project-example]] — Projects they participate in
- [[work-current-role]] — Relevant work context
- [[knowledge-skill]] — Areas of expertise
"""

        elif filename == "Project.md":
            return f"""---
title: "Project name"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
project_status: "in-progress"
start_date: {date_str}
target_date:
---

# [[Project name]]

## TL;DR
[1-2 line summary: what the project is, current status, and main owner.]

## Description
[Summary of what the project is and its purpose.]

## General information
- **Owner:** [[identity-person-name]]
- **Team:** [[identity-person-a]], [[identity-person-b]], [[identity-person-c]]
- **Dates:** Start: {date_str} | Estimated end: [YYYY-MM-DD]
- **Status:** In Progress | Planning | On Hold | Completed | Cancelled

## Goals
- [Goal 1]
- [Goal 2]
- [Goal 3]

## Context
[Description of why the project exists, the problem to solve, or business context.]

## Components and deliverables
- [[knowledge-technical-concept]] — [Brief description]
- [[knowledge-another-concept]] — [Brief description]

## Key decisions
- [[decision-architecture]] — Architectural decision
- [[decision-technical]] — Technical decision

## Risks and dependencies
- **Risk 1:** [Description] | Mitigation: [...]
- **Dependency:** Related to [[project-other]] or [[knowledge-domain]]

## Notes and next steps
[Recent progress, blockers, or pending actions.]

## Relationships with other modules
- [[identity-person]] — Team involved
- [[knowledge-concept]] — Related technical concepts
- [[project-dependent]] — Dependent projects
"""

        elif filename == "Technical-Concept.md":
            return f"""---
title: "Technical concept name"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
knowledge_domain: "backend-engineering"
learnings: ["learning1", "learning2"]
---

# [[Technical concept name]]

## TL;DR
[1-2 line summary: what it is, what it is for, and why it matters.]

## Definition
[Clear and concise explanation of what this concept is.]

## Context and why it matters
[Why this concept is relevant in the context of VOLTA or the business.]

## Key components or pillars
- [Component 1 and explanation]
- [Component 2 and explanation]

## Usage examples
```
[Code snippet, diagram, or practical example]
```

## Relationships
- **Uses:** [[knowledge-concept-a]], [[knowledge-concept-b]]
- **Used by:** [[project-example]], [[decision-example]]
- **Similar to:** [[knowledge-concept-c]]
- **Contrasts with:** [[knowledge-concept-d]]

## Resources and references
- [Official documentation URL]
- [Recommended article or tutorial]
- [[knowledge-personal-learning]]

## Notes
[Personal observations, specific use cases, or caveats.]

## Relationships with other modules
- [[project-using-concept]] — Projects that use this concept
- [[identity-person-expert]] — People with expertise
- [[decision-related]] — Related decisions
"""

        elif filename == "Decision.md":
            return f"""---
title: "Decision title"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
---

# [[Decision title]]

## TL;DR
[1-2 line summary: what was decided and why.]

## Context
[Description of the problem or question that required a decision. Include constraints, requirements, and business context.]

## Options considered

### Option A: [Name]
- **Pros:** [..., ...]
- **Cons:** [..., ...]

### Option B: [Name]
- **Pros:** [..., ...]
- **Cons:** [..., ...]

### Option C: [Name]
- **Pros:** [..., ...]
- **Cons:** [..., ...]

## Decision made
**Chosen:** Option [X]: [Name]

## Rationale
[Clear explanation of why this option was chosen over the others. Include the weighting of criteria and trade-offs.]

## Expected consequences
- **Positive:** [..., ...]
- **Negative or trade-offs:** [..., ...]

## People involved
- [[identity-person-1]] — Made the decision
- [[identity-person-2]] — Consulted
- [[identity-person-3]] — Affected

## Affected components
- [[project-example]] — Impacted project
- [[knowledge-concept]] — Related technical concept

## Follow-up notes
[How it will be implemented, who is responsible, expected timeline.]

## Relationships with other modules
- [[project-related]] — Project in which this decision is made
- [[decision-predecessor]] — Prior decision that supports this one
- [[knowledge-concept]] — Technical concepts involved
"""

        else:  # General-Note.md
            return f"""---
title: "Note title"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
knowledge_domain: "general"
---

# [[Note title]]

## TL;DR
[1-2 line summary: what this note is and why it matters.]

## Content
[Free body. Can include paragraphs, lists, code snippets, questions, or reflections.]

## Context (optional)
[Where this note fits in the larger system. What problem it solves or what question it answers.]

## Pending actions (if applicable)
- [ ] [Action 1]
- [ ] [Action 2]

## Additional notes
[Final observations, internal references, or caveats.]

## Relationships with other modules
- [[note-related]] — Related notes
- [[project-or-person]] — Relevant projects or people
- [[knowledge-concept]] — Related concepts
"""

    def _create_templates_readme(self, templates_path: Path) -> None:
        """Create README.md with template usage instructions for Claude agent."""
        readme_file = templates_path / "README.md"
        if readme_file.exists():
            return

        content = """---
title: "Templates - Usage guide for the Claude agent"
type: "index"
created: {created}
modified: {created}
tags: [templates, navigation, hub, ai]
status: "active"
---

# Templates - Usage Guide

These templates standardize the capture of information in your knowledge base. Each template includes a mandatory YAML frontmatter that enables search, filtering, and automatic processing by Claude agents.

## Template categories

### 1. **Person.md** — Contacts and collaborators
- **Type:** `identity`
- **Tags:** `[person, professional, active]`
- **When to use it:** To document key people in your work or personal context
- **Content:** Role, organization, relationships, expertise
- **Example:** "person-john-doe.md", "person-maria-boss.md"

### 2. **Project.md** — Active and past projects
- **Type:** `project`
- **Tags:** `[project, active, [domain-work|personal]]`
- **When to use it:** To document any project (work or personal)
- **Content:** Description, goals, team, dates, status, risks
- **Example:** "project-volta.md", "project-home-renovation.md"

### 3. **Technical-Concept.md** — Technologies, patterns, architectures
- **Type:** `knowledge`
- **Tags:** `[knowledge, [backend|frontend|architecture|pattern], active]`
- **When to use it:** To explain technical concepts you need to remember
- **Content:** Definition, components, examples, relationships, resources
- **Example:** "knowledge-llm-basics.md", "knowledge-microservices.md"

### 4. **Decision.md** — Architectural decisions (ADR format)
- **Type:** `project` (with the `decision` tag)
- **Tags:** `[decision, [architecture|business|process], active]`
- **When to use it:** To document important decisions with their context and rationale
- **Content:** Problem, options, decision made, rationale, consequences
- **Example:** "decision-database-postgres.md", "decision-react-framework.md"

### 5. **General-Note.md** — Reflections and miscellaneous notes
- **Type:** `knowledge`
- **Tags:** `[note, [free-category], active]`
- **When to use it:** To capture reflections that do not fit other categories
- **Content:** Flexible (paragraphs, lists, questions, ideas)
- **Example:** "note-weekly-reflection.md", "note-api-design-thoughts.md"

---

## Mandatory YAML frontmatter

All notes MUST include this frontmatter at the top:

```yaml
---
title: "Note title (max 100 characters)"
type: "identity | preference | work | project | knowledge | personal | index"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: "active | archived | draft"
---
```

**Mandatory fields:**
- `title`: Clear description of the content
- `type`: Category of the note (per template)
- `created`: Creation date
- `modified`: Last edit date
- `tags`: Array of tags (max 5)
- `status`: Current status of the note

**Optional fields by type:**
- **Person:** `identity_aspect`, `related_notes`, `context_for_claude`
- **Project:** `project_status`, `start_date`, `target_date`
- **Technical-Concept:** `knowledge_domain`, `learnings`
- **Decision:** (none special, uses tags)
- **General-Note:** `knowledge_domain`

---

## How to use the templates in Obsidian

### Option 1: Insert template (recommended)
1. Open the Obsidian menu: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Search for "Insert template"
3. Choose the template based on the type of note
4. Complete the YAML frontmatter
5. Fill in the content

### Option 2: Copy manually
1. Open the template file at `TEMPLATES/[Template-Name].md`
2. Copy all the content
3. Create a new note in the appropriate folder
4. Paste the content and customize it

---

## Tag system (per T0.1.1)

Tags should follow these categories:

**Domain:**
- `work`, `personal`, `ai`

**Subtopic (specific subtopic):**
- `backend`, `frontend`, `architecture`, `pattern`, `typescript`, etc.

**Temporal (temporal status):**
- `active`, `archived`, `draft`, `review`

**Relationship (relationship with other notes):**
- `blocker`, `depends-on`, `decision`, `principle`, `needs-update`

**Metadata (meta-information):**
- `index`, `navigation`, `hub`, `template`

**Usage examples:**
- Person: `[person, professional, active]`
- Project: `[project, active, work, backend]`
- Technical-Concept: `[knowledge, typescript, active, backend]`
- Decision: `[decision, architecture, active]`
- General-Note: `[note, reflection, active]`

---

## Naming conventions

Notes should be named with a prefix + description:

```
[category]-[descriptive-name].md

Examples:
- person-john-doe.md
- person-maria-boss.md
- project-volta.md
- project-home-renovation.md
- knowledge-llm-basics.md
- knowledge-react-hooks.md
- decision-database-postgres.md
- decision-react-framework.md
- note-weekly-reflection.md
- note-architecture-thoughts.md
```

**Rules:**
- Use English primarily (unless translating loses meaning)
- Lowercase and hyphens (kebab-case)
- Concise but descriptive
- No spaces or special characters

---

## 🔗 Links and relationships

The templates include a "Relationships with other modules" section to create backlinks.

**Obsidian syntax:**
```markdown
[[note-name]] — Description of why it is related

[[project-volta]] — Main project I work on
[[knowledge-llm-basics]] — Fundamental technical concept
[[identity-values]] — Values that guide my decisions
```

**Maximum 5 links per note** to avoid cluttering the graph.

---

## Checklist for a new note

- [ ] Chose the right template based on the type of content
- [ ] Completed the YAML frontmatter (title, type, created, modified, tags, status)
- [ ] Included a 1-2 line TL;DR
- [ ] Added the main description/content
- [ ] Created at most 5 links in "Relationships with other modules"
- [ ] Saved the note with the name: `[category]-[name].md`

---

## Relationship with other folders

The templates generated here are used to create notes in:
- **IDENTITY/** — For person-type notes
- **PROJECTS/** — For project-type notes
- **KNOWLEDGE/** — For technical-concept and general-note notes
- **AI-SYSTEM/CONTEXT/** — For agent context notes

---

## Note for the Claude agent

This README contains the instructions for determining **when and how to use each template**. When creating new notes:

1. **Identify the type of content** based on the 5 available types
2. **Choose the corresponding template**
3. **Respect the mandatory YAML frontmatter**
4. **Use the T0.1.1 tag system**
5. **Create relevant links** (at most 5 per note)

The templates provide consistent context and enable automatic search and filtering.

---

**Created:** {created}
**Last updated:** {created}
**Version:** 1.0.0
""".format(created=datetime.now().strftime("%Y-%m-%d"))

        readme_file.write_text(content, encoding="utf-8")
