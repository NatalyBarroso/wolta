"""Structure generator for vault folder hierarchy."""

from datetime import datetime
from pathlib import Path

from wolta import __version__ as CLI_VERSION
from wolta.utils.version_manager import VersionManager


def _inject_wolta_version(content: str, version: str) -> str:
    """Insert a `wolta_version` field into the YAML frontmatter of a managed file.

    Adds the line right after the opening `---` delimiter. Operates on the
    assembled string (not inside the literal) so it is safe regardless of
    whether the source used an f-string, `.format()`, or a plain string, and
    never collides with literal braces in the body (T2.3.2 R-03).
    """
    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        lines.insert(1, f'wolta_version: "{version}"')
    return "\n".join(lines)


class StructureGenerator:
    """Generates the complete folder and file structure for a Wolta vault."""

    # Main categories from T0.1.1
    MAIN_CATEGORIES = [
        "IDENTITY",
        "PREFERENCES",
        "WORK",
        "PROJECTS",
        "PERSONAL-SPACE",
        "KNOWLEDGE",
        "AI-SYSTEM",
    ]

    # Subcategories for AI-SYSTEM (including BOOTSTRAP)
    AI_SYSTEM_SUBCATEGORIES = [
        "AGENTS",
        "BOOTSTRAP",
        "CONTEXT",
        "SESSIONS",
        "SKILLS",
        "WORKFLOWS",
    ]

    # Base files to create in each category
    CATEGORY_FILES = {
        "IDENTITY": [
            "INDEX-IDENTITY.md",
            "identity-profile.md",
            "identity-values.md",
            "identity-voice.md",
            "identity-bio.md",
        ],
        "PREFERENCES": [
            "INDEX-PREFERENCES.md",
            "preferences-tools.md",
            "preferences-work-style.md",
            "preferences-lifestyle.md",
        ],
        "WORK": [
            "INDEX-WORK.md",
            "work-overview.md",
            "work-current-role.md",
            "work-company.md",
            "work-team.md",
        ],
        "PROJECTS": ["INDEX-PROJECTS.md"],
        "PERSONAL-SPACE": [
            "INDEX-PERSONAL-SPACE.md",
            "personal-hobbies.md",
            "personal-interests.md",
        ],
        "KNOWLEDGE": ["INDEX-KNOWLEDGE.md"],
        "AI-SYSTEM": ["INDEX-AI-SYSTEM.md"],
    }

    # Files to create in AI-SYSTEM subcategories
    SUBCATEGORY_FILES = {
        "BOOTSTRAP": [],  # bootstrap-questions.md will be generated separately
        "CONTEXT": ["context-current.md"],
        "AGENTS": [],
        "SESSIONS": [],
        "SKILLS": [],
        "WORKFLOWS": [],
    }

    def __init__(self, vault_path: str):
        """
        Initialize the structure generator.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)

    def generate(self) -> None:
        """Generate the complete vault structure."""
        # Create main categories
        for category in self.MAIN_CATEGORIES:
            self._create_category(category)

        # Create AI-SYSTEM subcategories
        ai_system_path = self.vault_path / "AI-SYSTEM"
        for subcategory in self.AI_SYSTEM_SUBCATEGORIES:
            self._create_subcategory(ai_system_path, subcategory)

        # Create special folders
        self._create_templates_folder()
        self._create_wolta_config_folder()
        self._create_version_file()
        self._create_raw_folder()

        # Create reference documents
        self._create_design_file()
        self._create_readme_file()

        # Create agent instruction files (Option B: skill logic in vault)
        self._create_claude_md()
        self._create_bootstrap_generate_skill()
        self._create_raw_ingest_skill()
        self._create_ingest_protocol()
        self._create_source_adapter_template()
        self._create_source_files_adapter()

    def _create_category(self, category: str) -> None:
        """Create a main category folder with its files."""
        category_path = self.vault_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        # Create files for this category
        files = self.CATEGORY_FILES.get(category, [])
        for filename in files:
            file_path = category_path / filename
            if not file_path.exists():
                self._create_file_with_frontmatter(file_path, category, filename)

    def _create_subcategory(self, parent_path: Path, subcategory: str) -> None:
        """Create a subcategory folder with its files."""
        subcategory_path = parent_path / subcategory
        subcategory_path.mkdir(parents=True, exist_ok=True)

        # Create files for this subcategory (skip BOOTSTRAP - it's handled separately)
        if subcategory != "BOOTSTRAP":
            files = self.SUBCATEGORY_FILES.get(subcategory, [])
            for filename in files:
                file_path = subcategory_path / filename
                if not file_path.exists():
                    self._create_file_with_frontmatter(
                        file_path,
                        f"AI-SYSTEM/{subcategory}",
                        filename,
                    )

    def _create_templates_folder(self) -> None:
        """Create TEMPLATES folder with a base template."""
        templates_path = self.vault_path / "TEMPLATES"
        templates_path.mkdir(parents=True, exist_ok=True)

        template_file = templates_path / "template-note.md"
        if not template_file.exists():
            content = """---
title: "[New note]"
type: "identity | preference | work | project | knowledge | personal"
created: {{date}}
modified: {{date}}
tags: [tag1, tag2]
status: "draft"
---

## Content

[Write here]

## Relationships

[Links to other notes]
"""
            template_file.write_text(content, encoding="utf-8")

    def _create_wolta_config_folder(self) -> None:
        """Create .wolta configuration folder."""
        wolta_path = self.vault_path / ".wolta"
        wolta_path.mkdir(parents=True, exist_ok=True)

        # Create a config file
        config_file = wolta_path / "config.md"
        if not config_file.exists():
            content = """# Wolta Configuration

This folder contains Wolta-specific configuration files and metadata.

## Folders

- **initialized**: Marker file indicating vault initialization status
- **config.md**: This configuration file

## Metadata

- Created: {created}

> The vault schema version lives in `.wolta/version` (source of truth). Do not edit that information here.

## Next Steps

