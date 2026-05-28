"""Templates generator for note creation patterns."""

from datetime import datetime
from pathlib import Path


class TemplateGenerator:
    """Generates standardized note templates respecting T0.1.1 specification."""

    # Template definitions: name, type, description
    TEMPLATES = {
        "Person.md": {
            "type": "identity",
            "description": "Para capturar información sobre contactos y colaboradores",
            "tags": ["person", "professional", "active"],
        },
        "Project.md": {
            "type": "project",
            "description": "Para documentar proyectos en curso o completados",
            "tags": ["project", "active"],
        },
        "Technical-Concept.md": {
            "type": "knowledge",
            "description": "Para explicar tecnologías, arquitecturas y patrones",
            "tags": ["knowledge", "active"],
        },
        "Decision.md": {
            "type": "project",
            "description": "Para documentar decisiones arquitectónicas y técnicas (ADR)",
            "tags": ["decision", "architecture", "active"],
        },
        "General-Note.md": {
            "type": "knowledge",
            "description": "Para capturar reflexiones e información miscelánea",
            "tags": ["note", "active"],
        },
    }

    def __init__(self, vault_path: str):
        """
        Initialize the template generator.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)

    def generate(self) -> None:
        """Generate all template files in TEMPLATES/ folder."""
        templates_path = self.vault_path / "TEMPLATES"
        templates_path.mkdir(parents=True, exist_ok=True)

        # Generate each template
        for filename, config in self.TEMPLATES.items():
            template_file = templates_path / filename
            if not template_file.exists():
                content = self._generate_template_content(
                    filename,
                    config["type"],
                    config["tags"],
                )
                template_file.write_text(content, encoding="utf-8")

        # Generate README.md with instructions
        self._create_templates_readme(templates_path)

    def _generate_template_content(
        self,
        filename: str,
        note_type: str,
        tags: list,
    ) -> str:
        """
        Generate template content with proper frontmatter.

        Args:
            filename: Template filename
            note_type: YAML type field value
            tags: List of tags for the template

        Returns:
            Template content as string
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        tags_str = ", ".join(tags)

        if filename == "Person.md":
            return f"""---
title: "Nombre de la persona"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
identity_aspect: "professional"
related_notes: []
context_for_claude: false
---

# [[Nombre de la persona]]

## TL;DR
[Resumen de 1-2 líneas: nombre, rol principal y por qué es importante en tu KB.]

## Información básica
- **Rol/Función:** [Descripción del rol o función]
- **Organización:** [Empresa, equipo o contexto]
- **Ubicación:** [Ciudad, país o contexto remoto]
- **Contacto:** [Email, teléfono, o enlace de contacto]

## Descripción
[Párrafo descriptivo sobre la persona: quién es, qué hace, relevancia en proyectos actuales.]

## Relaciones y contexto
- Participa en: [[project-example]], [[project-volta]]
- Reporta a: [[identity-person-name]]
- Colabora con: [[identity-person-a]], [[identity-person-b]]
- Expertise: [[knowledge-technical-skill]], [[knowledge-domain]]

## Notas
[Observaciones, preferencias de comunicación, antecedentes relevantes o contexto adicional.]

## Relaciones con otros módulos
- [[project-example]] — Proyectos en los que participa
- [[work-current-role]] — Contexto laboral relevante
- [[knowledge-skill]] — Áreas de expertise
"""

        elif filename == "Project.md":
            return f"""---
title: "Nombre del proyecto"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
project_status: "in-progress"
start_date: {date_str}
target_date:
---

# [[Nombre del proyecto]]

## TL;DR
[Resumen de 1-2 líneas: qué es el proyecto, estado actual y dueño principal.]

## Descripción
[Resumen de qué es el proyecto y su propósito.]

## Información general
- **Responsable:** [[identity-person-name]]
- **Equipo:** [[identity-person-a]], [[identity-person-b]], [[identity-person-c]]
- **Fechas:** Inicio: {date_str} | Fin estimado: [YYYY-MM-DD]
- **Estado:** In Progress | Planning | On Hold | Completed | Cancelled

## Objetivos
- [Objetivo 1]
- [Objetivo 2]
- [Objetivo 3]

## Contexto
[Descripción de por qué existe el proyecto, problema a resolver, o contexto empresarial.]

## Componentes y entregables
- [[knowledge-technical-concept]] — [Descripción breve]
- [[knowledge-another-concept]] — [Descripción breve]

## Decisiones clave
- [[decision-architecture]] — Decisión arquitectónica
- [[decision-technical]] — Decisión técnica

## Riesgos y dependencias
- **Riesgo 1:** [Descripción] | Mitigación: [...]
- **Dependencia:** Relacionado con [[project-other]] o [[knowledge-domain]]

## Notas y próximos pasos
[Avances recientes, blockers, o acciones pendientes.]

## Relaciones con otros módulos
- [[identity-person]] — Equipo involucrado
- [[knowledge-concept]] — Conceptos técnicos relacionados
- [[project-dependent]] — Proyectos dependientes
"""

        elif filename == "Technical-Concept.md":
            return f"""---
title: "Nombre del concepto técnico"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
knowledge_domain: "backend-engineering"
learnings: ["learning1", "learning2"]
---

# [[Nombre del concepto técnico]]

## TL;DR
[Resumen de 1-2 líneas: qué es, para qué sirve y por qué importa.]

## Definición
[Explicación clara y concisa de qué es este concepto.]

## Contexto y por qué importa
[Por qué este concepto es relevante en el contexto de VOLTA o el negocio.]

## Componentes o pilares clave
- [Componente 1 y explicación]
- [Componente 2 y explicación]

## Ejemplos de uso
```
[Fragmento de código, diagrama o ejemplo práctico]
```

## Relaciones
- **Usa:** [[knowledge-concept-a]], [[knowledge-concept-b]]
- **Usado por:** [[project-example]], [[decision-example]]
- **Similar a:** [[knowledge-concept-c]]
- **Contrasta con:** [[knowledge-concept-d]]

## Recursos y referencias
- [URL de documentación oficial]
- [Artículo o tutorial recomendado]
- [[knowledge-personal-learning]]

## Notas
[Observaciones personales, casos de uso específicos, o advertencias.]

## Relaciones con otros módulos
- [[project-using-concept]] — Proyectos que usan este concepto
- [[identity-person-expert]] — Personas con expertise
- [[decision-related]] — Decisiones relacionadas
"""

        elif filename == "Decision.md":
            return f"""---
title: "Título de la decisión"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
---

# [[Título de la decisión]]

## TL;DR
[Resumen de 1-2 líneas: qué se decidió y por qué.]

## Contexto
[Descripción del problema o pregunta que requería decisión. Incluir restricciones, requisitos y contexto empresarial.]

## Opciones consideradas

### Opción A: [Nombre]
- **Pros:** [..., ...]
- **Contras:** [..., ...]

### Opción B: [Nombre]
- **Pros:** [..., ...]
- **Contras:** [..., ...]

### Opción C: [Nombre]
- **Pros:** [..., ...]
- **Contras:** [..., ...]

## Decisión tomada
**Elegida:** Opción [X]: [Nombre]

## Justificación
[Explicación clara de por qué se eligió esta opción sobre las otras. Incluir ponderación de criterios y trade-offs.]

## Consecuencias esperadas
- **Positivas:** [..., ...]
- **Negativas o compromisos:** [..., ...]

## Personas involucradas
- [[identity-person-1]] — Tomó la decisión
- [[identity-person-2]] — Consultado
- [[identity-person-3]] — Afectado

## Componentes afectados
- [[project-example]] — Proyecto impactado
- [[knowledge-concept]] — Concepto técnico relacionado

## Notas de seguimiento
[Cómo se implementará, quién es responsable, timeline esperado.]

## Relaciones con otros módulos
- [[project-related]] — Proyecto en el que se toma esta decisión
- [[decision-predecessor]] — Decision anterior que respalda esta
- [[knowledge-concept]] — Conceptos técnicos involucrados
"""

        else:  # General-Note.md
            return f"""---
title: "Título de la nota"
type: "{note_type}"
created: {date_str}
modified: {date_str}
tags: [{tags_str}]
status: "active"
knowledge_domain: "general"
---

# [[Título de la nota]]

## TL;DR
[Resumen de 1-2 líneas: qué es esta nota y por qué importa.]

## Contenido
[Cuerpo libre. Puede incluir párrafos, listas, fragmentos de código, preguntas o reflexiones.]

## Contexto (opcional)
[Dónde encaja esta nota en el sistema más grande. Qué problema resuelve o qué pregunta contesta.]

## Acciones pendientes (si aplica)
- [ ] [Acción 1]
- [ ] [Acción 2]

## Notas adicionales
[Observaciones finales, referencias internas o advertencias.]

## Relaciones con otros módulos
- [[note-related]] — Notas relacionadas
- [[project-o-person]] — Proyectos o personas relevantes
- [[knowledge-concept]] — Conceptos relacionados
"""

    def _create_templates_readme(self, templates_path: Path) -> None:
        """Create README.md with template usage instructions for Claude agent."""
        readme_file = templates_path / "README.md"
        if readme_file.exists():
            return

        content = """---
title: "Templates - Guía de uso para agente Claude"
type: "index"
created: {created}
modified: {created}
tags: [templates, navigation, hub, ai]
status: "active"
---

# Templates - Guía de Uso

Estas plantillas estandarizan la captura de información en tu knowledge base. Cada plantilla incluye frontmatter YAML obligatorio que permite búsqueda, filtrado y procesamiento automático por agentes Claude.

## Categorías de plantillas

### 1. **Person.md** — Contactos y colaboradores
- **Type:** `identity`
- **Tags:** `[person, professional, active]`
- **Cuándo usarla:** Para documentar personas clave en tu contexto laboral o personal
- **Contenido:** Rol, organización, relaciones, expertise
- **Ejemplo:** "person-john-doe.md", "person-maria-boss.md"

### 2. **Project.md** — Proyectos activos y pasados
- **Type:** `project`
- **Tags:** `[project, active, [domain-work|personal]]`
- **Cuándo usarla:** Para documentar cualquier proyecto (laboral o personal)
- **Contenido:** Descripción, objetivos, equipo, fechas, estado, riesgos
- **Ejemplo:** "project-volta.md", "project-home-renovation.md"

### 3. **Technical-Concept.md** — Tecnologías, patrones, arquitecturas
- **Type:** `knowledge`
- **Tags:** `[knowledge, [backend|frontend|architecture|pattern], active]`
- **Cuándo usarla:** Para explicar conceptos técnicos que necesitas recordar
- **Contenido:** Definición, componentes, ejemplos, relaciones, recursos
- **Ejemplo:** "knowledge-llm-basics.md", "knowledge-microservices.md"

### 4. **Decision.md** — Decisiones arquitectónicas (ADR format)
- **Type:** `project` (con tag `decision`)
- **Tags:** `[decision, [architecture|business|process], active]`
- **Cuándo usarla:** Para documentar decisiones importantes con su contexto y rationale
- **Contenido:** Problema, opciones, decisión tomada, justificación, consecuencias
- **Ejemplo:** "decision-database-postgres.md", "decision-react-framework.md"

### 5. **General-Note.md** — Reflexiones y notas misceláneas
- **Type:** `knowledge`
- **Tags:** `[note, [categoría-libre], active]`
- **Cuándo usarla:** Para capturar reflexiones que no encajan en otras categorías
- **Contenido:** Flexible (párrafos, listas, preguntas, ideas)
- **Ejemplo:** "note-weekly-reflection.md", "note-api-design-thoughts.md"

---

## Frontmatter YAML obligatorio

Todas las notas DEBEN incluir este frontmatter al inicio:

```yaml
---
title: "Título de la nota (máx 100 caracteres)"
type: "identity | preference | work | project | knowledge | personal | index"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: "active | archived | draft"
---
```

**Campos obligatorios:**
- `title`: Descripción clara del contenido
- `type`: Categoría de la nota (según plantilla)
- `created`: Fecha de creación
- `modified`: Última fecha de edición
- `tags`: Array de etiquetas (máx 5)
- `status`: Estado actual de la nota

**Campos opcionales por tipo:**
- **Person:** `identity_aspect`, `related_notes`, `context_for_claude`
- **Project:** `project_status`, `start_date`, `target_date`
- **Technical-Concept:** `knowledge_domain`, `learnings`
- **Decision:** (ninguno especial, usa tags)
- **General-Note:** `knowledge_domain`

---

## Cómo usar las plantillas en Obsidian

### Opción 1: Insertar plantilla (recomendado)
1. Abre el menú de Obsidian: `Ctrl+Shift+P` (Windows) o `Cmd+Shift+P` (Mac)
2. Busca "Insert template"
3. Elige la plantilla según el tipo de nota
4. Completa el frontmatter YAML
5. Rellena el contenido

### Opción 2: Copiar manualmente
1. Abre el archivo de plantilla en `TEMPLATES/[Template-Name].md`
2. Copia todo el contenido
3. Crea una nueva nota en la carpeta apropiada
4. Pega el contenido y personaliza

---

## Sistema de tags (respeto a T0.1.1)

Los tags deben seguir estas categorías:

**Domain (Dominio):**
- `work`, `personal`, `ai`

**Subtema (Subtópico específico):**
- `backend`, `frontend`, `architecture`, `pattern`, `typescript`, etc.

**Temporal (Estado temporal):**
- `active`, `archived`, `draft`, `review`

**Relación (Relación con otras notas):**
- `blocker`, `depends-on`, `decision`, `principle`, `needs-update`

**Metadata (Metainformación):**
- `index`, `navigation`, `hub`, `template`

**Ejemplos de uso:**
- Person: `[person, professional, active]`
- Project: `[project, active, work, backend]`
- Technical-Concept: `[knowledge, typescript, active, backend]`
- Decision: `[decision, architecture, active]`
- General-Note: `[note, reflection, active]`

---

## Convenciones de nomenclatura

Las notas deben nombrarse con prefijo + descripción:

```
[category]-[descriptive-name].md

Ejemplos:
- person-john-doe.md
- person-maria-boss.md
- project-volta.md
- project-home-renovation.md
- knowledge-llm-basics.md
- knowledge-react-hooks.md
- decision-database-postgres.md
- decision-react-framework.md
- note-weekly-reflection.md
- note-architecture-thoughts.md
```

**Reglas:**
- Usar inglés principalmente (excepto si traducir pierde significado)
- Minúsculas y guiones (kebab-case)
- Conciso pero descriptivo
- Sin espacios ni caracteres especiales

---

## 🔗 Links y relaciones

Las plantillas incluyen una sección "Relaciones con otros módulos" para crear backlinks.

**Sintaxis de Obsidian:**
```markdown
[[note-name]] — Descripción de por qué está relacionada

[[project-volta]] — Proyecto principal en el que trabajo
[[knowledge-llm-basics]] — Concepto técnico fundamental
[[identity-values]] — Valores que guían mis decisiones
```

**Máximo 5 links por nota** para evitar saturar el grafo.

---

## Checklist para nueva nota

- [ ] Elegí la plantilla correcta según el tipo de contenido
- [ ] Completo el frontmatter YAML (title, type, created, modified, tags, status)
- [ ] Incluí un TL;DR de 1-2 líneas
- [ ] Agregué la descripción/contenido principal
- [ ] Creé máximo 5 links en "Relaciones con otros módulos"
- [ ] Guardé la nota con nombre: `[category]-[name].md`

---

## Relación con outras carpetas

Las plantillas generadas aquí se usan para crear notas en:
- **IDENTITY/** — Para notas de tipo persona
- **PROJECTS/** — Para notas de tipo project
- **KNOWLEDGE/** — Para notas de tipo technical-concept y general-note
- **AI-SYSTEM/CONTEXT/** — Para notas de contexto del agente

---

## Nota para agente Claude

Este README contiene las instrucciones para determinar **cuándo y cómo usar cada plantilla**. Al crear nuevas notas:

1. **Identifica el tipo de contenido** según los 5 tipos disponibles
2. **Elige la plantilla correspondiente**
3. **Respeta el frontmatter YAML** obligatorio
4. **Usa el sistema de tags** de T0.1.1
5. **Crea links relevantes** (máximo 5 por nota)

Las plantillas facilitan contexto consistente y permiten búsqueda y filtrado automático.

---

**Creado:** {created}
**Última actualización:** {created}
**Versión:** 1.0.0
""".format(created=datetime.now().strftime("%Y-%m-%d"))

        readme_file.write_text(content, encoding="utf-8")
