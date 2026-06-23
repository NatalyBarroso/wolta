"""Bootstrap questions generator for vault initialization."""

from datetime import datetime
from pathlib import Path


class BootstrapGenerator:
    """Generates bootstrap questions and supporting files for the knowledge base."""

    def __init__(self, vault_path: str):
        """Initialize the bootstrap generator."""
        self.vault_path = Path(vault_path)

    def generate(self) -> None:
        """Generate all bootstrap files: questionnaire, mapping, index, and support files."""
        bootstrap_dir = self.vault_path / "AI-SYSTEM" / "BOOTSTRAP"
        bootstrap_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate INDEX-BOOTSTRAP.md (hub)
        self._create_bootstrap_index(bootstrap_dir)

        # 2. Generate BOOTSTRAP-QUESTIONNAIRE.md (main questionnaire with answer spaces)
        self._create_bootstrap_questionnaire(bootstrap_dir)

        # 3. Generate BOOTSTRAP-MAPPING.md (reference for P→note mapping)
        self._create_bootstrap_mapping(bootstrap_dir)

        # 4. Generate BOOTSTRAP-QUESTIONS.json (structured questions for agent)
        self._create_bootstrap_questions_json(bootstrap_dir)

        # 5. Generate BOOTSTRAP-INTERACTIVE-GUIDE.md (agent implementation guide)
        self._create_bootstrap_interactive_guide(bootstrap_dir)

        # 6. Generate update_bootstrap.py (utility script)
        self._create_bootstrap_updater_script(bootstrap_dir)

    def _create_bootstrap_index(self, bootstrap_dir: Path) -> None:
        """Create INDEX-BOOTSTRAP.md as the hub for bootstrap resources."""
        index_file = bootstrap_dir / "INDEX-BOOTSTRAP.md"
        content = f"""---
title: "INDEX-BOOTSTRAP - Initial KB Population"
type: "index"
index_module: "BOOTSTRAP"
created: {datetime.now().strftime("%Y-%m-%d")}
modified: {datetime.now().strftime("%Y-%m-%d")}
tags: [index, bootstrap, setup, ai-system]
status: "active"
context_for_claude: false
---

# BOOTSTRAP — Initial Population of the Knowledge Base

Control hub for populating the personal KB from scratch. Operational resources for the agent.

---

## Main Documents

### [[BOOTSTRAP-QUESTIONNAIRE]]
**31 reflective questions across 6 categories**
- IDENTITY (6 questions)
- PREFERENCES (6 questions)
- WORK (5 questions)
- PROJECTS (4 questions)
- PERSONAL-SPACE (5 questions)
- KNOWLEDGE (5 questions)

**Use:** Answer to generate the vault's initial notes
**Time:** 45-90 minutes
**Output:** ~20-30 new notes in the vault

### [[BOOTSTRAP-MAPPING]]
**Quick reference for the Question → Note mapping**
- Mapping table by category
- Standard frontmatter for new notes
- Step-by-step integration process
- Expected structure after completion

**Use:** Consult while creating notes from answers
**Reference:** Quick, does not require a full read

---

## Bootstrap Flow

```
1. Answer BOOTSTRAP-QUESTIONNAIRE.md
   ↓
2. Consult BOOTSTRAP-MAPPING.md
   ↓
3. Create notes following the mapping
   ↓
4. Run: graphify . --update --no-cluster
   ↓
5. Validate in Obsidian
   ↓
   KB populated and integrated
```

---

## Next Actions

- [ ] Answer BOOTSTRAP-QUESTIONNAIRE.md
- [ ] Create notes in IDENTITY/ from P.ID.1-6
- [ ] Create notes in PREFERENCES/ from P.PREF.1-6
- [ ] Create notes in WORK/ from P.WORK.1-5
- [ ] Create notes in PROJECTS/ from P.PROJ.1-4
- [ ] Create notes in PERSONAL-SPACE/ from P.PERS.1-5
- [ ] Create notes in KNOWLEDGE/ from P.KNOW.1-5
- [ ] Run `graphify . --update --no-cluster`
- [ ] Validate in Obsidian that all notes load
- [ ] Review graph.html to see the new connections

---

## Maintenance

**Frequency:** Every 2-3 months
- Review BOOTSTRAP-QUESTIONNAIRE.md
- Update answers that have changed
- Modify the corresponding notes
- Run graphify again

---

**Hub created:** {datetime.now().strftime("%Y-%m-%d")}
**Status:** Active and ready to use
**Owner:** Nataly
"""
        index_file.write_text(content, encoding="utf-8")

    def _create_bootstrap_questionnaire(self, bootstrap_dir: Path) -> None:
        """Create BOOTSTRAP-QUESTIONNAIRE.md with answer spaces and detailed instructions."""
        questionnaire_file = bootstrap_dir / "BOOTSTRAP-QUESTIONNAIRE.md"
        content = self._build_questionnaire_content()
        questionnaire_file.write_text(content, encoding="utf-8")

    def _build_questionnaire_content(self) -> str:
        """Build BOOTSTRAP-QUESTIONNAIRE.md with complete structure."""
        lines = []
        lines.append("---")
        lines.append('title: "BOOTSTRAP-QUESTIONNAIRE - Initial KB Populator"')
        lines.append('type: "index"')
        lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"modified: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("tags: [bootstrap, questionnaire, setup, context_for_claude]")
        lines.append('status: "active"')
        lines.append("context_for_claude: true")
        lines.append("---")
        lines.append("")
        lines.append("# BOOTSTRAP QUESTIONNAIRE — Populate your Knowledge Base")
        lines.append("")
        lines.append(
            "**Instruction:** This document will guide you through 31 reflective questions. Answer each one honestly. Each answer will generate a note in your vault, categorized automatically."
        )
        lines.append("")
        lines.append(
            "**Recommended duration:** 45-90 minutes (you can pause and come back)  "
        )
        lines.append(
            "**Answer length:** 2-5 paragraphs per question (no maximum limit)  "
        )
        lines.append(
            "**Next review:** Every 2-3 months to keep the KB up to date"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        # IDENTITY section
        lines.extend(self._build_section_identity())

        # PREFERENCES section
        lines.extend(self._build_section_preferences())

        # WORK section
        lines.extend(self._build_section_work())

        # PROJECTS section
        lines.extend(self._build_section_projects())

        # PERSONAL-SPACE section
        lines.extend(self._build_section_personal_space())

        # KNOWLEDGE section
        lines.extend(self._build_section_knowledge())

        # Instructions section
        lines.extend(self._build_instructions())

        return "\n".join(lines)

    def _build_section_identity(self) -> list:
        """Build IDENTITY section with answer spaces."""
        lines = []
        lines.append("## IDENTITY — Who You Are (6 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `IDENTITY/identity-profile.md`, `identity-values.md`, `identity-voice.md`, `identity-bio.md`"
        )
        lines.append("")

        # P.ID.1
        lines.append("### P.ID.1 — Personal Profile")
        lines.append(
            "**How would you describe yourself to someone who has never met you?**  "
        )
        lines.append(
            "We are not talking about your job or your resume, but simply about who you are as a person."
        )
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-profile.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — 2-5 paragraphs about who you essentially are]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.2
        lines.append("### P.ID.2 — Core Values")
        lines.append("**What are the things that matter most in your life?**  ")
        lines.append(
            "The principles or values that truly guide your day-to-day decisions?"
        )
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-values.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — List and explain your main values]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.3
        lines.append("### P.ID.3 — Defining Moments")
        lines.append("**Think about the moments that have shaped you most in your life.**  ")
        lines.append(
            "Is there an event, place, or person that has shaped who you are today?"
        )
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-bio.md` (history section)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Describe 2-3 key events or people]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.4
        lines.append("### P.ID.4 — Your Natural Voice")
        lines.append("**How do you prefer people to talk to you?**  ")
        lines.append(
            "What is your natural way of communicating, writing, and expressing what you think?"
        )
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-voice.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append(
            "[Write here — Describe your tone, communication style, preferences]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.5
        lines.append("### P.ID.5 — Deep Beliefs")
        lines.append("**What do you truly believe about work, life, and success?**  ")
        lines.append(
            "Is there something you deeply reject or something you believe without question?"
        )
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-values.md` (beliefs)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Explore your beliefs about fundamental topics]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.6
        lines.append("### P.ID.6 — Personal Motto")
        lines.append("**Is there a phrase, idea, or principle that defines you?**  ")
        lines.append("Something you would repeat to yourself in hard times.")
        lines.append("")
        lines.append("*Target note:* `IDENTITY/identity-profile.md` (epigraph)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your phrase, mantra, or personal principle]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_preferences(self) -> list:
        """Build PREFERENCES section with answer spaces."""
        lines = []
        lines.append("## PREFERENCES — How You Like to Work and Live (6 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `PREFERENCES/preferences-work-style.md`, `preferences-tools.md`, `preferences-lifestyle.md`"
        )
        lines.append("")

        # P.PREF.1
        lines.append("### P.PREF.1 — Your Ideal Day")
        lines.append("**What would your ideal day look like?**  ")
        lines.append(
            "What time do you wake up, how do you structure your time, when do you have energy for the important things?"
        )
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append(
            "[Write here — Describe your ideal day from waking up to going to sleep]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.2
        lines.append("### P.PREF.2 — Focus Environment")
        lines.append("**What is the perfect environment for you to concentrate?**  ")
        lines.append("Noise, silence, coffee, home, office, nature?")
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-work-style.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Detail your ideal working conditions]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.3
        lines.append("### P.PREF.3 — Essential Tools")
        lines.append(
            "**What tools or apps do you consider essential in your day-to-day?**  "
        )
        lines.append("Why did you choose them over others?")
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-tools.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — List your favorite tools and why]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.4
        lines.append("### P.PREF.4 — Communication Mode")
        lines.append(
            "**If you had to choose: do you prefer to communicate by writing, talking, or a mix?**  "
        )
        lines.append("Synchronously or asynchronously?")
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-work-style.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Explore your communication preferences]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.5
        lines.append("### P.PREF.5 — Non-Negotiable Habits")
        lines.append("**Are there habits you would not change for anything?**  ")
        lines.append(
            "(exercise, meditation, reading before sleep, a morning routine, etc.)"
        )
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your fundamental routines and habits]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.6
        lines.append("### P.PREF.6 — Relationship with Money")
        lines.append("**What is your relationship with money and owning things?**  ")
        lines.append("Do you care about having a lot, few things, or something in between?")
        lines.append("")
        lines.append("*Target note:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your philosophy about money and possessions]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_work(self) -> list:
        """Build WORK section with answer spaces."""
        lines = []
        lines.append("## WORK — Your Professional Life (5 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `WORK/work-current-role.md`, `work-company.md`, `work-overview.md`, `work-team.md`"
        )
        lines.append("")

        lines.append("### P.WORK.1 — Current Work Context")
        lines.append("**Tell me about your current job.**  ")
        lines.append(
            "Where do you work, what do you do, and in which areas do you feel you contribute most?"
        )
        lines.append("")
        lines.append("*Target note:* `WORK/work-overview.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append(
            "[Write here — Description of your role, company, responsibilities]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.2 — Your Ideal Work Day")
        lines.append("**What would your ideal work day look like, and what would a bad one look like?**  ")
        lines.append("What conditions or circumstances make you give your best?")
        lines.append("")
        lines.append("*Target note:* `WORK/work-current-role.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — What energizes you and what drains you at work]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.3 — Technical Specialty")
        lines.append("**What is your technical background or area of specialty?**  ")
        lines.append("In which topics do you feel truly comfortable and confident?")
        lines.append("")
        lines.append("*Target note:* `WORK/work-current-role.md` (expertise)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your background, skills, areas of mastery]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.4 — Key Professional People")
        lines.append("**Who are the key people in your professional life?**  ")
        lines.append("What are your relationships with colleagues, boss, and team like?")
        lines.append("")
        lines.append("*Target note:* `WORK/work-team.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Describe your key professional relationships]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.5 — Professional Trajectory")
        lines.append(
            "**Thinking about your career so far, what roles have you had and what did you learn from each experience?**"
        )
        lines.append("")
        lines.append("*Target note:* `WORK/work-overview.md` (history section)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your professional history and what you learned]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_projects(self) -> list:
        """Build PROJECTS section with answer spaces."""
        lines = []
        lines.append("## PROJECTS — What You Are Doing (4 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `PROJECTS/[project-name].md` (new notes per project)"
        )
        lines.append("")

        lines.append("### P.PROJ.1 — Active Projects")
        lines.append(
            "**What projects are you working on right now, whether professional or personal?**  "
        )
        lines.append("What state are they in?")
        lines.append("")
        lines.append(
            "*Target note:* `PROJECTS/[project-name].md` (create one per project)"
        )
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — List your active projects with their current status]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.2 — Future Projects")
        lines.append(
            "**Is there a personal or creative project you would be excited to pursue in the coming months?**"
        )
        lines.append("")
        lines.append("*Target note:* `PROJECTS/[project-name].md` (ideation)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Projects that appeal to you but you have not started]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.3 — Proud Projects")
        lines.append(
            "**Looking back, is there a project you are especially proud of?**  "
        )
        lines.append("What made it special?")
        lines.append("")
        lines.append(
            "*Target note:* `PROJECTS/[project-name].md` (archived with reflection)"
        )
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append(
            "[Write here — Completed projects you feel good about]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.4 — Long-Term Vision")
        lines.append(
            "**What would you like to be doing in 2 or 3 years, both professionally and personally?**  "
        )
        lines.append("Where do you want to go?")
        lines.append("")
        lines.append("*Target note:* `PROJECTS/INDEX-PROJECTS.md` (vision section)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your medium-term direction]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_personal_space(self) -> list:
        """Build PERSONAL-SPACE section with answer spaces."""
        lines = []
        lines.append("## PERSONAL-SPACE — Your Leisure and Entertainment (5 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `PERSONAL-SPACE/personal-hobbies.md`, `personal-interests.md`"
        )
        lines.append("")

        lines.append("### P.PERS.1 — Movies and Series")
        lines.append(
            "**What are your favorite movies, series, or documentaries?**  "
        )
        lines.append("What is it about them that marked you or still draws you in?")
        lines.append("")
        lines.append(
            "*Target note:* `PERSONAL-SPACE/personal-interests.md` (watchlist)"
        )
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your favorite movies/series and why]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.2 — Books that Matter")
        lines.append("**What books have you read that really left you with something?**  ")
        lines.append("Is there one you reread or recommend?")
        lines.append("")
        lines.append(
            "*Target note:* `PERSONAL-SPACE/personal-interests.md` (readlist)"
        )
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your favorite and impactful books]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.3 — Free Time")
        lines.append("**How do you spend your free time when you are not working?**  ")
        lines.append("What activities make you feel most alive?")
        lines.append("")
        lines.append("*Target note:* `PERSONAL-SPACE/personal-hobbies.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your hobbies and leisure activities]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.4 — Inspiration and Quotes")
        lines.append("**Are there phrases, quotes, or ideas that especially inspire you?**  ")
        lines.append("Something you repeat in your head when you need it?")
        lines.append("")
        lines.append("*Target note:* `PERSONAL-SPACE/personal-interests.md` (quotes)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your inspiring phrases and quotes]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.5 — Music and Podcasts")
        lines.append("**What kind of music or podcasts do you usually listen to?**  ")
        lines.append("Are there topics that spark your curiosity, laughter, or calm?")
        lines.append("")
        lines.append("*Target note:* `PERSONAL-SPACE/personal-interests.md` (audio)")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your musical taste and podcast topics]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_knowledge(self) -> list:
        """Build KNOWLEDGE section with answer spaces."""
        lines = []
        lines.append("## KNOWLEDGE — What You Learn (5 questions)")
        lines.append("")
        lines.append(
            "*These answers will populate:* `KNOWLEDGE/[specialty].md` (notes by area of specialization)"
        )
        lines.append("")

        lines.append("### P.KNOW.1 — Current Learning")
        lines.append("**Is there something you are learning right now?**  ")
        lines.append("A course, a language, a skill you are pursuing.")
        lines.append("")
        lines.append("*Target note:* `KNOWLEDGE/knowledge-current-learning.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your learning in progress]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.2 — Future Specialization")
        lines.append(
            "**Is there a specific area in your field that draws you to specialize or go deeper?**  "
        )
        lines.append("Even if right now it is only a vague interest.")
        lines.append("")
        lines.append("*Target note:* `KNOWLEDGE/knowledge-interests.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Areas you want to explore or master]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.3 — Current Expertise")
        lines.append("**On which topics do you feel you really know what you are talking about?**  ")
        lines.append("And which ones would you like to improve?")
        lines.append("")
        lines.append("*Target note:* `KNOWLEDGE/knowledge-expertise.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your current expertise and areas for improvement]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.4 — Learning Sources")
        lines.append("**Where do you typically learn from?**  ")
        lines.append(
            "Blogs, books, YouTube, online communities, talking with others?"
        )
        lines.append("")
        lines.append("*Target note:* `KNOWLEDGE/knowledge-sources.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Your favorite learning channels and sources]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.5 — Fundamental Concepts")
        lines.append(
            "**Is there a concept, insight, or idea you have learned that you consider fundamental and want to retain?**"
        )
        lines.append("")
        lines.append("*Target note:* `KNOWLEDGE/knowledge-insights.md`")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("```")
        lines.append("[Write here — Key ideas you want to preserve]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_instructions(self) -> list:
        """Build instructions section."""
        lines = []
        lines.append("## INTEGRATION INSTRUCTIONS")
        lines.append("")
        lines.append("### Step 1: Complete the Questionnaire")
        lines.append("- Answer the 31 questions in this document")
        lines.append("- Take your time (it is not a race)")
        lines.append("- Be specific and detailed")
        lines.append("")
        lines.append("### Step 2: Mapping to Notes")
        lines.append("Once complete, each answer becomes a note:")
        lines.append("")
        lines.append(
            "Consult **BOOTSTRAP-MAPPING.md** to see exactly where each answer goes."
        )
        lines.append("")
        lines.append("### Step 3: Create the Notes")
        lines.append("In Obsidian:")
        lines.append("1. Go to the correct folder (e.g. IDENTITY/)")
        lines.append("2. Create a new file")
        lines.append("3. Name it according to the convention")
        lines.append("4. Copy the standard frontmatter")
        lines.append("5. Add the content of the answer")
        lines.append("")
        lines.append("### Step 4: Update Graphify")
        lines.append("```bash")
        lines.append("graphify . --update --no-cluster")
        lines.append("```")
        lines.append("")
        lines.append("### Step 5: Validate")
        lines.append("- Open the vault in Obsidian")
        lines.append("- Verify that all notes load")
        lines.append("- Review the Graph View to see the connections")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Final instructions:**")
        lines.append(
            "1. **Answer honestly**: There are no correct answers. This is for you."
        )
        lines.append(
            "2. **Take your time**: Do not rush. Genuinely reflect on each question."
        )
        lines.append(
            "3. **Be specific**: Concrete details and examples will make your KB much more useful."
        )
        lines.append(
            "4. **Update regularly**: Come back to these questions every 2-3 months. Your KB should grow with you."
        )
        lines.append(
            "5. **Length is not a problem**: Write as much as you need. More context = a better KB."
        )
        lines.append("")
        lines.append("---")
        lines.append("")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        lines.append(f"**Total completed:** 31 questions across 6 categories")
        lines.append(f"**Generated:** {timestamp}")
        lines.append(f"**Version:** 1.0")
        lines.append("")

        return lines

    def _create_bootstrap_questions_json(self, bootstrap_dir: Path) -> None:
        """Create BOOTSTRAP-QUESTIONS.json for agent access."""
        import json

        questions_file = bootstrap_dir / "BOOTSTRAP-QUESTIONS.json"
        questions_data = {
            "metadata": {
                "total_questions": 31,
                "categories": 6,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0",
                "description": "Bootstrap questionnaire for Wolta KB initialization"
            },
            "instructions": {
                "how_to_respond": "Answer honestly. There are no correct answers.",
                "recommended_length": "2-5 paragraphs per question (no maximum limit)",
                "estimated_duration": "45-90 minutes total",
                "agent_mode": "If you say 'Start the bootstrap', the agent will ask the questions one by one"
            }
        }

        questions_file.write_text(json.dumps(questions_data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _create_bootstrap_interactive_guide(self, bootstrap_dir: Path) -> None:
        """Create BOOTSTRAP-INTERACTIVE-GUIDE.md for agent implementation."""
        guide_file = bootstrap_dir / "BOOTSTRAP-INTERACTIVE-GUIDE.md"
        content = """---
title: "BOOTSTRAP Interactive Guide for Agents"
type: "guide"
audience: "claude-agents"
created: {date}
tags: [bootstrap, agent, interactive, guide]
context_for_claude: true
---

# BOOTSTRAP Interactive Mode - Agent Implementation Guide

## Trigger Detection

When the user says any of these, activate bootstrap interactive mode:
- "start the bootstrap"
- "start bootstrap"
- "begin bootstrap"
- "answer bootstrap questions"

## What to Do

1. Load questions from BOOTSTRAP-QUESTIONS.json
2. Ask 31 questions one by one with format: [CATEGORY - X/31]
3. Record each response
4. Update BOOTSTRAP-QUESTIONNAIRE.md with responses
5. Show progress: "We are at X/31"

## Question Format

```
[IDENTITY - 1/31]

**P.ID.1 — Personal Profile**

[Question text]

[Context if available]

Go ahead, I'm listening.
```

## Response Recording

1. User answers
2. You confirm: "Got it. Recorded."
3. Ask next question
4. Continue until 31 or user says "pause"

## Session End

After all 31 questions:
```
Excellent. I have completed the 31 questions.
Now I will update the BOOTSTRAP-QUESTIONNAIRE.md file
```

Then update the file with all responses.

## Rules

- No emoticons/emojis
- Accept any response length
- Do NOT critique responses
- Record exactly what the user says
- Match the user's language
- Always show X/31 progress

---

For full technical specification, see this file metadata.
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        guide_file.write_text(content, encoding="utf-8")

    def _create_bootstrap_updater_script(self, bootstrap_dir: Path) -> None:
        """Create update_bootstrap.py utility script."""
        script_file = bootstrap_dir / "update_bootstrap.py"
        content = '''#!/usr/bin/env python3
"""Bootstrap Questionnaire File Updater - Auto-generated"""

import re
from pathlib import Path
from typing import Dict, Optional

class BootstrapUpdater:
    """Updates BOOTSTRAP-QUESTIONNAIRE.md with responses."""

    def __init__(self, markdown_file: Path):
        self.markdown_file = Path(markdown_file)
        self.markdown_content = self._load_markdown()

    def _load_markdown(self) -> str:
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            return f.read()

    def update_response(self, question_id: str, response_text: str) -> bool:
        """Update response for a specific question."""
        pattern = rf"### {re.escape(question_id)}\\s*—.*?(?=^###|^##|$)"
        match = re.search(pattern, self.markdown_content, re.MULTILINE | re.DOTALL)

        if not match:
            return False

        section = self.markdown_content[match.start():match.end()]
        response_pattern = r"\\*\\*Your answer:\\*\\*\\n```\\n(.*?)\\n```"
        response_match = re.search(response_pattern, section, re.DOTALL)

        if not response_match:
            return False

        block_start = match.start() + response_match.start(1)
        block_end = match.start() + response_match.end(1)

        self.markdown_content = (
            self.markdown_content[:block_start] +
            response_text +
            self.markdown_content[block_end:]
        )
        return True

    def save(self) -> bool:
        try:
            with open(self.markdown_file, 'w', encoding='utf-8') as f:
                f.write(self.markdown_content)
            return True
        except Exception:
            return False

def update_bootstrap(file_path: str, responses: Dict[str, str]) -> bool:
    """Update bootstrap file with responses."""
    updater = BootstrapUpdater(Path(file_path))
    for q_id, response in responses.items():
        updater.update_response(q_id, response)
    return updater.save()
'''
        script_file.write_text(content, encoding="utf-8")

    def _create_bootstrap_mapping(self, bootstrap_dir: Path) -> None:
        """Create BOOTSTRAP-MAPPING.md reference file."""
        mapping_file = bootstrap_dir / "BOOTSTRAP-MAPPING.md"
        content = self._build_mapping_content()
        mapping_file.write_text(content, encoding="utf-8")

    def _build_mapping_content(self) -> str:
        """Build BOOTSTRAP-MAPPING.md content."""
        lines = []
        lines.append("---")
        lines.append('title: "BOOTSTRAP-MAPPING - Question→Note Mapping Reference"')
        lines.append('type: "index"')
        lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"modified: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("tags: [bootstrap, mapping, reference]")
        lines.append('status: "active"')
        lines.append("context_for_claude: false")
        lines.append("---")
        lines.append("")
        lines.append("# BOOTSTRAP MAPPING — Question → KB Note")
        lines.append("")
        lines.append(
            "**Quick reference for turning questionnaire answers into vault notes.**"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## IDENTITY — Who You Are (6 questions → 4 notes)")
        lines.append("")
        lines.append("| # | Question | Target Note | Section |")
        lines.append("|---|----------|-------------|---------|")
        lines.append(
            "| P.ID.1 | How would you describe yourself? | `IDENTITY/identity-profile.md` | Main profile |"
        )
        lines.append(
            "| P.ID.2 | What are your values? | `IDENTITY/identity-values.md` | Core values |"
        )
        lines.append(
            '| P.ID.3 | Moments that shaped you | `IDENTITY/identity-bio.md` | Section: "My History" |'
        )
        lines.append(
            "| P.ID.4 | How do you prefer to be addressed? | `IDENTITY/identity-voice.md` | Your voice and communication |"
        )
        lines.append(
            "| P.ID.5 | What do you believe about work/success? | `IDENTITY/identity-values.md` | Deep beliefs |"
        )
        lines.append(
            "| P.ID.6 | Your personal phrase/principle? | `IDENTITY/identity-profile.md` | Epigraph or motto |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## PREFERENCES — How You Like to Work (6 questions → 3 notes)")
        lines.append("")
        lines.append("| # | Question | Target Note | Section |")
        lines.append("|---|----------|-------------|---------|")
        lines.append(
            "| P.PREF.1 | What would your ideal day be? | `PREFERENCES/preferences-lifestyle.md` | Daily routine |"
        )
        lines.append(
            "| P.PREF.2 | Perfect environment | `PREFERENCES/preferences-work-style.md` | Work environment |"
        )
        lines.append(
            "| P.PREF.3 | Essential tools | `PREFERENCES/preferences-tools.md` | Tool stack |"
        )
        lines.append(
            "| P.PREF.4 | Communication mode | `PREFERENCES/preferences-work-style.md` | Communication preferences |"
        )
        lines.append(
            "| P.PREF.5 | Non-negotiable habits | `PREFERENCES/preferences-lifestyle.md` | Routines and habits |"
        )
        lines.append(
            "| P.PREF.6 | Relationship with money | `PREFERENCES/preferences-lifestyle.md` | Personal philosophy |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## WORK — Your Professional Life (5 questions → 4 notes)")
        lines.append("")
        lines.append("| # | Question | Target Note | Section |")
        lines.append("|---|----------|-------------|---------|")
        lines.append(
            "| P.WORK.1 | Your current job | `WORK/work-overview.md` | General context |"
        )
        lines.append(
            "| P.WORK.2 | Ideal vs bad day | `WORK/work-current-role.md` | Energy dynamics |"
        )
        lines.append(
            "| P.WORK.3 | Your background/specialty | `WORK/work-current-role.md` | Expertise |"
        )
        lines.append(
            "| P.WORK.4 | Key people | `WORK/work-team.md` | Professional relationships |"
        )
        lines.append(
            "| P.WORK.5 | Professional trajectory | `WORK/work-overview.md` | Professional history |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## PROJECTS — What You Are Doing (4 questions → Dynamic)")
        lines.append("")
        lines.append("| # | Question | Target Note | Type |")
        lines.append("|---|----------|-------------|------|")
        lines.append(
            "| P.PROJ.1 | Active projects | `PROJECTS/[project-name].md` | One per project |"
        )
        lines.append(
            "| P.PROJ.2 | Future projects | `PROJECTS/[project-name].md` | One per ideated project |"
        )
        lines.append(
            "| P.PROJ.3 | Proud projects | `PROJECTS/[project-name].md` | One per archived project |"
        )
        lines.append(
            '| P.PROJ.4 | Long-term vision | `PROJECTS/INDEX-PROJECTS.md` | Section: "2-3 year vision" |'
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(
            "## PERSONAL-SPACE — Leisure and Entertainment (5 questions → 2 notes)"
        )
        lines.append("")
        lines.append("| # | Question | Target Note | Subsection |")
        lines.append("|---|----------|-------------|-----------|")
        lines.append(
            "| P.PERS.1 | Favorite movies/series | `PERSONAL-SPACE/personal-interests.md` | Watchlist |"
        )
        lines.append(
            "| P.PERS.2 | Impactful books | `PERSONAL-SPACE/personal-interests.md` | Readlist |"
        )
        lines.append(
            "| P.PERS.3 | Free time and hobbies | `PERSONAL-SPACE/personal-hobbies.md` | Main activities |"
        )
        lines.append(
            "| P.PERS.4 | Inspiring phrases/quotes | `PERSONAL-SPACE/personal-interests.md` | Quotes |"
        )
        lines.append(
            "| P.PERS.5 | Music and podcasts | `PERSONAL-SPACE/personal-interests.md` | Audio |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## KNOWLEDGE — What You Learn (5 questions → 5 notes)")
        lines.append("")
        lines.append("| # | Question | Target Note | Content |")
        lines.append("|---|----------|-------------|----------|")
        lines.append(
            "| P.KNOW.1 | Current learning | `KNOWLEDGE/knowledge-current-learning.md` | Courses, languages, skills in progress |"
        )
        lines.append(
            "| P.KNOW.2 | Future specialization | `KNOWLEDGE/knowledge-interests.md` | Areas to explore |"
        )
        lines.append(
            "| P.KNOW.3 | Your current expertise | `KNOWLEDGE/knowledge-expertise.md` | What you know well + areas for improvement |"
        )
        lines.append(
            "| P.KNOW.4 | Learning sources | `KNOWLEDGE/knowledge-sources.md` | Channels: blogs, books, YouTube, etc. |"
        )
        lines.append(
            "| P.KNOW.5 | Fundamental concepts | `KNOWLEDGE/knowledge-insights.md` | Key ideas to retain |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## STANDARD FRONTMATTER FOR ALL NOTES")
        lines.append("")
        lines.append("```yaml")
        lines.append("---")
        lines.append('title: "[Specific title]"')
        lines.append(
            'type: "identity | preference | work | project | personal | knowledge"'
        )
        lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"modified: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("tags: [category, subcategory, relevant-topic]")
        lines.append('status: "active"')
        lines.append("context_for_claude: true")
        lines.append("---")
        lines.append("```")
        lines.append("")
        lines.append(
            "**Note:** `context_for_claude: true` so the agent loads these notes automatically in future sessions."
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(
            "**This document is your quick reference during integration.**"
        )
        lines.append("")

        return "\n".join(lines)