1. Configure Obsidian vault settings
2. Complete bootstrap questions in AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md
3. Populate knowledge base categories
""".format(created=datetime.now().isoformat())
            config_file.write_text(content, encoding="utf-8")

    def _create_version_file(self) -> None:
        """Write .wolta/version with the initial schema state (D-08, T2.3.2).

        Delegates to VersionManager so there is a single writer of the
        vault version. The schema version is taken from the CLI's __version__.
        """
        VersionManager(str(self.vault_path)).initialize(CLI_VERSION)

    def _create_raw_folder(self) -> None:
        """Create raw/ staging directory for unprocessed source files.

        raw/           - Drop zone for source files before ingestion
        raw/processed/ - Processed source files (audit trail, never deleted)
        raw/.gitkeep   - Keeps raw/ tracked in git even when empty
        """
        raw_path = self.vault_path / "raw"
        processed_path = raw_path / "processed"

        raw_path.mkdir(parents=True, exist_ok=True)
        processed_path.mkdir(parents=True, exist_ok=True)

        # .gitkeep so both dirs are tracked in git when empty
        for keep_path in (raw_path / ".gitkeep", processed_path / ".gitkeep"):
            if not keep_path.exists():
                keep_path.touch()

        # README inside raw/ so the agent and user know the rules
        readme = raw_path / "README.md"
        if not readme.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            content = f"""# raw/ — Staging Zone for Ingestion

This directory receives **unprocessed** source files that the agent will turn into valid KB notes.

## Rules

- Drop here any file you want to ingest: `.md`, `.txt`, `.pdf`, `.docx`
- Files here are **not valid KB notes**: they have no frontmatter and do not appear in the Graph View
- Once a file is processed, the agent moves it to `raw/processed/` — it does not delete it
- If you cannot export a source (e.g. WhatsApp, Notion with restrictions), paste the content manually into a new `.md` here

## How to trigger the ingestion

Once you have dropped your files, tell the agent:

- `/raw-ingest`
- "process the files in raw"
- "ingest my personal information"

## Full flow

See `AI-SYSTEM/SKILLS/raw-ingest.md` for the runbook the agent follows.

---

*Generated by wolta init · {today}*
"""
            readme.write_text(content, encoding="utf-8")

    def _create_file_with_frontmatter(
        self,
        file_path: Path,
        category: str,
        filename: str,
    ) -> None:
        """Create a file with YAML frontmatter."""
        # Determine the type based on category
        type_mapping = {
            "IDENTITY": "identity",
            "PREFERENCES": "preference",
            "WORK": "work",
            "PROJECTS": "project",
            "PERSONAL-SPACE": "personal",
            "KNOWLEDGE": "knowledge",
        }

        # Extract base type from category
        base_type = type_mapping.get(category.split("/")[0], "index")

        # Build frontmatter
        frontmatter = f"""---
title: "{filename.replace("-", " ").replace(".md", "").title()}"
type: "{base_type}"
created: {datetime.now().strftime("%Y-%m-%d")}
modified: {datetime.now().strftime("%Y-%m-%d")}
tags: []
status: "active"
---

## Content

[Fill in this section]

## Relationships

[Add links to other notes if applicable]
"""

        file_path.write_text(frontmatter, encoding="utf-8")

    def _create_design_file(self) -> None:
        """Create DESIGN.md specification file in vault root."""
        design_file = self.vault_path / "DESIGN.md"
        if design_file.exists():
            return

        content = """---
title: "DESIGN - KB-PERSONAL Specification"
type: "index"
created: {created}
modified: {created}
tags: [design, architecture, kb-structure]
status: "active"
---

<!-- wolta:managed:start id="vault-spec" v="{version}" -->

# DESIGN — KB-PERSONAL Specification

**Vault:** KB-PERSONAL
**Status:** Active

---

## 1. Vault Goal

Centralize personal and professional information in a Knowledge Base that Claude agents can query. A hybrid PARA + Zettelkasten system for maximum flexibility.

---

## 2. Folder Structure

```
wolta-vault/
├── IDENTITY/               # Who you are: profile, values, history, voice
│   ├── INDEX-IDENTITY.md
│   ├── identity-profile.md
│   ├── identity-values.md
│   ├── identity-voice.md
│   └── identity-bio.md
│
├── PREFERENCES/            # Tastes, habits, personal settings
│   ├── INDEX-PREFERENCES.md
│   ├── preferences-tools.md
│   ├── preferences-work-style.md
│   └── preferences-lifestyle.md
│
├── WORK/                   # Professional context: company, role, team
│   ├── INDEX-WORK.md
│   ├── work-overview.md
│   ├── work-current-role.md
│   ├── work-company.md
│   └── work-team.md
│
├── PROJECTS/               # Active and past projects
│   └── INDEX-PROJECTS.md
│
├── PERSONAL-SPACE/         # Everyday content: movies, books, quotes
│   ├── INDEX-PERSONAL-SPACE.md
│   ├── personal-hobbies.md
│   └── personal-interests.md
│
├── KNOWLEDGE/              # Educational content: courses, studies, research
│   └── INDEX-KNOWLEDGE.md
│
├── AI-SYSTEM/              # Operational resources for the agent
│   ├── INDEX-AI-SYSTEM.md
│   ├── BOOTSTRAP/          # Initial population of the KB
│   │   ├── INDEX-BOOTSTRAP.md
│   │   ├── BOOTSTRAP-QUESTIONNAIRE.md    # 27 questions
│   │   └── BOOTSTRAP-MAPPING.md          # Question→note mapping
│   ├── AGENTS/             # Agent definitions
│   ├── CONTEXT/            # Current agent context
│   │   └── context-current.md
│   ├── SESSIONS/           # Session history
│   ├── SKILLS/             # Available skills and prompts
│   └── WORKFLOWS/          # Workflows and automations
│
├── TEMPLATES/              # Templates for new notes
│   └── template-note.md
│
├── raw/                    # Staging for unprocessed source files
│   ├── processed/          # Already processed files (audit)
│   └── README.md           # Directory rules
│
├── DESIGN.md               # This document (vault specification)
├── README.md               # Quick start guide
│
└── graphify-out/           # Generated knowledge graph
    ├── graph.json          # Queryable structure
    ├── GRAPH_REPORT.md     # Graph analysis
    └── graph.html          # Interactive visualization
```

---

## 3. Standard Frontmatter

Every .md file must include:

```yaml
---
title: "Descriptive title"
type: "index | identity | preference | work | project | knowledge | personal"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: "active | draft | archived"
context_for_claude: true | false
---
```

**Optional fields:**
- `index_module`: For INDEX files, indicate the main module
- `related_notes`: Array of related notes

---

## 4. Tag System

**Domains:**
- `identity` / `personal` / `work` / `ai` — main category
- `professional` / `hobby` — context

**Temporal:**
- `active` — in use now
- `draft` — incomplete draft
- `archived` — historical

**Relationship:**
- `blocker` — depends on another note
- `depends-on` — another note depends on this one
- `reference` — read-only

---

## 5. Bootstrap: Initial Population

### Folder: `AI-SYSTEM/BOOTSTRAP/`

**Operational hub for the initial population of the KB.**

