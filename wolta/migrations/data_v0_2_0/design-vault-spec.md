# DESIGN — KB-PERSONAL Specification

**Vault:** KB-PERSONAL
**Schema:** 0.2.0
**Status:** Active

---

## 1. Vault Goal

Centralize personal and professional information in a Knowledge Base that Claude agents can query. A hybrid PARA + Zettelkasten system for maximum flexibility.

---

## 2. The two spaces

From schema 0.2.0 the vault is split at the root by **ownership**:

| Space | Owner | Policy | Agent reads | Agent writes |
| --- | --- | --- | --- | --- |
| `SYSTEM/` | wolta and the agent | managed, managed-section and user-owned, per file | Freely | Freely |
| `HUMAN/` | The user | User-owned, in full and explicitly | On request | Only when the user asks |

`HUMAN/` is born empty and has no fixed structure — the user shapes it. It is **not part of the knowledge base**: it is an ingestion source, raw material the agent may be pointed at, not curated truth. The knowledge base proper is everything under `SYSTEM/`.

The boundary is a **policy, not a technical lock**. Nothing in the filesystem prevents a write into `HUMAN/`; the rule lives in `CLAUDE.md` and is enforced by the agent's own discipline.

Three artifacts stay at the root and belong to neither space: `.wolta/` marks the vault and stores its schema state, `CLAUDE.md` is auto-loaded when the vault is opened as a project, and `README.md` is the entry point for a person.

---

## 3. Folder Structure

```
wolta-vault/
├── HUMAN/                  # The user's space — born empty, no fixed structure
│   └── .gitkeep
│
├── SYSTEM/                 # The agent's space — this is the knowledge base
│   ├── IDENTITY/           # Who you are: profile, values, history, voice
│   │   ├── INDEX-IDENTITY.md
│   │   ├── identity-profile.md
│   │   ├── identity-values.md
│   │   ├── identity-voice.md
│   │   └── identity-bio.md
│   │
│   ├── PREFERENCES/        # Tastes, habits, personal settings
│   │   ├── INDEX-PREFERENCES.md
│   │   ├── preferences-tools.md
│   │   ├── preferences-work-style.md
│   │   └── preferences-lifestyle.md
│   │
│   ├── WORK/               # Professional context: company, role, team
│   │   ├── INDEX-WORK.md
│   │   ├── work-overview.md
│   │   ├── work-current-role.md
│   │   ├── work-company.md
│   │   └── work-team.md
│   │
│   ├── PROJECTS/           # Active and past projects
│   │   └── INDEX-PROJECTS.md
│   │
│   ├── PERSONAL-SPACE/     # Everyday content: movies, books, quotes
│   │   ├── INDEX-PERSONAL-SPACE.md
│   │   ├── personal-hobbies.md
│   │   └── personal-interests.md
│   │
│   ├── KNOWLEDGE/          # Educational content: courses, studies, research
│   │   └── INDEX-KNOWLEDGE.md
│   │
│   ├── AI-SYSTEM/          # Operational resources for the agent
│   │   ├── INDEX-AI-SYSTEM.md
│   │   ├── BOOTSTRAP/      # Initial population of the KB
│   │   │   ├── INDEX-BOOTSTRAP.md
│   │   │   ├── BOOTSTRAP-QUESTIONNAIRE.md
│   │   │   └── BOOTSTRAP-MAPPING.md
│   │   ├── AGENTS/         # Agent definitions
│   │   ├── CONTEXT/        # Current agent context
│   │   │   └── context-current.md
│   │   ├── SESSIONS/       # Session history
│   │   ├── SKILLS/         # Available skills and prompts
│   │   └── WORKFLOWS/      # Workflows and automations
│   │
│   ├── TEMPLATES/          # Templates for new notes
│   │   ├── template-note.md
│   │   └── template-source-adapter.md
│   │
│   ├── raw/                # Staging for unprocessed source files
│   │   ├── processed/      # Already processed files (audit)
│   │   └── README.md       # Directory rules
│   │
│   └── DESIGN.md           # This document (vault specification)
│
├── .wolta/                 # Vault marker and schema state
├── CLAUDE.md               # Instructions loaded by the agent
├── README.md               # Quick start guide
│
└── graphify-out/           # Generated knowledge graph
    ├── graph.json          # Queryable structure
    ├── GRAPH_REPORT.md     # Graph analysis
    └── graph.html          # Interactive visualization
```

---

## 4. Standard Frontmatter

Every .md file under `SYSTEM/` must include:

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

Files in `HUMAN/` have no frontmatter requirement. They are the user's, in whatever shape the user wants.

---

## 5. Tag System

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

## 6. Bootstrap: Initial Population

### Folder: `SYSTEM/AI-SYSTEM/BOOTSTRAP/`

**Operational hub for the initial population of the KB.**

1. **INDEX-BOOTSTRAP.md** — Navigation hub and checklist
2. **BOOTSTRAP-QUESTIONNAIRE.md** — Reflective questions (45-90 minutes)
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

## 7. Knowledge Graph (Graphify)

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

## 8. Upgrading from 0.1.0

A vault created before 0.2.0 kept the seven categories at the root. `wolta upgrade` relocates them under `SYSTEM/` with a single rename each, creates the empty `HUMAN/`, and refreshes this document. Nothing is copied and nothing is merged: if a destination already exists, the upgrade stops and asks for a human decision rather than guessing.

Two things the upgrade deliberately leaves alone, because they are not wolta's to touch:

- **Obsidian configuration** (`.obsidian/`). Saved searches, starred notes, and workspace layouts may point at the old root paths. Review them after upgrading.
- **The generated graph** (`graphify-out/`). Re-run graphify to regenerate it against the new paths.

---

## 9. Next Steps

1. Open the vault in Obsidian
2. Explore the structure in the File Explorer
3. Read README.md for a quick guide
4. Navigate to `SYSTEM/AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md` to begin
5. Answer BOOTSTRAP-QUESTIONNAIRE.md
6. Run graphify to update the graph

---

**Status:** Active — Ready for use once bootstrap is completed
