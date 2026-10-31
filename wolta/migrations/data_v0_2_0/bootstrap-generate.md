---
wolta_version: "0.2.0"
title: "SKILL — bootstrap-generate"
type: "skill"
created: 2026-08-29
modified: 2026-08-29
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
Read `SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md`.
Verify that the frontmatter contains `status: "completed"` and that all 31 questions have an answer (they must not be empty nor contain only the text `[Your answer here]`).

If the questionnaire is not complete, respond:
```
The bootstrap questionnaire is not complete yet.
Navigate to SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md and answer
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
SYSTEM/IDENTITY/, SYSTEM/PREFERENCES/, SYSTEM/WORK/,
SYSTEM/PROJECTS/, SYSTEM/PERSONAL-SPACE/, SYSTEM/KNOWLEDGE/

Shall I proceed? (yes / no)
```

---

## Inputs you need to read

1. `SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` — source of all answers
2. `SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md` — question → target note mapping table

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
- Location: `SYSTEM/PROJECTS/`
- Extract from the text the name, status, and description of each project

The same applies to future projects (`P.PROJ.2`) and proud projects (`P.PROJ.3`).
`INDEX-PROJECTS.md` receives only the content of `P.PROJ.4`.

### Step 5 — Create each note

For each target note:

1. **Check whether it already exists.** If it exists with real content, ask the user whether they want to overwrite it before proceeding.
2. **Write the frontmatter** with the correct type and tags for the category.
3. **Organize the content** using `###` headings to separate subtopics when a note receives multiple answers.
4. **Add tags** following the convention `[category, subtype, topic]`.
5. **Report progress** to the user as you go: `Created: SYSTEM/IDENTITY/identity-profile.md`

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
├── SYSTEM/IDENTITY/          [N] notes
├── SYSTEM/PREFERENCES/       [N] notes
├── SYSTEM/WORK/              [N] notes
├── SYSTEM/PROJECTS/          [N] notes
├── SYSTEM/PERSONAL-SPACE/    [N] notes
└── SYSTEM/KNOWLEDGE/         [N] notes

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