1. **INDEX-BOOTSTRAP.md** — Navigation hub and checklist
2. **BOOTSTRAP-QUESTIONNAIRE.md** — 27 reflective questions (45-90 minutes)
3. **BOOTSTRAP-MAPPING.md** — Question → note reference

### Process

1. Open BOOTSTRAP-QUESTIONNAIRE.md in Obsidian
2. Answer each question (2-5 paragraphs per question)
3. Check BOOTSTRAP-MAPPING.md to see where each answer maps
4. Create notes following the mapping pattern
5. Run graphify to update the graph:
   ```bash
   graphify /path/to/vault --update --no-cluster
   ```

---

## 6. Knowledge Graph (Graphify)

**Tool:** Graphify CLI
**Output:** `graphify-out/`

**Generated files:**
- `graph.json` — Queryable structure of relationships
- `GRAPH_REPORT.md` — Graph analysis
- `graph.html` — Interactive visualization

**Command to update:**
```bash
graphify /path/to/vault --update --no-cluster
```

---

## 7. Next Steps

1. Open the vault in Obsidian
2. Explore the structure in the File Explorer
3. Read README.md for a quick guide
4. Navigate to AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md to begin
5. Answer BOOTSTRAP-QUESTIONNAIRE.md
6. Run graphify to update the graph

---

**Last updated:** {created}
**Status:** Active — Ready for use once bootstrap is completed

<!-- wolta:managed:end id="vault-spec" -->

## User notes

<!-- Free space. wolta never touches anything outside the markers. -->
""".format(created=datetime.now().strftime("%Y-%m-%d"), version=CLI_VERSION)

        design_file.write_text(content, encoding="utf-8")

    def _create_claude_md(self) -> None:
        """Create CLAUDE.md project instructions in vault root.

        This file is loaded automatically by Claude agents when the vault
        is connected as a project in Cowork. It registers available commands
        and tells the agent how to operate within the vault context.
        """
        claude_file = self.vault_path / "CLAUDE.md"
        if claude_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""# WOLTA — Project Instructions for the Claude Agent

<!-- wolta:managed:start id="agent-instructions" v="{CLI_VERSION}" -->
This vault is a **personal knowledge base** built with Obsidian and designed to be queried and operated by Claude agents. It contains the owner's personal, professional, and learning information.

---

## Vault context

When the user connects this vault as a project, this file is loaded automatically. The agent must:

1. Recognize that it is operating inside a WOLTA vault
2. Read the files with `context_for_claude: true` to build the user's context
3. Answer queries using the vault content as the primary source of truth
4. Use the skills available in `AI-SYSTEM/SKILLS/` for structured operations

---

## Fixed commands

### `/bootstrap-generate`

**File:** `AI-SYSTEM/SKILLS/bootstrap-generate.md`
**When:** When the user has completed the bootstrap questionnaire and wants to turn their answers into vault notes.

Triggers:
- `/bootstrap-generate`
- "generate the notes for my knowledge base"
- "create the bootstrap notes"
- "populate the kb"
- "turn the answers into notes"

---

## Ingestion from external sources

The vault uses an extensible ingestion system. The core protocol is in `AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md`. The **source adapters** are skills in `AI-SYSTEM/SKILLS/` with the `source-` prefix that describe how to extract information from a specific source and produce blocks compatible with the protocol.

### How to respond when the user asks to ingest information

**Step 1 — Identify the source**
Determine where the information comes from: local files, a directory, an external app (Notion, Discord, etc.), content from the active conversation, or any other origin.

**Step 2 — Look for an adapter for that source**
List the files in `AI-SYSTEM/SKILLS/` that match the `source-*.md` pattern.
Read the one that corresponds to the requested source.

**Step 3 — If the adapter exists**
Follow its instructions for the extraction phase, then continue with `INGEST-PROTOCOL.md` for classification, gate, writing, and tracking.

**Step 4 — If the adapter does NOT exist**
Present the user with two options:
```
I do not have an adapter configured for [source].
Options:
  a) Export the content manually to raw/ and run /raw-ingest
  b) Create an adapter for [source] using TEMPLATES/template-source-adapter.md
     (you only need to fill in the marked sections — takes ~10 minutes)
```

**Step 5 — Ingestion from the active conversation**
If, during a conversation, the user explains something relevant to the KB (project context, technical decision, personal information), you can propose ingesting it directly:
```
That looks like valuable information for your KB.
Do you want me to add it to [suggested target note]?
```
Do not ingest without the user's confirmation. Information from the active conversation does not need to go through a source file.

### General ingestion triggers (any source)

- "ingest my information from [source]"
- "explore [directory/app] and feed the KB"
- "add this to my KB"
- "process [source] as notes"
- "/ingest [source]"

---

## raw/ directory

`raw/` is the **universal fallback adapter**: any source without an adapter can use this directory as a manual bridge. The corresponding adapter is `AI-SYSTEM/SKILLS/source-files.md`.

Operational rules:
1. Files in `raw/` are not valid notes — do not read them as KB context
2. Do not write to the vault without the user's approval (gate in INGEST-PROTOCOL.md)
3. When processing a file, move it to `raw/processed/` — never delete it
4. Attribute the source: add `source` and `ingested` to the frontmatter of notes created from `raw/`

---

## How to query the KB

1. Always prioritize the vault content over your training knowledge for the user's data
2. Files with `context_for_claude: true` are primary sources
3. If the information is not in the vault, say so explicitly instead of inferring it

---

## Vault structure

```
IDENTITY/           → Owner's profile, values, history, voice
PREFERENCES/        → Work style, tools, habits
WORK/               → Current role, company, team, career
PROJECTS/           → Active, future, and proud projects
PERSONAL-SPACE/     → Hobbies, cultural interests, quotes
KNOWLEDGE/          → Current learning, expertise, sources
AI-SYSTEM/          → Operational resources for the agent
  BOOTSTRAP/        → Initial ingestion questionnaire and mapping
  SKILLS/           → Agent skills
    INGEST-PROTOCOL.md     → Canonical ingestion pipeline (source-agnostic)
    source-*.md            → Source adapters (one per source)
    bootstrap-generate.md  → Initial population skill
  CONTEXT/          → Dynamic session context
  SESSIONS/         → Session history
  WORKFLOWS/        → Automated workflows
TEMPLATES/
  template-source-adapter.md  → Template for creating new adapters
raw/                → Universal fallback staging (do NOT read as KB)
  processed/        → Processed files (audit)
```

---

## Bootstrap status

Read `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` → `status` field in frontmatter.
If `kb_populated: true`, the vault has already been populated. If not, the notes have not yet been generated.

---

## KB conventions

- Every relevant file has `context_for_claude: true` in its frontmatter
- Internal links: `[[note-name]]`
- `status`: `active`, `draft`, or `archived`
- PROJECTS notes with `status: archived` are historical

---

*Generated by wolta init · {today}*
<!-- wolta:managed:end id="agent-instructions" -->

## User notes

<!-- Free space for your instructions. wolta never touches anything outside the markers. -->
"""
        claude_file.write_text(content, encoding="utf-8")

    def _create_bootstrap_generate_skill(self) -> None:
        """Create the bootstrap-generate skill instruction file.

        Lives at AI-SYSTEM/SKILLS/bootstrap-generate.md. The agent reads this
        file when /bootstrap-generate is triggered and follows its instructions
        to populate the vault from the completed questionnaire.
        """
        skill_file = self.vault_path / "AI-SYSTEM" / "SKILLS" / "bootstrap-generate.md"
        if skill_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""---
