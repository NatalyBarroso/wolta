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
title: "INDEX-BOOTSTRAP - Población Inicial de la KB"
type: "index"
index_module: "BOOTSTRAP"
created: {datetime.now().strftime("%Y-%m-%d")}
modified: {datetime.now().strftime("%Y-%m-%d")}
tags: [index, bootstrap, setup, ai-system]
status: "active"
context_for_claude: false
---

# BOOTSTRAP — Población Inicial de la Knowledge Base

Hub de control para poblar la KB personal desde cero. Recursos operativos del agente.

---

## Documentos Principales

### [[BOOTSTRAP-QUESTIONNAIRE]]
**31 preguntas reflexivas en 6 categorías**
- IDENTITY (6 preguntas)
- PREFERENCES (6 preguntas)
- WORK (5 preguntas)
- PROJECTS (4 preguntas)
- PERSONAL-SPACE (5 preguntas)
- KNOWLEDGE (5 preguntas)

**Uso:** Responde para generar notas iniciales del vault
**Tiempo:** 45-90 minutos
**Salida:** ~20-30 notas nuevas en el vault

### [[BOOTSTRAP-MAPPING]]
**Referencia rápida de mapeo Pregunta → Nota**
- Tabla de mapeos por categoría
- Frontmatter estándar para nuevas notas
- Proceso paso-a-paso para integración
- Estructura esperada después de completar

**Uso:** Consulta mientras creas notas desde respuestas
**Referencia:** Rápida, no requiere lectura completa

---

## Flujo de Bootstrap

```
1. Responde BOOTSTRAP-QUESTIONNAIRE.md
   ↓
2. Consulta BOOTSTRAP-MAPPING.md
   ↓
3. Crea notas siguiendo el mapping
   ↓
4. Ejecuta: graphify . --update --no-cluster
   ↓
5. Valida en Obsidian
   ↓
   KB poblada e integrada
```

---

## Próximas Acciones

- [ ] Responder BOOTSTRAP-QUESTIONNAIRE.md
- [ ] Crear notas en IDENTITY/ desde P.ID.1-6
- [ ] Crear notas en PREFERENCES/ desde P.PREF.1-6
- [ ] Crear notas en WORK/ desde P.WORK.1-5
- [ ] Crear notas en PROJECTS/ desde P.PROJ.1-4
- [ ] Crear notas en PERSONAL-SPACE/ desde P.PERS.1-5
- [ ] Crear notas en KNOWLEDGE/ desde P.KNOW.1-5
- [ ] Ejecutar `graphify . --update --no-cluster`
- [ ] Validar en Obsidian que todas las notas cargan
- [ ] Revisar graph.html para ver nuevas conexiones

---

## Mantenimiento

**Periodicidad:** Cada 2-3 meses
- Revisa BOOTSTRAP-QUESTIONNAIRE.md
- Actualiza respuestas que hayan cambiado
- Modifica notas correspondientes
- Ejecuta graphify nuevamente

---

