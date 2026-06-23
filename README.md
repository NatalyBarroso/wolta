# Wolta CLI - Personal Knowledge Base Initializer

Command-line tool to initialize and manage a personal knowledge base in Obsidian, integrated with Claude agents for intelligent queries.

## Description

Wolta creates a structured Obsidian vault with predefined categories and bootstrap questions to complete your knowledge base from day one. The vault is designed to be queried by Claude agents with full contextual understanding.

**Vault Structure:**
- **IDENTITY** - Personal profile, values, voice
- **PREFERENCES** - Tools, work style, lifestyle
- **WORK** - Current role, company, team information
- **PROJECTS** - Active projects and status
- **PERSONAL-SPACE** - Hobbies and interests
- **KNOWLEDGE** - Learning resources
- **AI-SYSTEM** - Agent context, workflows, skills
  - **BOOTSTRAP** - Initial questions to complete
  - **CONTEXT** - Current context
  - **AGENTS** - Agent configuration
  - **SESSIONS** - Session history
  - **SKILLS** - Custom skills
  - **WORKFLOWS** - Workflows

## Installation

### Option 1: With pip (classic)

```bash
pip install -e .
```

Then use the global command:
```bash
wolta init
```

### Option 2: With uv (recommended - faster)

```bash
uv pip install -e .
```

Then use the global command:
```bash
wolta init
```

### Option 3: Direct execution with Python

```bash
python main.py init
```

Or with uv:
```bash
uv run main.py init
```

## Usage

### Basic initialization

Initialize a vault in the current directory:
```bash
wolta init
```

Creates a `wolta/` folder with the default structure.

### Custom name for the vault

Customize the name of the vault folder:
```bash
wolta init --name joanna
```

Creates: `wolta-joanna/` instead of `wolta/`

### Custom path

Specify where the vault should be created:
```bash
wolta init --vault-path ~/Documents
```

### Combined options

```bash
wolta init --vault-path ~/Documents --name my-kb
```

Creates: `~/Documents/wolta-my-kb/`

### Force re-initialization

Re-initialize an existing vault (overwrites):
```bash
wolta init --name joanna --force
```

## Command Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--vault-path` | Path | Current directory | Directory where the vault will be created |
| `--name` | String | `wolta` | Custom name for the folder (creates `wolta-[name]/`) |
| `--force` | Flag | False | Forces the re-initialization of an existing vault |
| `--help` | Flag | - | Shows the help message |
| `--version` | Flag | - | Shows the version number |

## Name Validation

Vault names must follow these rules:
- Only alphanumeric characters and hyphens
- 1-50 characters long
- Cannot start or end with a hyphen

**Valid examples:**
- `my-kb`
- `joanna123`
- `kb-2026`

**Invalid examples:**
- `-invalid` (starts with a hyphen)
- `invalid-` (ends with a hyphen)
- `invalid name` (contains spaces)

## Output

After a successful initialization:

```
✓ Vault initialized successfully!
  Vault location: ~/Documents/wolta-joanna
  Vault name: wolta-joanna

Next steps:
  1. Open the vault in Obsidian: File → Open folder as vault
  2. Navigate to: ~/Documents/wolta-joanna
  3. Complete the bootstrap questions in AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

## Generated Structure

### Folders (8 main + subfolders)
```
wolta-[name]/
├── IDENTITY/
├── PREFERENCES/
├── WORK/
├── PROJECTS/
├── PERSONAL-SPACE/
├── KNOWLEDGE/
├── AI-SYSTEM/
│   ├── AGENTS/
│   ├── BOOTSTRAP/
│   ├── CONTEXT/
│   ├── SESSIONS/
│   ├── SKILLS/
│   └── WORKFLOWS/
├── TEMPLATES/
└── .wolta/
```

### Created Files
- INDEX files for each category (e.g. `INDEX-IDENTITY.md`)
- Category-specific files with YAML frontmatter
- Bootstrap questions file: `AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md`
- Template file: `TEMPLATES/template-note.md`
- Configuration marker: `.wolta/initialized`

## Bootstrap Questions

After initialization, complete the bootstrap questions in:
```
AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

Or ask the agent to start generating the note templates.
```
"Start the bootstrap"
```

These questions cover 27 topics across 6 categories:

- **IDENTITY** (6 questions) - Who you are, values, communication
- **PREFERENCES** (6 questions) - How you work, tools, lifestyle
- **WORK** (5 questions) - Role, company, team, career
- **PROJECTS** (4 questions) - Current and future projects
- **PERSONAL-SPACE** (5 questions) - Entertainment, music, learning
- **KNOWLEDGE** (5 questions) - Areas of specialty and learning

## Frontmatter Specification

All generated files include YAML frontmatter:

```yaml
---
title: "[File Title]"
type: "identity | preference | work | project | knowledge | personal"
created: 2026-05-19
modified: 2026-05-19
tags: []
status: "active"
---
```

## Development

### Run tests

```bash
pytest
```

### Code style

Format with Black:
```bash
black .
```

Lint with Ruff:
```bash
ruff check .
```

## Architecture

- `main.py` - Entry point for `python main.py` and `uv run main.py`
- `wolta/cli.py` - Click CLI group and command registration
- `wolta/commands/init.py` - init command implementation
- `wolta/generators/structure.py` - Folder structure generator
- `wolta/generators/bootstrap.py` - Bootstrap questions generator
- `wolta/utils/validators.py` - Validation utilities

## Next Steps

After initializing your vault:

1. **Open in Obsidian** - File → Open folder as vault
2. **Configure Obsidian** - Settings → Configure the vault name, templates, attachments
3. **Answer the Bootstrap Questions** - Complete `AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md`
4. **Populate Categories** - Fill in your information across all categories
5. **Generate the Knowledge Graph** - Use the Graphify CLI for a queryable representation

## License

Personal project for knowledge base management.

## Author

Nataly Barroso (barrosonataly.dev@gmail.com)