title: "SKILL — bootstrap-generate"
type: "skill"
created: {today}
modified: {today}
tags: [skill, bootstrap, agent, kb-population]
status: "active"
context_for_claude: true
---

# SKILL: bootstrap-generate

**Purpose:** Populate the vault with the initial knowledge base notes from the bootstrap questionnaire answers. This process runs only once, immediately after the user completes `BOOTSTRAP-QUESTIONNAIRE.md`.

**Executor:** Claude agent — not the user.

---

## Trigger Detection

Activate this skill when the user says any of the following:

- `/bootstrap-generate`
- "generate the notes for my knowledge base"
- "create the bootstrap notes"
- "populate the kb"
- "generate notes from the questionnaire"
- "turn the answers into notes"

---

## Pre-flight: Validation before running

Before creating any file, verify that these conditions are met:

**1. The questionnaire is complete**
Read `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md`.
Verify that the frontmatter contains `status: "completed"` and that all 31 questions have an answer (they must not be empty nor contain only the text `[Your answer here]`).

If the questionnaire is not complete, respond:
```
The bootstrap questionnaire is not complete yet.
Navigate to AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md and answer
all the questions before running this command.
To answer conversationally, use: "start bootstrap"
```
And stop execution.

**2. The vault has write access**
Confirm that you can create files in the vault. If you do not have write access, inform the user and stop execution.

**3. Inform the user before proceeding**
Once validated, show this message and wait for confirmation:
```
Ready to populate your knowledge base.
I will create [N] notes in the folders:
IDENTITY, PREFERENCES, WORK, PROJECTS, PERSONAL-SPACE, KNOWLEDGE

Shall I proceed? (yes / no)
```

---

## Inputs you need to read

1. `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` — source of all answers
2. `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md` — question → target note mapping table

---

## Standard frontmatter for all notes

Every note created by this skill must begin with:

```yaml
---
title: "[Descriptive note title]"
type: "[identity | preference | work | project | personal | knowledge]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [category, subcategory, topic]
status: "active"
context_for_claude: true
---
```

The `context_for_claude: true` field is **mandatory** in all KB notes.

---

## Execution flow

### Step 1 — Read and parse the questionnaire

Read the complete `BOOTSTRAP-QUESTIONNAIRE.md`. Extract each answer by its ID:
- `P.ID.1` to `P.ID.6`
- `P.PREF.1` to `P.PREF.6`
- `P.WORK.1` to `P.WORK.5`
- `P.PROJ.1` to `P.PROJ.4`
- `P.PERS.1` to `P.PERS.5`
- `P.KNOW.1` to `P.KNOW.5`

### Step 2 — Read the mapping

Read `BOOTSTRAP-MAPPING.md` to know exactly which note receives the content of each question.

### Step 3 — Group answers by target note

Some notes receive content from multiple questions. Build an internal map:

```
identity-profile.md        ← P.ID.1 + P.ID.6
identity-values.md         ← P.ID.2 + P.ID.5
identity-bio.md            ← P.ID.3
identity-voice.md          ← P.ID.4

preferences-lifestyle.md   ← P.PREF.1 + P.PREF.5 + P.PREF.6
preferences-work-style.md  ← P.PREF.2 + P.PREF.4
preferences-tools.md       ← P.PREF.3

work-overview.md           ← P.WORK.1 + P.WORK.5
work-current-role.md       ← P.WORK.2 + P.WORK.3
work-team.md               ← P.WORK.4

[active projects]          ← P.PROJ.1 (one per identified project)
[future projects]          ← P.PROJ.2 (one per future project)
[proud projects]           ← P.PROJ.3 (one per archived project)
INDEX-PROJECTS.md          ← P.PROJ.4 (long-term vision)

personal-interests.md      ← P.PERS.1 + P.PERS.2 + P.PERS.4 + P.PERS.5
personal-hobbies.md        ← P.PERS.3

knowledge-current-learning.md ← P.KNOW.1
knowledge-interests.md        ← P.KNOW.2
knowledge-expertise.md        ← P.KNOW.3
knowledge-sources.md          ← P.KNOW.4
knowledge-insights.md         ← P.KNOW.5
```

### Step 4 — Handle PROJECTS notes (special case)

`P.PROJ.1` may mention multiple active projects. For each identified project, create an individual file:
- File name: `project-[name-kebab-case].md`
- Location: `PROJECTS/`
- Extract from the text the name, status, and description of each project

The same applies to future projects (`P.PROJ.2`) and proud projects (`P.PROJ.3`).
`INDEX-PROJECTS.md` receives only the content of `P.PROJ.4`.

### Step 5 — Create each note

For each target note:

1. **Check whether it already exists.** If it exists with real content, ask the user whether they want to overwrite it before proceeding.
2. **Write the frontmatter** with the correct type and tags for the category.
3. **Organize the content** using `###` headings to separate subtopics when a note receives multiple answers.
4. **Add tags** following the convention `[category, subtype, topic]`.
5. **Report progress** to the user as you go: `Created: IDENTITY/identity-profile.md`

### Step 6 — Add internal links

Once all notes are done, add `[[note-name]]` links where natural references exist. Add them at the end of each note in a `## Relationships` section:

- `identity-values.md` → `[[identity-profile]]`
- `work-overview.md` → `[[work-team]]`, `[[work-current-role]]`
- `knowledge-expertise.md` → `[[work-current-role]]`
- `knowledge-interests.md` → `[[knowledge-expertise]]`
- PROJECTS notes → `[[INDEX-PROJECTS]]`

### Step 7 — Final report

When finished, show a summary:

