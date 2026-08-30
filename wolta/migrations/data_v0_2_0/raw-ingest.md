---
wolta_version: "0.2.0"
title: "SKILL — raw-ingest"
type: "skill"
created: 2026-08-29
modified: 2026-08-29
tags: [skill, ingestion, raw, agent]
status: "active"
context_for_claude: true
---

# SKILL: raw-ingest

**Purpose:** Process files dropped in `SYSTEM/raw/` and turn them into valid KB notes. This skill can be run multiple times over the life of the vault: every time the owner wants to ingest new material.

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

**1. Verify that there are files in `SYSTEM/raw/`**
List the files in `SYSTEM/raw/` (exclude `SYSTEM/raw/processed/`, `SYSTEM/raw/README.md`, and `SYSTEM/raw/.gitkeep`).

If there are no files, respond:
```
There are no files in SYSTEM/raw/ to process.
To start an ingestion, drop files in SYSTEM/raw/ and run /raw-ingest again.
Supported formats: .md, .txt, .pdf, .docx
```
And stop execution.

**2. Verify write access to the vault**
Confirm that you can create and move files. If not, inform the user and stop.

---

## Step 1 — Inventory available files

List all files in `SYSTEM/raw/` with their name and extension. Present to the user:

```
Files found in SYSTEM/raw/:
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
✓ Created: SYSTEM/IDENTITY/identity-profile.md
✓ Updated: SYSTEM/WORK/work-current-role.md
...
```

---

## Step 5 — Move processed files

When you finish processing each source file, move it from `SYSTEM/raw/` to `SYSTEM/raw/processed/`.

```
SYSTEM/raw/cv-nataly-2026.pdf  →  SYSTEM/raw/processed/cv-nataly-2026.pdf
```

**Do not delete the files.** They serve as an audit trail of what information entered the vault and when.

---

## Step 6 — Record backlog (if applicable)

If the 2h timebox runs out before processing everything, or if there are blocks the user rejected but are valid for the future, record them in `SYSTEM/AI-SYSTEM/CONTEXT/ingestion-backlog.md`:

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
└── Moved to SYSTEM/raw/processed/

[If there is a backlog:]
Pending items recorded in SYSTEM/AI-SYSTEM/CONTEXT/ingestion-backlog.md: [N]
```

---

## Rules

- The Step 3 gate is mandatory. Do not write to the vault without the user's approval.
- Detect overlap before creating: if a note about the same topic already exists, prefer APPEND or UPDATE over a duplicate CREATE.
- If a file in `SYSTEM/raw/` is not processable (incompatible format, corrupt, no useful content), inform the user and continue with the next one.
- Do not modify files in `SYSTEM/raw/processed/` or in `SYSTEM/AI-SYSTEM/BOOTSTRAP/`.
- The `context_for_claude: true` field is mandatory in all notes created or updated.
