This vault is a **personal knowledge base** built with Obsidian and designed to be queried and operated by Claude agents. It contains the owner's personal, professional, and learning information.

---

## The two spaces of the vault

A 0.2.0 vault has two root folders, and the difference between them is one of **ownership**, not of content:

| Space | Owner | The agent reads | The agent writes |
| --- | --- | --- | --- |
| `SYSTEM/` | wolta and the agent | Freely — this is the knowledge base | Freely — add, edit, and remove as the work requires |
| `HUMAN/` | The user | Freely, but **only when asked** | **Only** on an explicit instruction from the user, or inside an automated flow the user started |

Two consequences that change how you must behave:

1. **`HUMAN/` is not part of the knowledge base.** A file is not context just because it sits there. `HUMAN/` is an *ingestion source*: raw, uncurated material the user keeps for themselves. Never load it as background context, never cite it as the vault's answer, and never let it override a curated note in `SYSTEM/`.
2. **The boundary is a policy, not a lock.** Nothing in the filesystem stops you from writing into `HUMAN/`. This document is the only thing that does. Treat a write into the user's space as you would any destructive action: ask first.

`.wolta/`, `CLAUDE.md`, and `README.md` stay at the root. `.wolta/` identifies the vault and holds its schema state, this file is loaded automatically when the vault is opened as a project, and `README.md` is the first thing a person sees when they open the folder.

---

## Vault context

When the user connects this vault as a project, this file is loaded automatically. The agent must:

1. Recognize that it is operating inside a WOLTA vault
2. Read the files with `context_for_claude: true` under `SYSTEM/` to build the user's context
3. Answer queries using the vault content as the primary source of truth
4. Use the skills available in `SYSTEM/AI-SYSTEM/SKILLS/` for structured operations

---

## Fixed commands

### `/bootstrap-generate`

**File:** `SYSTEM/AI-SYSTEM/SKILLS/bootstrap-generate.md`
**When:** When the user has completed the bootstrap questionnaire and wants to turn their answers into vault notes.

Triggers:
- `/bootstrap-generate`
- "generate the notes for my knowledge base"
- "create the bootstrap notes"
- "populate the kb"
- "turn the answers into notes"

---

## Ingestion from external sources

The vault uses an extensible ingestion system. The core protocol is in `SYSTEM/AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md`. The **source adapters** are skills in `SYSTEM/AI-SYSTEM/SKILLS/` with the `source-` prefix that describe how to extract information from a specific source and produce blocks compatible with the protocol.

### How to respond when the user asks to ingest information

**Step 1 — Identify the source**
Determine where the information comes from: local files, a directory, the user's own `HUMAN/` space, an external app (Notion, Discord, etc.), content from the active conversation, or any other origin.

**Step 2 — Look for an adapter for that source**
List the files in `SYSTEM/AI-SYSTEM/SKILLS/` that match the `source-*.md` pattern.
Read the one that corresponds to the requested source.

**Step 3 — If the adapter exists**
Follow its instructions for the extraction phase, then continue with `INGEST-PROTOCOL.md` for classification, gate, writing, and tracking.

**Step 4 — If the adapter does NOT exist**
Present the user with two options:
```
I do not have an adapter configured for [source].
Options:
  a) Export the content manually to SYSTEM/raw/ and run /raw-ingest
  b) Create an adapter for [source] using SYSTEM/TEMPLATES/template-source-adapter.md
     (you only need to fill in the marked sections — takes ~10 minutes)
```

**Step 5 — Ingestion from the active conversation**
If, during a conversation, the user explains something relevant to the KB (project context, technical decision, personal information), you can propose ingesting it directly:
```
That looks like valuable information for your KB.
Do you want me to add it to [suggested target note]?
```
Do not ingest without the user's confirmation. Information from the active conversation does not need to go through a source file.

**Step 6 — Ingestion from `HUMAN/`**
If the user asks you to feed the KB from their own space, read the files they point at and run them through the same protocol. The result lands in `SYSTEM/`; the originals in `HUMAN/` are left exactly as they were. Do not go looking through `HUMAN/` on your own initiative.

### General ingestion triggers (any source)

- "ingest my information from [source]"
- "explore [directory/app] and feed the KB"
- "add this to my KB"
- "process [source] as notes"
- "/ingest [source]"

---

## The staging directory

`SYSTEM/raw/` is the **universal fallback adapter**: any source without an adapter can use this directory as a manual bridge. The corresponding adapter is `SYSTEM/AI-SYSTEM/SKILLS/source-files.md`.

Operational rules:
1. Files in `SYSTEM/raw/` are not valid notes — do not read them as KB context
2. Do not write to the vault without the user's approval (gate in INGEST-PROTOCOL.md)
3. When processing a file, move it to `SYSTEM/raw/processed/` — never delete it
4. Attribute the source: add `source` and `ingested` to the frontmatter of notes created this way

---

## How to query the KB

1. Always prioritize the vault content over your training knowledge for the user's data
2. Files under `SYSTEM/` with `context_for_claude: true` are primary sources
3. If the information is not in the vault, say so explicitly instead of inferring it
4. Never answer from `HUMAN/` unless the user pointed you at it in this conversation

---

## Vault structure

```
├── HUMAN/                → The user's space. Not the KB. Read on request only
│
├── SYSTEM/               → The agent's space
│   ├── IDENTITY/         → Owner's profile, values, history, voice
│   ├── PREFERENCES/      → Work style, tools, habits
│   ├── WORK/             → Current role, company, team, career
│   ├── PROJECTS/         → Active, future, and proud projects
│   ├── PERSONAL-SPACE/   → Hobbies, cultural interests, quotes
│   ├── KNOWLEDGE/        → Current learning, expertise, sources
│   ├── AI-SYSTEM/        → Operational resources for the agent
│   │   ├── BOOTSTRAP/    → Initial ingestion questionnaire and mapping
│   │   ├── SKILLS/       → Agent skills
│   │   │   ├── INGEST-PROTOCOL.md     → Canonical ingestion pipeline
│   │   │   ├── source-*.md            → Source adapters (one per source)
│   │   │   └── bootstrap-generate.md  → Initial population skill
│   │   ├── CONTEXT/      → Dynamic session context
│   │   ├── SESSIONS/     → Session history
│   │   └── WORKFLOWS/    → Automated workflows
│   ├── TEMPLATES/        → template-source-adapter.md and note templates
│   ├── raw/              → Universal fallback staging (do NOT read as KB)
│   │   └── processed/    → Processed files (audit)
│   └── DESIGN.md         → Vault specification
│
├── .wolta/               → Vault marker and schema state
├── CLAUDE.md             → This file
└── README.md             → Entry point for a person
```

---

## Bootstrap status

Read `SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` → `status` field in frontmatter.
If `kb_populated: true`, the vault has already been populated. If not, the notes have not yet been generated.

---

## KB conventions

- Every relevant file under `SYSTEM/` has `context_for_claude: true` in its frontmatter
- Internal links: `[[note-name]]`
- `status`: `active`, `draft`, or `archived`
- Notes under `SYSTEM/PROJECTS/` with `status: archived` are historical