```
Bootstrap completed.

Notes created: [N]
├── IDENTITY/          [N] notes
├── PREFERENCES/       [N] notes
├── WORK/              [N] notes
├── PROJECTS/          [N] notes
├── PERSONAL-SPACE/    [N] notes
└── KNOWLEDGE/         [N] notes

Recommended next step:
Open the vault in Obsidian and review the Graph View
to verify that the notes are connected correctly.
```

Then update the frontmatter of `BOOTSTRAP-QUESTIONNAIRE.md` by adding:
- `kb_populated: true`
- `kb_populated_date: YYYY-MM-DD`

---

## Tags by category

| Note | Tags |
|------|------|
| identity-profile | `[identity, profile, personal]` |
| identity-values | `[identity, values, beliefs]` |
| identity-bio | `[identity, bio, history]` |
| identity-voice | `[identity, voice, communication]` |
| preferences-lifestyle | `[preferences, lifestyle, habits]` |
| preferences-work-style | `[preferences, work-style, focus]` |
| preferences-tools | `[preferences, tools, stack]` |
| work-overview | `[work, career, professional]` |
| work-current-role | `[work, role, expertise]` |
| work-team | `[work, team, relationships]` |
| project-* (active) | `[project, active, project-name]` |
| project-* (future) | `[project, ideation, project-name]` |
| project-* (proud) | `[project, archived, project-name]` |
| INDEX-PROJECTS | `[project, index, vision]` |
| personal-interests | `[personal, interests, culture]` |
| personal-hobbies | `[personal, hobbies, creative]` |
| knowledge-current-learning | `[knowledge, learning, active]` |
| knowledge-interests | `[knowledge, interests, future]` |
| knowledge-expertise | `[knowledge, expertise, skills]` |
| knowledge-sources | `[knowledge, sources, learning]` |
| knowledge-insights | `[knowledge, insights, principles]` |

---

## Rules

