---
wolta_version: "0.1.0"
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
