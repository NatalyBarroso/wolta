---
wolta_version: "0.1.0"
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