- Do not interrupt the process to ask intermediate questions, except for the initial confirmation and the case of an existing note with content.
- If an answer is empty or fewer than 20 words, create the note anyway with the warning: `> [Note: This section needs more content. Update the answer in BOOTSTRAP-QUESTIONNAIRE.md]`
- Do not modify `BOOTSTRAP-QUESTIONNAIRE.md` or `BOOTSTRAP-MAPPING.md` during execution (only the frontmatter at the end).
- Do not create notes outside the defined folders.
"""
        content = _inject_wolta_version(content, CLI_VERSION)
        skill_file.write_text(content, encoding="utf-8")

    def _create_raw_ingest_skill(self) -> None:
        """Create the raw-ingest skill instruction file.

        Lives at AI-SYSTEM/SKILLS/raw-ingest.md. The agent reads this file
        when /raw-ingest is triggered and follows its instructions to process
        files from raw/ into valid KB notes.
        """
        skill_file = self.vault_path / "AI-SYSTEM" / "SKILLS" / "raw-ingest.md"
        if skill_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""---
title: "SKILL — raw-ingest"
type: "skill"
created: {today}
modified: {today}
tags: [skill, ingestion, raw, agent]
status: "active"
context_for_claude: true
---

# SKILL: raw-ingest

**Purpose:** Process files dropped in `raw/` and turn them into valid KB notes. This skill can be run multiple times over the life of the vault: every time the owner wants to ingest new material.

**Executor:** Claude agent — not the user.
**Timebox:** 2 hours maximum per ingestion session.

---

## Trigger Detection

Activate this skill when the user says any of the following:

- `/raw-ingest`
- "process the files in raw"
- "ingest my personal information"
- "turn the raw files into notes"
- "I have files in raw to process"
- "there are new files in raw"

---

## Pre-flight: Validation before running

**1. Verify that there are files in `raw/`**
List the files in `raw/` (exclude `raw/processed/`, `raw/README.md`, and `raw/.gitkeep`).

If there are no files, respond:
```
There are no files in raw/ to process.
To start an ingestion, drop files in raw/ and run /raw-ingest again.
Supported formats: .md, .txt, .pdf, .docx
```
And stop execution.

**2. Verify write access to the vault**
Confirm that you can create and move files. If not, inform the user and stop.

---

## Step 1 — Inventory available files

List all files in `raw/` with their name and extension. Present to the user:

```
Files found in raw/:
- [file-name-1].[ext]
- [file-name-2].[ext]
...

Shall I analyze all of them? (yes / no / select which ones)
```

Wait for confirmation before continuing.

---

## Step 2 — Extract information blocks

For each confirmed file, read its content and extract information blocks, classifying them:

**Extraction criteria — include if:**
- It updates or enriches a note that already exists in the vault
- It covers a topic with no note in the vault yet
- It is information the owner uses frequently with the agent (profile, projects, stack, preferences)

**Extraction criteria — discard if:**
- It is redundant with notes already created in the bootstrap
- It is very temporary state ("this week I have X") → goes to `context-current.md` if applicable
- It does not provide useful context for the agent

For each extracted block, record internally:
```
- Excerpt/paraphrase of the block
- Target KB category: IDENTITY | PREFERENCES | WORK | PROJECTS | PERSONAL-SPACE | KNOWLEDGE
- Target note: file where it will go (existing or new)
- Operation: CREATE | APPEND | UPDATE
```

---

## Step 3 — Present the inventory to the user (mandatory gate)

Before writing to the vault, show the complete inventory of extracted blocks:

```
Blocks identified for ingestion:

[IDENTITY]
- identity-profile.md → APPEND: [block description]
- identity-values.md  → CREATE: [block description]

[WORK]
- work-current-role.md → UPDATE: [block description]

[PROJECTS]
- project-new.md → CREATE: [block description]

...

Total: [N] operations across [M] notes.
Shall I proceed? (yes / no / edit one)
```

**Do not write to the vault without the user's explicit approval.**

---

## Step 4 — Execute approved operations

For each approved operation:

### CREATE (new note)

```yaml
---
title: "[Descriptive title]"
type: "[identity | preference | work | project | personal | knowledge]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [category, subtype, topic]
status: "active"
context_for_claude: true
source: "[source-file-name]"
ingested: YYYY-MM-DD
---
```

Organize the content with `###` headings if the note receives multiple blocks.
Add a `## Relationships` section with `[[note-name]]` links where there are natural references.

### APPEND (add to an existing note)

Add the new content at the end of the relevant section of the note.
Update the `modified` field in the frontmatter.
Add `source` and `ingested` as additional fields if they do not exist.

### UPDATE (replace an outdated section)

Replace the indicated section with the new content.
Update `modified` in the frontmatter.
Keep the rest of the note intact.

Report to the user as you go:
```
✓ Created: IDENTITY/identity-profile.md
✓ Updated: WORK/work-current-role.md
...
```

---

## Step 5 — Move processed files

When you finish processing each source file, move it from `raw/` to `raw/processed/`.

```
raw/cv-nataly-2026.pdf  →  raw/processed/cv-nataly-2026.pdf
```

**Do not delete the files.** They serve as an audit trail of what information entered the vault and when.

---

## Step 6 — Record backlog (if applicable)

If the 2h timebox runs out before processing everything, or if there are blocks the user rejected but are valid for the future, record them in `AI-SYSTEM/CONTEXT/ingestion-backlog.md`:

```markdown
---
title: "Ingestion Backlog"
type: "system"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [system, ingestion, backlog]
status: "active"
---

## Pending processing

| Source | Block / Topic | Target category | Priority |
| --- | --- | --- | --- |
| [name] | [description] | [CATEGORY] | High/Medium/Low |
```

If the file already exists, add the new pending items at the end of the table.

---

## Step 7 — Closing report

When finished, show:

```
Ingestion completed.

Operations executed: [N]
├── Notes created:      [N]
├── Notes updated:      [N]
└── Notes unchanged:    [N]

Files processed: [N]
└── Moved to raw/processed/

[If there is a backlog:]
Pending items recorded in AI-SYSTEM/CONTEXT/ingestion-backlog.md: [N]
```

---

## Rules

- The Step 3 gate is mandatory. Do not write to the vault without the user's approval.
- Detect overlap before creating: if a note about the same topic already exists, prefer APPEND or UPDATE over a duplicate CREATE.
- If a file in `raw/` is not processable (incompatible format, corrupt, no useful content), inform the user and continue with the next one.
- Do not modify files in `raw/processed/` or in `AI-SYSTEM/BOOTSTRAP/`.
- The `context_for_claude: true` field is mandatory in all notes created or updated.
"""
        content = _inject_wolta_version(content, CLI_VERSION)
        skill_file.write_text(content, encoding="utf-8")

    def _create_ingest_protocol(self) -> None:
        """Create AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md — canonical source-agnostic ingestion pipeline."""
        skills_dir = self.vault_path / "AI-SYSTEM" / "SKILLS"
        skills_dir.mkdir(parents=True, exist_ok=True)
        protocol_file = skills_dir / "INGEST-PROTOCOL.md"
        if protocol_file.exists():
            return

        content = """---
title: "INGEST-PROTOCOL — Canonical Ingestion Pipeline"
type: "skill"
context_for_claude: true
tags: ["ingestion", "protocol", "skill"]
status: "active"
---

# INGEST-PROTOCOL — Canonical Ingestion Pipeline

This file defines the 5-phase pipeline the agent runs to ingest information from **any external source** into the vault. It is source-agnostic: the source adapters handle extraction; this protocol takes over from the already-extracted blocks.

---

## Contract: IngestionBlock

Every source adapter must produce blocks with this structure before passing them to the pipeline:

```
IngestionBlock {
  content:            text or excerpt of the block
  source_id:          source identifier (path, URL, channel, etc.)
  source_type:        "file" | "directory" | "api" | "chat" | [whatever the adapter defines]
  suggested_category: IDENTITY | PREFERENCES | WORK | PROJECTS | PERSONAL-SPACE | KNOWLEDGE
  suggested_note:     suggested target file name (without extension)
  operation:          CREATE | APPEND | UPDATE
}
```

If the adapter cannot determine `suggested_category` or `suggested_note`, it can leave them empty — the agent infers them during Phase 2.

---

## Phase 1 — Extraction (adapter's responsibility)

The agent reads the corresponding source adapter (`AI-SYSTEM/SKILLS/source-*.md`) and runs its instructions to produce a list of `IngestionBlock`.

If no adapter exists for the requested source, offer the user:
- Drop the content in `raw/` and use `source-files.md` as a fallback
- Create a new adapter from `TEMPLATES/template-source-adapter.md`

---

## Phase 2 — Classification

For each `IngestionBlock`:

1. Verify that `suggested_category` is one of the vault's main folders. If empty, infer it from the content.
2. Verify that `suggested_note` is a valid file name (lowercase, hyphens, no extension). If empty, infer it from the content.
3. If the inferred category is ambiguous, use KNOWLEDGE as a fallback and document the ambiguity.

---

## Phase 3 — Gate (mandatory approval)

Before writing to the vault, present the complete inventory to the user:

```
Blocks ready for ingestion:

| # | Content (summary) | Target | Operation |
|---|-------------------|--------|-----------|
| 1 | [10-word summary] | CATEGORY/note.md | CREATE |
| 2 | ...               | ...              | APPEND |

Do you approve these operations? (Y/n)
```

**Do not write to the vault until you receive explicit confirmation.**
If the user rejects a specific block, skip it and continue with the rest.

---

## Phase 4 — Writing

For each approved block:

**CREATE:** Create the file with minimal frontmatter:
```yaml
---
title: "[inferred title]"
type: "[type based on category]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: []
status: "active"
context_for_claude: true
source: "[block's source_id]"
ingested: YYYY-MM-DD
---
```
Then write `content` as the body of the note.

**APPEND:** Add `content` at the end of the existing file. Update `modified` in the frontmatter.

**UPDATE:** Replace the relevant section of the file. Update `modified` in the frontmatter. If you cannot identify the exact section, use APPEND and document the ambiguity.

Rules:
- Always check for overlap before CREATE: if a note about the same topic already exists, escalate to APPEND or UPDATE.
- `context_for_claude: true` is mandatory in all notes created or updated.
- `source` and `ingested` are mandatory when the origin is an external source file.

---

## Phase 5 — Post-ingestion

1. **Move processed source files** (if applicable): The adapter indicates whether the source files should be moved. For `raw/`, move to `raw/processed/`.

2. **Record in the backlog** the blocks that could not be processed (incompatible format, unresolved ambiguity, user rejection). File: `AI-SYSTEM/CONTEXT/ingestion-backlog.md`.

3. **Closing report:**
```
Ingestion completed from [source].

Operations executed: [N]
├── Notes created:      [N]
├── Notes updated:      [N]
└── Notes unchanged:    [N]

[If there is a backlog:]
Pending items recorded in AI-SYSTEM/CONTEXT/ingestion-backlog.md: [N]
```

---

## General rules

- The Phase 3 gate is **mandatory**. Without the user's approval, there is no writing.
- When in doubt about the target, prefer KNOWLEDGE over any other category.
- Never modify files in `raw/processed/`, `AI-SYSTEM/BOOTSTRAP/`, or this file.
- If the adapter produces no blocks (empty source or no useful content), inform the user and finish without error.
"""
        content = _inject_wolta_version(content, CLI_VERSION)
        protocol_file.write_text(content, encoding="utf-8")

    def _create_source_adapter_template(self) -> None:
        """Create TEMPLATES/template-source-adapter.md — template for building new source adapters."""
        templates_dir = self.vault_path / "TEMPLATES"
        templates_dir.mkdir(parents=True, exist_ok=True)
        template_file = templates_dir / "template-source-adapter.md"
        if template_file.exists():
            return

        content = """---
title: "Template: Source Adapter"
type: "template"
tags: ["template", "ingestion", "adapter"]
status: "active"
---

# Template: Source Adapter

Copy this file to `AI-SYSTEM/SKILLS/source-[name].md` and complete the sections marked with `[FILL IN]`.
Once completed, the agent will use it automatically when the user asks to ingest from that source.

---

## Adapter metadata

```yaml
source_id:    [FILL IN: unique identifier, e.g. "notion", "discord", "dropbox"]
source_type:  [FILL IN: "file" | "directory" | "api" | "chat" | other]
description:  [FILL IN: one line describing the source]
requires_mcp: [FILL IN: true if it needs an external MCP/tool, false if the user exports manually]
mcp_name:     [FILL IN if requires_mcp=true: name of the MCP or tool]
```

---

## When to activate this adapter

[FILL IN: list of natural-language triggers that indicate the user wants to use this source]

Examples:
- "ingest my information from [source name]"
- "explore [source name] and feed the KB"
- "[source name] has things I want in my KB"

---

## Extraction phase

Instructions for the agent to extract content from this source and turn it into `IngestionBlock`s.

### Pre-requisites

[FILL IN: what the user must have ready before the agent can extract]

Examples:
- Exported file dropped in `raw/`
- [name] MCP connected in Cowork
- Authenticated access to [URL/app]

### Extraction steps

[FILL IN: concrete steps the agent must follow]

1. [Step 1 — how to access the content]
2. [Step 2 — how to identify what is relevant for the KB]
3. [Step 3 — how to build each IngestionBlock]

### Relevance criteria

[FILL IN: what content from this source is worth ingesting and what should be ignored]

### Mapping to vault categories

[FILL IN: guide on how to map this source's content to the vault categories]

| Content type in [source] | Vault category | Suggested note |
|--------------------------|----------------|----------------|
| [type 1]                 | [CATEGORY]     | [note.md]      |
| [type 2]                 | [CATEGORY]     | [note.md]      |

---

## Post-extraction phase

[FILL IN: what to do with the source files/data after extracting the blocks]

Examples:
- Move the exported file to `raw/processed/`
- No action required (external source remains unchanged)
- Mark items in [source] as processed

---

## Additional notes

[FILL IN: any particularity of this source the agent should know]

---

*Adapter created:* [DATE]
*Based on:* INGEST-PROTOCOL.md
"""
        content = _inject_wolta_version(content, CLI_VERSION)
        template_file.write_text(content, encoding="utf-8")

    def _create_source_files_adapter(self) -> None:
        """Create AI-SYSTEM/SKILLS/source-files.md — reference adapter for raw/ and local directories."""
        skills_dir = self.vault_path / "AI-SYSTEM" / "SKILLS"
        skills_dir.mkdir(parents=True, exist_ok=True)
        adapter_file = skills_dir / "source-files.md"
        if adapter_file.exists():
            return

        content = """---
title: "Source Adapter: Local Files and Directories"
type: "skill"
context_for_claude: true
tags: ["ingestion", "adapter", "files", "raw"]
status: "active"
source_id: "files"
source_type: "file | directory"
requires_mcp: false
---

# Source Adapter: Local Files and Directories

Reference adapter for ingesting content from files dropped in `raw/` or from any local directory the agent has access to. It is the **universal fallback adapter**: use it when no specific adapter exists for the requested source.

---

## When to activate this adapter

- `/raw-ingest`
- "process the files in raw"
- "ingest the files from raw"
- "I have files in raw to process"
- "explore [directory] and feed the KB"
- "read [file path] and add it to my KB"
- When the user mentions a local file without a specific adapter

---

## Extraction phase

### Pre-requisites

For files in `raw/`: the user must have dropped the files in the vault's `raw/` directory.
For external directories: the agent must have read access to the indicated path.

### Extraction steps

**Case A — Files in `raw/`:**

1. List all files in `raw/` (exclude `raw/processed/` and `.gitkeep`)
2. For each file, determine whether it is processable:
   - Supported formats: `.md`, `.txt`, `.pdf`, `.docx`, any plain text
   - If the format is not processable, inform the user and continue with the next one
3. Read the content of each file
4. Split the content into thematic blocks (one block per identifiable topic)
5. For each block, build an `IngestionBlock`:
   - `source_id`: relative path of the file (`raw/file-name.ext`)
   - `source_type`: "file"
   - `suggested_category`: infer from the identified topics
   - `suggested_note`: infer from the content (descriptive name in lowercase with hyphens)
   - `operation`: CREATE if no similar note exists, APPEND or UPDATE if one already exists

**Case B — External local directory:**

1. List the files in the directory indicated by the user
2. Ask the user whether to process subfolders recursively
3. Filter by processable formats (same as Case A)
4. Follow steps 3–5 of Case A

### Relevance criteria

Include in the extraction:
- Personal information (identity, values, history)
- Professional context (projects, roles, companies)
- Learning notes (concepts, resources, synthesis)
- Documented preferences and habits

Ignore:
- Technical configuration files with no personal content
- Temporary or cache files
- Duplicate content already present in the vault

### Mapping to vault categories

| Content type | Category | Suggested note |
|--------------|----------|----------------|
| Personal information, bio, history | IDENTITY | identity-profile.md or new note |
| Values, principles | IDENTITY | identity-values.md |
| Work style, tools | PREFERENCES | preferences-work-style.md or preferences-tools.md |
| Work context, company | WORK | work-company.md or work-current-role.md |
| Specific project | PROJECTS | PROJECTS/[project-name]/ |
| Hobbies, personal interests | PERSONAL-SPACE | personal-hobbies.md or personal-interests.md |
| Learning, concepts, resources | KNOWLEDGE | new note in KNOWLEDGE/ |

---

## Post-extraction phase

For files processed from `raw/`:
- Move each processed file to `raw/processed/`
- Do not delete files in `raw/processed/`

For files from external directories:
- Do not move or modify the source files
- Only record `source_id` with the full path in the frontmatter of the created notes

---

## Additional notes

- A source file can produce multiple blocks and therefore multiple notes
- If a file is very long (>1000 lines), process it by sections and confirm with the user before continuing
- Files in `raw/` that the user marked as "do not process" (with the `_` prefix) must be ignored
- This adapter is the fallback: if the user asks to ingest from a source without an adapter, offer to export the content to `raw/` to use it with this adapter
"""
        content = _inject_wolta_version(content, CLI_VERSION)
        adapter_file.write_text(content, encoding="utf-8")

    def _create_readme_file(self) -> None:
        """Create README.md quick start guide in vault root."""
        readme_file = self.vault_path / "README.md"
        if readme_file.exists():
            return

        content = """# KB-PERSONAL: Quick Start Guide

Welcome to your Personal Knowledge Base. This vault is designed to centralize personal and professional information so it can be queried by Claude agents.

---

## What's here?

**7 main modules + agent resources:**

| Folder | Purpose |
|--------|---------|
| **IDENTITY/** | Who you are (profile, values, voice, biography) |
| **PREFERENCES/** | Tastes, tools, work style |
| **WORK/** | Professional context (company, role, team) |
| **PROJECTS/** | Active and past projects |
| **PERSONAL-SPACE/** | Personal content (hobbies, interests) |
| **KNOWLEDGE/** | Education (courses, research, learning) |
| **AI-SYSTEM/** | Resources for Claude agents (bootstrap, context, workflows) |

---

## First Steps (5 minutes)

### 1. Set up Obsidian
- Open Obsidian
- Click: File → Open folder as vault
- Select this folder

### 2. Explore the structure
- Left panel: File Explorer
- Open each folder (e.g. IDENTITY/, WORK/)
- Note the INDEX-* files (they are the hubs of each module)

### 3. Read the DESIGN
- Open `DESIGN.md` in the root
- It defines the complete specification of this vault
- Reference for understanding frontmatter, tags, and structure

---

## Next: Bootstrap (45-90 minutes)

The **AI-SYSTEM/BOOTSTRAP/** folder contains tools to populate your vault from day one.

### Flow:

1. **Navigate to:** `AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md`
   - Read the bootstrap hub
   - Understand the flow

2. **Answer:** `BOOTSTRAP-QUESTIONNAIRE.md`
   - 27 reflective questions across 6 categories
   - 2-5 paragraphs per question
   - Estimated time: 45-90 minutes

3. **Map:** `BOOTSTRAP-MAPPING.md`
   - See where each answer goes
   - Each question → target note

4. **Create notes:**
   - Use the template in `TEMPLATES/template-note.md`
   - Follow the frontmatter pattern
   - Respect the folder structure

5. **Update the graph:**
   ```bash
   graphify /path/to/vault --update --no-cluster
   ```

---

## Folder Structure (Visual)

```
vault/
├── IDENTITY/
│   ├── INDEX-IDENTITY.md         ← Start here to get to know yourself
│   ├── identity-profile.md
│   ├── identity-values.md
│   ├── identity-voice.md
│   └── identity-bio.md
│
├── PREFERENCES/
│   ├── INDEX-PREFERENCES.md      ← Your personal settings
│   ├── preferences-tools.md
│   ├── preferences-work-style.md
│   └── preferences-lifestyle.md
│
├── WORK/
│   ├── INDEX-WORK.md             ← Your professional context
│   ├── work-overview.md
│   ├── work-current-role.md
│   ├── work-company.md
│   └── work-team.md
│
├── PROJECTS/
│   └── INDEX-PROJECTS.md         ← Your projects (active/past)
│
├── PERSONAL-SPACE/
│   ├── INDEX-PERSONAL-SPACE.md   ← Your personal content
│   ├── personal-hobbies.md
│   └── personal-interests.md
│
├── KNOWLEDGE/
│   └── INDEX-KNOWLEDGE.md        ← Your learning and education
│
├── AI-SYSTEM/                    ← Resources for agents
│   ├── INDEX-AI-SYSTEM.md
│   ├── BOOTSTRAP/
│   │   ├── INDEX-BOOTSTRAP.md           ← START HERE for bootstrap
│   │   ├── BOOTSTRAP-QUESTIONNAIRE.md   ← 27 questions
│   │   └── BOOTSTRAP-MAPPING.md         ← Question→note mapping
│   ├── AGENTS/
│   ├── CONTEXT/
│   ├── SESSIONS/
│   ├── SKILLS/
│   │   ├── bootstrap-generate.md        ← Skill: /bootstrap-generate
│   │   └── raw-ingest.md                ← Skill: /raw-ingest
│   └── WORKFLOWS/
│
├── TEMPLATES/
│   └── template-note.md          ← Template for new notes
│
├── raw/                          ← Staging for unprocessed files
│   ├── processed/                ← Already processed files (audit)
│   └── README.md                 ← Directory rules
│
├── DESIGN.md                     ← Complete specification
├── README.md                     ← This file
│
└── graphify-out/                 ← Generated graph (queried by the agent)
    ├── graph.json
    ├── GRAPH_REPORT.md
    └── graph.html
```

---

## Frontmatter: The Foundation of Everything

Every `.md` note needs YAML frontmatter:

```yaml
---
title: "Your Note"
type: "identity | preference | work | project | knowledge | personal"
created: 2026-05-22
modified: 2026-05-22
tags: [tag1, tag2]
status: "active"
context_for_claude: true
---
```

**Key field:** `context_for_claude: true` → The agent queries it

---

## Knowledge Graph

After populating notes with bootstrap, run:

```bash
graphify /path/to/vault --update --no-cluster
```

This generates:
- `graph.json` — Queryable by agents
- `graph.html` — Open in a browser to visualize
- `GRAPH_REPORT.md` — Relationship analysis

---

## Checklist: First Session

- [ ] Obsidian configured (File → Open folder as vault)
- [ ] Read DESIGN.md (5 minutes)
- [ ] Explored the structure in the File Explorer
- [ ] Opened AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md
- [ ] Started answering BOOTSTRAP-QUESTIONNAIRE.md

---

## Resources

- **DESIGN.md** — Complete technical specification
- **AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md** — Bootstrap hub
- **AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md** — The 27 questions
- **AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md** — Mapping guide
- **TEMPLATES/template-note.md** — Standard template

---

**Created:** {created}
**Last updated:** {created}
**Version:** 1.0.0
""".format(created=datetime.now().strftime("%Y-%m-%d"))

        readme_file.write_text(content, encoding="utf-8")
