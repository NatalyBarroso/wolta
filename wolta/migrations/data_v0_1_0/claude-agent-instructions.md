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

*Generated by wolta init · 2026-06-21*