**Hub creado:** {datetime.now().strftime("%Y-%m-%d")}
**Status:** Activo y listo para usar
**Responsable:** Nataly
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
        lines.append('title: "BOOTSTRAP-QUESTIONNAIRE - Poblador Inicial de KB"')
        lines.append('type: "index"')
        lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"modified: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("tags: [bootstrap, questionnaire, setup, context_for_claude]")
        lines.append('status: "active"')
        lines.append("context_for_claude: true")
        lines.append("---")
        lines.append("")
        lines.append("# BOOTSTRAP QUESTIONNAIRE — Pobla tu Knowledge Base")
        lines.append("")
        lines.append(
            "**Instrucción:** Este documento te guiará a través de 31 preguntas reflexivas. Responde cada una con sinceridad. Cada respuesta generará una nota en tu vault, categorizada automáticamente."
        )
        lines.append("")
        lines.append(
            "**Duración recomendada:** 45-90 minutos (puedes pausar y volver)  "
        )
        lines.append(
            "**Longitud de respuestas:** 2-5 párrafos por pregunta (sin límite máximo)  "
        )
        lines.append(
            "**Próxima revisión:** Cada 2-3 meses para mantener la KB actualizada"
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
        lines.append("## IDENTITY — Quién Eres (6 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `IDENTITY/identity-profile.md`, `identity-values.md`, `identity-voice.md`, `identity-bio.md`"
        )
        lines.append("")

        # P.ID.1
        lines.append("### P.ID.1 — Perfil Personal")
        lines.append(
            "**¿Cómo te describirías ante alguien que nunca te ha conocido?**  "
        )
        lines.append(
            "No hablamos de tu puesto de trabajo ni tu currículum, sino simplemente de quién eres como persona."
        )
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-profile.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — 2-5 párrafos sobre quién eres esencialmente]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.2
        lines.append("### P.ID.2 — Valores Fundamentales")
        lines.append("**¿Cuáles son las cosas que más importan en tu vida?**  ")
        lines.append(
            "¿Los principios o valores que guían realmente tus decisiones día a día?"
        )
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-values.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Enumera y explica tus valores principales]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.3
        lines.append("### P.ID.3 — Momentos Marcadores")
        lines.append("**Piensa en los momentos que más te han marcado en tu vida.**  ")
        lines.append(
            "¿Hay algún evento, lugar o persona que haya moldeado quién eres hoy?"
        )
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-bio.md` (sección histórica)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Describe 2-3 eventos o personas clave]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.4
        lines.append("### P.ID.4 — Tu Voz Natural")
        lines.append("**¿Cómo prefieres que la gente te hable?**  ")
        lines.append(
            "¿Cuál es tu forma natural de comunicarte, de escribir, de expresar lo que piensas?"
        )
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-voice.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append(
            "[Escribe aquí — Describe tu tono, estilo comunicativo, preferencias]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.5
        lines.append("### P.ID.5 — Creencias Profundas")
        lines.append("**¿Qué crees realmente sobre el trabajo, la vida, el éxito?**  ")
        lines.append(
            "¿Hay algo que rechaces profundamente o algo en lo que creas sin dudarlo?"
        )
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-values.md` (creencias)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Explora tus creencias sobre temas fundamentales]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.ID.6
        lines.append("### P.ID.6 — Lema Personal")
        lines.append("**¿Hay una frase, idea o principio que te defina?**  ")
        lines.append("Algo que repetirías a ti mismo en momentos difíciles.")
        lines.append("")
        lines.append("*Nota destino:* `IDENTITY/identity-profile.md` (epígrafe)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu frase, mantra o principio personal]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_preferences(self) -> list:
        """Build PREFERENCES section with answer spaces."""
        lines = []
        lines.append("## PREFERENCES — Cómo Te Gusta Trabajar y Vivir (6 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `PREFERENCES/preferences-work-style.md`, `preferences-tools.md`, `preferences-lifestyle.md`"
        )
        lines.append("")

        # P.PREF.1
        lines.append("### P.PREF.1 — Tu Día Ideal")
        lines.append("**¿Cómo sería tu día ideal?**  ")
        lines.append(
            "¿A qué hora te despiertas, cómo estructuras tu tiempo, cuándo tienes energía para las cosas importantes?"
        )
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append(
            "[Escribe aquí — Describe tu día ideal desde despertarse hasta dormir]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.2
        lines.append("### P.PREF.2 — Entorno de Concentración")
        lines.append("**¿Cuál es el entorno perfecto para que te concentres?**  ")
        lines.append("¿Ruido, silencio, café, casa, oficina, naturaleza?")
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-work-style.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Detalla tus condiciones ideales de trabajo]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.3
        lines.append("### P.PREF.3 — Herramientas Imprescindibles")
        lines.append(
            "**¿Qué herramientas o apps consideras que son imprescindibles en tu día a día?**  "
        )
        lines.append("¿Por qué las elegiste sobre otras?")
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-tools.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Lista tus herramientas favoritas y por qué]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.4
        lines.append("### P.PREF.4 — Modo de Comunicación")
        lines.append(
            "**Si tuvieras que elegir: ¿prefieres comunicarte escribiendo, hablando, o una mezcla?**  "
        )
        lines.append("¿Síncronamente o asincronamente?")
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-work-style.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Explora tus preferencias comunicativas]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.5
        lines.append("### P.PREF.5 — Hábitos No Negociables")
        lines.append("**¿Hay hábitos que no cambiarías por nada?**  ")
        lines.append(
            "(ejercicio, meditación, leer antes de dormir, una rutina matutina, etc.)"
        )
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus rutinas y hábitos fundamentales]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # P.PREF.6
        lines.append("### P.PREF.6 — Relación con el Dinero")
        lines.append("**¿Cuál es tu relación con el dinero y la posesión de cosas?**  ")
        lines.append("¿Te importa tener mucho, pocas cosas, o algo intermedio?")
        lines.append("")
        lines.append("*Nota destino:* `PREFERENCES/preferences-lifestyle.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu filosofía sobre dinero y posesiones]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_work(self) -> list:
        """Build WORK section with answer spaces."""
        lines = []
        lines.append("## WORK — Tu Vida Profesional (5 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `WORK/work-current-role.md`, `work-company.md`, `work-overview.md`, `work-team.md`"
        )
        lines.append("")

        lines.append("### P.WORK.1 — Contexto Laboral Actual")
        lines.append("**Cuéntame sobre tu trabajo actual.**  ")
        lines.append(
            "¿Dónde trabajas, qué haces, y en qué áreas sientes que contribuyes más?"
        )
        lines.append("")
        lines.append("*Nota destino:* `WORK/work-overview.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append(
            "[Escribe aquí — Descripción de tu puesto, empresa, responsabilidades]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.2 — Tu Día de Trabajo Ideal")
        lines.append("**¿Cómo sería tu día de trabajo ideal y cómo sería uno malo?**  ")
        lines.append("¿Qué condiciones o circunstancias hacen que des lo mejor de ti?")
        lines.append("")
        lines.append("*Nota destino:* `WORK/work-current-role.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Qué te energiza y qué te drena en el trabajo]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.3 — Especialidad Técnica")
        lines.append("**¿Cuál es tu formación técnica o área de especialidad?**  ")
        lines.append("¿En qué temas te sientes realmente cómodo y confiado?")
        lines.append("")
        lines.append("*Nota destino:* `WORK/work-current-role.md` (expertise)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu background, habilidades, áreas de dominio]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.4 — Personas Clave Profesionales")
        lines.append("**¿Quiénes son las personas clave en tu vida profesional?**  ")
        lines.append("¿Cómo son tus relaciones con colegas, jefe, equipo?")
        lines.append("")
        lines.append("*Nota destino:* `WORK/work-team.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Describe tus relaciones profesionales clave]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.WORK.5 — Trayectoria Profesional")
        lines.append(
            "**Pensando en tu carrera hasta ahora, ¿qué roles has tenido y qué aprendiste de cada experiencia?**"
        )
        lines.append("")
        lines.append("*Nota destino:* `WORK/work-overview.md` (sección histórica)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu historia profesional y lo aprendido]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_projects(self) -> list:
        """Build PROJECTS section with answer spaces."""
        lines = []
        lines.append("## PROJECTS — Qué Estás Haciendo (4 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `PROJECTS/[project-name].md` (notas nuevas por proyecto)"
        )
        lines.append("")

        lines.append("### P.PROJ.1 — Proyectos Activos")
        lines.append(
            "**¿En qué proyectos estás trabajando ahora mismo, ya sean profesionales o personales?**  "
        )
        lines.append("¿En qué estado se encuentran?")
        lines.append("")
        lines.append(
            "*Nota destino:* `PROJECTS/[project-name].md` (crear una por proyecto)"
        )
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Lista tus proyectos activos con estado actual]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.2 — Proyectos Futuros")
        lines.append(
            "**¿Hay algún proyecto personal o creativo que te emocionaría sacar adelante en los próximos meses?**"
        )
        lines.append("")
        lines.append("*Nota destino:* `PROJECTS/[project-name].md` (ideation)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Proyectos que te atraen pero no has iniciado]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.3 — Proyectos de Orgullo")
        lines.append(
            "**Mirando hacia atrás, ¿hay algún proyecto del que estés especialmente orgulloso?**  "
        )
        lines.append("¿Qué lo hizo especial?")
        lines.append("")
        lines.append(
            "*Nota destino:* `PROJECTS/[project-name].md` (archived with reflection)"
        )
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append(
            "[Escribe aquí — Proyectos completados de los que te sientes bien]"
        )
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PROJ.4 — Visión a Largo Plazo")
        lines.append(
            "**¿Qué te gustaría estar haciendo en 2 o 3 años, tanto a nivel profesional como personal?**  "
        )
        lines.append("¿Hacia dónde quieres ir?")
        lines.append("")
        lines.append("*Nota destino:* `PROJECTS/INDEX-PROJECTS.md` (vision section)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu dirección a mediano plazo]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_personal_space(self) -> list:
        """Build PERSONAL-SPACE section with answer spaces."""
        lines = []
        lines.append("## PERSONAL-SPACE — Tu Ocio y Entretenimiento (5 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `PERSONAL-SPACE/personal-hobbies.md`, `personal-interests.md`"
        )
        lines.append("")

        lines.append("### P.PERS.1 — Películas y Series")
        lines.append(
            "**¿Cuáles son tus películas, series o documentales favoritos?**  "
        )
        lines.append("¿Qué tienen que te marcó o te sigue atrayendo?")
        lines.append("")
        lines.append(
            "*Nota destino:* `PERSONAL-SPACE/personal-interests.md` (watchlist)"
        )
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus películas/series favoritas y por qué]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.2 — Libros que Importan")
        lines.append("**¿Qué libros has leído que realmente te hayan dejado algo?**  ")
        lines.append("¿Hay alguno que releas o que recomiendes?")
        lines.append("")
        lines.append(
            "*Nota destino:* `PERSONAL-SPACE/personal-interests.md` (readlist)"
        )
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus libros favoritos e impactantes]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.3 — Tiempo Libre")
        lines.append("**¿Cómo pasas tu tiempo libre cuando no estás trabajando?**  ")
        lines.append("¿Qué actividades te hacen sentir más vivo?")
        lines.append("")
        lines.append("*Nota destino:* `PERSONAL-SPACE/personal-hobbies.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus pasatiempos, actividades de ocio]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.4 — Inspiración y Citas")
        lines.append("**¿Hay frases, citas o ideas que te inspiren especialmente?**  ")
        lines.append("¿Algo que repitas en tu cabeza cuando lo necesitas?")
        lines.append("")
        lines.append("*Nota destino:* `PERSONAL-SPACE/personal-interests.md` (quotes)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus frases y citas inspiradoras]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.PERS.5 — Música y Podcasts")
        lines.append("**¿Qué tipo de música o podcasts sueles escuchar?**  ")
        lines.append("¿Hay temas que te causen curiosidad, risa o calma?")
        lines.append("")
        lines.append("*Nota destino:* `PERSONAL-SPACE/personal-interests.md` (audio)")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu gusto musical y temas de podcast]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_section_knowledge(self) -> list:
        """Build KNOWLEDGE section with answer spaces."""
        lines = []
        lines.append("## KNOWLEDGE — Lo Que Aprendes (5 preguntas)")
        lines.append("")
        lines.append(
            "*Estas respuestas poblarán:* `KNOWLEDGE/[specialty].md` (notas por área de especialización)"
        )
        lines.append("")

        lines.append("### P.KNOW.1 — Aprendizaje Actual")
        lines.append("**¿Hay algo que estés aprendiendo en estos momentos?**  ")
        lines.append("Un curso, un lenguaje, una habilidad que persigues.")
        lines.append("")
        lines.append("*Nota destino:* `KNOWLEDGE/knowledge-current-learning.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus aprendizajes en progreso]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.2 — Especialización Futura")
        lines.append(
            "**¿Hay alguna área específica en tu campo que te llame la atención para especializarte o profundizar?**  "
        )
        lines.append("Incluso si ahora es solo un interés vago.")
        lines.append("")
        lines.append("*Nota destino:* `KNOWLEDGE/knowledge-interests.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Áreas que quieres explorar o dominar]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.3 — Expertise Actual")
        lines.append("**¿En qué temas sientes que realmente sabes de qué hablas?**  ")
        lines.append("¿Y en cuáles te gustaría mejorar?")
        lines.append("")
        lines.append("*Nota destino:* `KNOWLEDGE/knowledge-expertise.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tu expertise actual y áreas de mejora]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.4 — Fuentes de Aprendizaje")
        lines.append("**¿De dónde aprendes típicamente?**  ")
        lines.append(
            "¿Blogs, libros, YouTube, comunidades en línea, conversando con otros?"
        )
        lines.append("")
        lines.append("*Nota destino:* `KNOWLEDGE/knowledge-sources.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Tus canales y fuentes de aprendizaje favoritas]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("### P.KNOW.5 — Conceptos Fundamentales")
        lines.append(
            "**¿Hay algún concepto, insight o idea que hayas aprendido que consideres fundamental y que quieras retener?**"
        )
        lines.append("")
        lines.append("*Nota destino:* `KNOWLEDGE/knowledge-insights.md`")
        lines.append("")
        lines.append("**Tu respuesta:**")
        lines.append("```")
        lines.append("[Escribe aquí — Ideas clave que quieres preservar]")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        return lines

    def _build_instructions(self) -> list:
        """Build instructions section."""
        lines = []
        lines.append("## INSTRUCCIONES DE INTEGRACIÓN")
        lines.append("")
        lines.append("### Paso 1: Completa el Cuestionario")
        lines.append("- Responde las 31 preguntas en este documento")
        lines.append("- Tómate tiempo (no es una carrera)")
        lines.append("- Sé específico y detallado")
        lines.append("")
        lines.append("### Paso 2: Mapeo a Notas")
        lines.append("Una vez completado, cada respuesta se convierte en una nota:")
        lines.append("")
        lines.append(
            "Consulta **BOOTSTRAP-MAPPING.md** para ver exactamente dónde va cada respuesta."
        )
        lines.append("")
        lines.append("### Paso 3: Crea las Notas")
        lines.append("En Obsidian:")
        lines.append("1. Ve a la carpeta correcta (ej: IDENTITY/)")
        lines.append("2. Crea nuevo archivo")
        lines.append("3. Nómbralo según convención")
        lines.append("4. Copia frontmatter estándar")
        lines.append("5. Agrega contenido de la respuesta")
        lines.append("")
        lines.append("### Paso 4: Actualiza Graphify")
        lines.append("```bash")
        lines.append("graphify . --update --no-cluster")
        lines.append("```")
        lines.append("")
        lines.append("### Paso 5: Valida")
        lines.append("- Abre vault en Obsidian")
        lines.append("- Verifica que carguen todas las notas")
        lines.append("- Revisa Graph View para ver conexiones")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Instrucciones finales:**")
        lines.append(
            "1. **Responde con honestidad**: No hay respuestas correctas. Esto es para ti."
        )
        lines.append(
            "2. **Tómate tu tiempo**: No tengas prisa. Reflexiona genuinamente sobre cada pregunta."
        )
        lines.append(
            "3. **Sé específico**: Los detalles y ejemplos concretos harán tu KB mucho más útil."
        )
        lines.append(
            "4. **Actualiza regularmente**: Vuelve a estas preguntas cada 2-3 meses. Tu KB debe crecer contigo."
        )
        lines.append(
            "5. **Largo no es problema**: Responde todo lo que necesites. Más contexto = mejor KB."
        )
        lines.append("")
        lines.append("---")
        lines.append("")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        lines.append(f"**Total completado:** 31 preguntas en 6 categorías")
        lines.append(f"**Generado:** {timestamp}")
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
                "how_to_respond": "Responde con sinceridad. No hay respuestas correctas.",
                "recommended_length": "2-5 parrafos por pregunta (sin limite maximo)",
                "estimated_duration": "45-90 minutos total",
                "agent_mode": "Si dices 'Comienza con el bootstrap', el agente hara las preguntas una a una"
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

When user says any of these, activate bootstrap interactive mode:
- "comienza con el bootstrap"
- "comienza bootstrap"
- "inicia bootstrap"
- "responder preguntas de bootstrap"

## What to Do

1. Load questions from BOOTSTRAP-QUESTIONS.json
2. Ask 31 questions one by one with format: [CATEGORY - X/31]
3. Record each response
4. Update BOOTSTRAP-QUESTIONNAIRE.md with responses
5. Show progress: "Vamos por X/31"

## Question Format

```
[IDENTITY - 1/31]

**P.ID.1 — Perfil Personal**

[Question text]

[Context if available]

Adelante, te escucho.
```

## Response Recording

1. User answers
2. You confirm: "Entendido. Registrado."
3. Ask next question
4. Continue until 31 or user says "pausa"

## Session End

After all 31 questions:
```
Excelente. He completado las 31 preguntas.
Ahora actualizare el archivo BOOTSTRAP-QUESTIONNAIRE.md
```

Then update the file with all responses.

## Rules

- No emoticons/emojis
- Accept any response length
- Do NOT critique responses
- Record exactly what user says
- Maintain Spanish language
- Show X/31 progress always

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
        response_pattern = r"\\*\\*Tu respuesta:\\*\\*\\n```\\n(.*?)\\n```"
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
        lines.append('title: "BOOTSTRAP-MAPPING - Referencia de Mapeo P→Nota"')
        lines.append('type: "index"')
        lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"modified: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("tags: [bootstrap, mapping, reference]")
        lines.append('status: "active"')
        lines.append("context_for_claude: false")
        lines.append("---")
        lines.append("")
        lines.append("# BOOTSTRAP MAPPING — Pregunta → Nota de KB")
        lines.append("")
        lines.append(
            "**Referencia rápida para convertir respuestas del cuestionario en notas del vault.**"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## IDENTITY — Quién Eres (6 preguntas → 4 notas)")
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Sección |")
        lines.append("|---|----------|--------------|---------|")
        lines.append(
            "| P.ID.1 | ¿Cómo te describirías? | `IDENTITY/identity-profile.md` | Perfil principal |"
        )
        lines.append(
            "| P.ID.2 | ¿Cuáles son tus valores? | `IDENTITY/identity-values.md` | Valores fundamentales |"
        )
        lines.append(
            '| P.ID.3 | Momentos que te marcaron | `IDENTITY/identity-bio.md` | Sección: "Mi Historia" |'
        )
        lines.append(
            "| P.ID.4 | ¿Cómo prefieres que te hablen? | `IDENTITY/identity-voice.md` | Tu voz y comunicación |"
        )
        lines.append(
            "| P.ID.5 | ¿Qué crees sobre trabajo/éxito? | `IDENTITY/identity-values.md` | Creencias profundas |"
        )
        lines.append(
            "| P.ID.6 | ¿Tu frase/principio personal? | `IDENTITY/identity-profile.md` | Epígrafe o lema |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## PREFERENCES — Cómo Te Gusta Trabajar (6 preguntas → 3 notas)")
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Sección |")
        lines.append("|---|----------|--------------|---------|")
        lines.append(
            "| P.PREF.1 | ¿Cómo sería tu día ideal? | `PREFERENCES/preferences-lifestyle.md` | Rutina diaria |"
        )
        lines.append(
            "| P.PREF.2 | Entorno perfecto | `PREFERENCES/preferences-work-style.md` | Ambiente de trabajo |"
        )
        lines.append(
            "| P.PREF.3 | Herramientas imprescindibles | `PREFERENCES/preferences-tools.md` | Stack de herramientas |"
        )
        lines.append(
            "| P.PREF.4 | Modo de comunicación | `PREFERENCES/preferences-work-style.md` | Preferencias comunicativas |"
        )
        lines.append(
            "| P.PREF.5 | Hábitos no negociables | `PREFERENCES/preferences-lifestyle.md` | Rutinas y hábitos |"
        )
        lines.append(
            "| P.PREF.6 | Relación con dinero | `PREFERENCES/preferences-lifestyle.md` | Filosofía personal |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## WORK — Tu Vida Profesional (5 preguntas → 4 notas)")
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Sección |")
        lines.append("|---|----------|--------------|---------|")
        lines.append(
            "| P.WORK.1 | Tu trabajo actual | `WORK/work-overview.md` | Contexto general |"
        )
        lines.append(
            "| P.WORK.2 | Día ideal vs malo | `WORK/work-current-role.md` | Dinámicas de energía |"
        )
        lines.append(
            "| P.WORK.3 | Tu formación/especialidad | `WORK/work-current-role.md` | Expertise |"
        )
        lines.append(
            "| P.WORK.4 | Personas clave | `WORK/work-team.md` | Relaciones profesionales |"
        )
        lines.append(
            "| P.WORK.5 | Trayectoria profesional | `WORK/work-overview.md` | Historia profesional |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## PROJECTS — Qué Estás Haciendo (4 preguntas → Dinámico)")
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Tipo |")
        lines.append("|---|----------|--------------|------|")
        lines.append(
            "| P.PROJ.1 | Proyectos activos | `PROJECTS/[project-name].md` | Uno por proyecto |"
        )
        lines.append(
            "| P.PROJ.2 | Proyectos futuros | `PROJECTS/[project-name].md` | Uno por proyecto ideado |"
        )
        lines.append(
            "| P.PROJ.3 | Proyectos de orgullo | `PROJECTS/[project-name].md` | Uno por proyecto archived |"
        )
        lines.append(
            '| P.PROJ.4 | Visión a largo plazo | `PROJECTS/INDEX-PROJECTS.md` | Sección: "2-3 año vision" |'
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(
            "## PERSONAL-SPACE — Ocio y Entretenimiento (5 preguntas → 2 notas)"
        )
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Subsección |")
        lines.append("|---|----------|--------------|-----------|")
        lines.append(
            "| P.PERS.1 | Películas/series favoritas | `PERSONAL-SPACE/personal-interests.md` | Watchlist |"
        )
        lines.append(
            "| P.PERS.2 | Libros impactantes | `PERSONAL-SPACE/personal-interests.md` | Readlist |"
        )
        lines.append(
            "| P.PERS.3 | Tiempo libre y hobbies | `PERSONAL-SPACE/personal-hobbies.md` | Actividades principales |"
        )
        lines.append(
            "| P.PERS.4 | Frases/citas inspiradoras | `PERSONAL-SPACE/personal-interests.md` | Quotes |"
        )
        lines.append(
            "| P.PERS.5 | Música y podcasts | `PERSONAL-SPACE/personal-interests.md` | Audio |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## KNOWLEDGE — Lo Que Aprendes (5 preguntas → 5 notas)")
        lines.append("")
        lines.append("| # | Pregunta | Nota Destino | Contenido |")
        lines.append("|---|----------|--------------|----------|")
        lines.append(
            "| P.KNOW.1 | Aprendizaje actual | `KNOWLEDGE/knowledge-current-learning.md` | Cursos, idiomas, habilidades en progreso |"
        )
        lines.append(
            "| P.KNOW.2 | Especialización futura | `KNOWLEDGE/knowledge-interests.md` | Áreas a explorar |"
        )
        lines.append(
            "| P.KNOW.3 | Tu expertise actual | `KNOWLEDGE/knowledge-expertise.md` | Lo que sabes bien + áreas de mejora |"
        )
        lines.append(
            "| P.KNOW.4 | Fuentes de aprendizaje | `KNOWLEDGE/knowledge-sources.md` | Canales: blogs, libros, YouTube, etc. |"
        )
        lines.append(
            "| P.KNOW.5 | Conceptos fundamentales | `KNOWLEDGE/knowledge-insights.md` | Ideas clave a retener |"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## FRONTMATTER ESTÁNDAR PARA TODAS LAS NOTAS")
        lines.append("")
        lines.append("```yaml")
        lines.append("---")
        lines.append('title: "[Título específico]"')
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
            "**Nota:** `context_for_claude: true` para que el agente cargue estas notas automáticamente en futuras sesiones."
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(
            "**Este documento es tu referencia rápida durante la integración.**"
        )
        lines.append("")

        return "\n".join(lines)
