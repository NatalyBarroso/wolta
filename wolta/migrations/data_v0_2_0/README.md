# KB-PERSONAL: Quick Start Guide

Welcome to your Personal Knowledge Base. This vault centralizes your personal and professional information so it can be queried by Claude agents.

---

## The two spaces

The vault has two folders at the root, and the difference between them is **who owns them**:

| Space | Yours or the agent's | What goes in it |
| --- | --- | --- |
| `HUMAN/` | **Yours.** The agent only writes here when you ask it to | Anything you want, in any shape. Drafts, exports, working files |
| `SYSTEM/` | The agent's. It reads and writes here freely | The knowledge base itself: the seven categories and the agent's tooling |

`HUMAN/` starts empty and stays however you leave it — wolta does not impose a structure on your own space and will not reorganize it. It is also **not part of the knowledge base**: the agent will not read it as background context. Point the agent at a file there when you want it ingested, and the curated result lands in `SYSTEM/`.

Three files stay at the root: `.wolta/` (how wolta recognizes the vault), `CLAUDE.md` (loaded automatically by the agent), and this README.

---

## What's in the agent's space?

**7 main modules + agent resources, all under `SYSTEM/`:**

| Folder | Purpose |
|--------|---------|
| **`SYSTEM/IDENTITY/`** | Who you are (profile, values, voice, biography) |
| **`SYSTEM/PREFERENCES/`** | Tastes, tools, work style |
| **`SYSTEM/WORK/`** | Professional context (company, role, team) |
| **`SYSTEM/PROJECTS/`** | Active and past projects |
| **`SYSTEM/PERSONAL-SPACE/`** | Personal content (hobbies, interests) |
| **`SYSTEM/KNOWLEDGE/`** | Education (courses, research, learning) |
| **`SYSTEM/AI-SYSTEM/`** | Resources for Claude agents (bootstrap, context, workflows) |

---

## First Steps (5 minutes)

### 1. Set up Obsidian
- Open Obsidian
- Click: File → Open folder as vault
- Select this folder

### 2. Explore the structure
- Left panel: File Explorer
- Open `SYSTEM/` and look through the categories
- Note the INDEX-* files (they are the hubs of each module)

### 3. Read the DESIGN
- Open `SYSTEM/DESIGN.md`
- It defines the complete specification of this vault
- Reference for understanding frontmatter, tags, and structure

---

## Next: Bootstrap (45-90 minutes)

The `SYSTEM/AI-SYSTEM/BOOTSTRAP/` folder contains tools to populate your vault from day one.

### Flow:

1. **Navigate to:** `SYSTEM/AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md`
   - Read the bootstrap hub
   - Understand the flow

2. **Answer:** `BOOTSTRAP-QUESTIONNAIRE.md`
   - Reflective questions across 6 categories
   - 2-5 paragraphs per question
   - Estimated time: 45-90 minutes

3. **Map:** `BOOTSTRAP-MAPPING.md`
   - See where each answer goes
   - Each question → target note

4. **Create notes:**
   - Use the template in `SYSTEM/TEMPLATES/template-note.md`
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
├── HUMAN/                        ← Your space. Starts empty, shaped by you
│
├── SYSTEM/                       ← The agent's space
│   ├── IDENTITY/
│   │   ├── INDEX-IDENTITY.md     ← Start here to get to know yourself
│   │   ├── identity-profile.md
│   │   ├── identity-values.md
│   │   ├── identity-voice.md
│   │   └── identity-bio.md
│   │
│   ├── PREFERENCES/
│   │   ├── INDEX-PREFERENCES.md  ← Your personal settings
│   │   ├── preferences-tools.md
│   │   ├── preferences-work-style.md
│   │   └── preferences-lifestyle.md
│   │
│   ├── WORK/
│   │   ├── INDEX-WORK.md         ← Your professional context
│   │   ├── work-overview.md
│   │   ├── work-current-role.md
│   │   ├── work-company.md
│   │   └── work-team.md
│   │
│   ├── PROJECTS/
│   │   └── INDEX-PROJECTS.md     ← Your projects (active/past)
│   │
│   ├── PERSONAL-SPACE/
│   │   ├── INDEX-PERSONAL-SPACE.md
│   │   ├── personal-hobbies.md
│   │   └── personal-interests.md
│   │
│   ├── KNOWLEDGE/
│   │   └── INDEX-KNOWLEDGE.md    ← Your learning and education
│   │
│   ├── AI-SYSTEM/                ← Resources for agents
│   │   ├── INDEX-AI-SYSTEM.md
│   │   ├── BOOTSTRAP/
│   │   │   ├── INDEX-BOOTSTRAP.md         ← START HERE for bootstrap
│   │   │   ├── BOOTSTRAP-QUESTIONNAIRE.md
│   │   │   └── BOOTSTRAP-MAPPING.md
│   │   ├── AGENTS/
│   │   ├── CONTEXT/
│   │   ├── SESSIONS/
│   │   ├── SKILLS/
│   │   │   ├── bootstrap-generate.md      ← Skill: /bootstrap-generate
│   │   │   └── raw-ingest.md              ← Skill: /raw-ingest
│   │   └── WORKFLOWS/
│   │
│   ├── TEMPLATES/
│   │   └── template-note.md      ← Template for new notes
│   │
│   ├── raw/                      ← Staging for unprocessed files
│   │   ├── processed/            ← Already processed files (audit)
│   │   └── README.md             ← Directory rules
│   │
│   └── DESIGN.md                 ← Complete specification
│
├── .wolta/                       ← Vault marker and schema state
├── CLAUDE.md                     ← Instructions for the agent
├── README.md                     ← This file
│
└── graphify-out/                 ← Generated graph (queried by the agent)
    ├── graph.json
    ├── GRAPH_REPORT.md
    └── graph.html
```

---

## Frontmatter: The Foundation of Everything

Every `.md` note under `SYSTEM/` needs YAML frontmatter:

```yaml
---
title: "Your Note"
type: "identity | preference | work | project | knowledge | personal"
created: 2026-01-15
modified: 2026-01-15
tags: [tag1, tag2]
status: "active"
context_for_claude: true
---
```

**Key field:** `context_for_claude: true` → The agent queries it

Your own files in `HUMAN/` need none of this.

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

## Coming from a 0.1.0 vault?

`wolta upgrade` moved the seven categories from the root into `SYSTEM/` and created your empty `HUMAN/`. Your notes were renamed, not copied — content, history, and timestamps are untouched.

Two things the upgrade left alone on purpose, because they are not wolta's to change:

- **Obsidian's own configuration** (`.obsidian/`). Saved searches, starred notes, and workspace layouts may still point at the old root paths. Worth a look.
- **The generated graph** (`graphify-out/`). Re-run graphify to rebuild it against the new paths.

Nothing else needs your attention: links between notes are relative to the vault and kept working through the move.

---

## Checklist: First Session

- [ ] Obsidian configured (File → Open folder as vault)
- [ ] Read `SYSTEM/DESIGN.md` (5 minutes)
- [ ] Explored the structure in the File Explorer
- [ ] Opened `SYSTEM/AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md`
- [ ] Started answering BOOTSTRAP-QUESTIONNAIRE.md

---

## Resources

- **`SYSTEM/DESIGN.md`** — Complete technical specification
- **`SYSTEM/AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md`** — Bootstrap hub
- **`SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md`** — The questions
- **`SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md`** — Mapping guide
- **`SYSTEM/TEMPLATES/template-note.md`** — Standard template

---

**Schema version:** 0.2.0
