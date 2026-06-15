"""Structure generator for vault folder hierarchy."""

from datetime import datetime
from pathlib import Path


class StructureGenerator:
    """Generates the complete folder and file structure for a Wolta vault."""

    # Main categories from T0.1.1
    MAIN_CATEGORIES = [
        "IDENTITY",
        "PREFERENCES",
        "WORK",
        "PROJECTS",
        "PERSONAL-SPACE",
        "KNOWLEDGE",
        "AI-SYSTEM",
    ]

    # Subcategories for AI-SYSTEM (including BOOTSTRAP)
    AI_SYSTEM_SUBCATEGORIES = [
        "AGENTS",
        "BOOTSTRAP",
        "CONTEXT",
        "SESSIONS",
        "SKILLS",
        "WORKFLOWS",
    ]

    # Base files to create in each category
    CATEGORY_FILES = {
        "IDENTITY": [
            "INDEX-IDENTITY.md",
            "identity-profile.md",
            "identity-values.md",
            "identity-voice.md",
            "identity-bio.md",
        ],
        "PREFERENCES": [
            "INDEX-PREFERENCES.md",
            "preferences-tools.md",
            "preferences-work-style.md",
            "preferences-lifestyle.md",
        ],
        "WORK": [
            "INDEX-WORK.md",
            "work-overview.md",
            "work-current-role.md",
            "work-company.md",
            "work-team.md",
        ],
        "PROJECTS": ["INDEX-PROJECTS.md"],
        "PERSONAL-SPACE": [
            "INDEX-PERSONAL-SPACE.md",
            "personal-hobbies.md",
            "personal-interests.md",
        ],
        "KNOWLEDGE": ["INDEX-KNOWLEDGE.md"],
        "AI-SYSTEM": ["INDEX-AI-SYSTEM.md"],
    }

    # Files to create in AI-SYSTEM subcategories
    SUBCATEGORY_FILES = {
        "BOOTSTRAP": [],  # bootstrap-questions.md will be generated separately
        "CONTEXT": ["context-current.md"],
        "AGENTS": [],
        "SESSIONS": [],
        "SKILLS": [],
        "WORKFLOWS": [],
    }

    def __init__(self, vault_path: str):
        """
        Initialize the structure generator.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)

    def generate(self) -> None:
        """Generate the complete vault structure."""
        # Create main categories
        for category in self.MAIN_CATEGORIES:
            self._create_category(category)

        # Create AI-SYSTEM subcategories
        ai_system_path = self.vault_path / "AI-SYSTEM"
        for subcategory in self.AI_SYSTEM_SUBCATEGORIES:
            self._create_subcategory(ai_system_path, subcategory)

        # Create special folders
        self._create_templates_folder()
        self._create_wolta_config_folder()
        self._create_raw_folder()

        # Create reference documents
        self._create_design_file()
        self._create_readme_file()

        # Create agent instruction files (Option B: skill logic in vault)
        self._create_claude_md()
        self._create_bootstrap_generate_skill()
        self._create_ingest_protocol()
        self._create_source_adapter_template()
        self._create_source_files_adapter()

    def _create_category(self, category: str) -> None:
        """Create a main category folder with its files."""
        category_path = self.vault_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        # Create files for this category
        files = self.CATEGORY_FILES.get(category, [])
        for filename in files:
            file_path = category_path / filename
            if not file_path.exists():
                self._create_file_with_frontmatter(file_path, category, filename)

    def _create_subcategory(self, parent_path: Path, subcategory: str) -> None:
        """Create a subcategory folder with its files."""
        subcategory_path = parent_path / subcategory
        subcategory_path.mkdir(parents=True, exist_ok=True)

        # Create files for this subcategory (skip BOOTSTRAP - it's handled separately)
        if subcategory != "BOOTSTRAP":
            files = self.SUBCATEGORY_FILES.get(subcategory, [])
            for filename in files:
                file_path = subcategory_path / filename
                if not file_path.exists():
                    self._create_file_with_frontmatter(
                        file_path,
                        f"AI-SYSTEM/{subcategory}",
                        filename,
                    )

    def _create_templates_folder(self) -> None:
        """Create TEMPLATES folder with a base template."""
        templates_path = self.vault_path / "TEMPLATES"
        templates_path.mkdir(parents=True, exist_ok=True)

        template_file = templates_path / "template-note.md"
        if not template_file.exists():
            content = """---
title: "[Nota nueva]"
type: "identity | preference | work | project | knowledge | personal"
created: {{date}}
modified: {{date}}
tags: [tag1, tag2]
status: "draft"
---

## Contenido

[Escribe aquí]

## Relaciones

[Links a otras notas]
"""
            template_file.write_text(content, encoding="utf-8")

    def _create_wolta_config_folder(self) -> None:
        """Create .wolta configuration folder."""
        wolta_path = self.vault_path / ".wolta"
        wolta_path.mkdir(parents=True, exist_ok=True)

        # Create a config file
        config_file = wolta_path / "config.md"
        if not config_file.exists():
            content = """# Wolta Configuration

This folder contains Wolta-specific configuration files and metadata.

## Folders

- **initialized**: Marker file indicating vault initialization status
- **config.md**: This configuration file

## Metadata

- Created: {created}
- Version: 0.1.0

## Next Steps

1. Configure Obsidian vault settings
2. Complete bootstrap questions in AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md
3. Populate knowledge base categories
""".format(created=datetime.now().isoformat())
            config_file.write_text(content, encoding="utf-8")

    def _create_raw_folder(self) -> None:
        """Create raw/ staging directory for unprocessed source files.

        raw/           - Drop zone for source files before ingestion
        raw/processed/ - Processed source files (audit trail, never deleted)
        raw/.gitkeep   - Keeps raw/ tracked in git even when empty
        """
        raw_path = self.vault_path / "raw"
        processed_path = raw_path / "processed"

        raw_path.mkdir(parents=True, exist_ok=True)
        processed_path.mkdir(parents=True, exist_ok=True)

        # .gitkeep so both dirs are tracked in git when empty
        for keep_path in (raw_path / ".gitkeep", processed_path / ".gitkeep"):
            if not keep_path.exists():
                keep_path.touch()

        # README inside raw/ so the agent and user know the rules
        readme = raw_path / "README.md"
        if not readme.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            content = f"""# raw/ — Zona de Staging para Ingesta

Este directorio recibe archivos fuente **sin procesar** que el agente convertirá en notas válidas de la KB.

## Reglas

- Deposita aquí cualquier archivo que quieras ingestar: `.md`, `.txt`, `.pdf`, `.docx`
- Los archivos aquí **no son notas válidas** de la KB: no llevan frontmatter y no aparecen en el Graph View
- Una vez procesado un archivo, el agente lo mueve a `raw/processed/` — no lo elimina
- Si no puedes exportar una fuente (ej: WhatsApp, Notion con restricciones), pega el contenido manualmente en un `.md` nuevo aquí

## Cómo disparar la ingesta

Una vez que hayas depositado tus archivos, di al agente:

- `/raw-ingest`
- "procesa los archivos en raw"
- "ingesta mi información personal"

## Flujo completo

Ver `AI-SYSTEM/SKILLS/raw-ingest.md` para el runbook que sigue el agente.

---

*Generado por wolta init · {today}*
"""
            readme.write_text(content, encoding="utf-8")

    def _create_file_with_frontmatter(
        self,
        file_path: Path,
        category: str,
        filename: str,
    ) -> None:
        """Create a file with YAML frontmatter."""
        # Determine the type based on category
        type_mapping = {
            "IDENTITY": "identity",
            "PREFERENCES": "preference",
            "WORK": "work",
            "PROJECTS": "project",
            "PERSONAL-SPACE": "personal",
            "KNOWLEDGE": "knowledge",
        }

        # Extract base type from category
        base_type = type_mapping.get(category.split("/")[0], "index")

        # Build frontmatter
        frontmatter = f"""---
title: "{filename.replace("-", " ").replace(".md", "").title()}"
type: "{base_type}"
created: {datetime.now().strftime("%Y-%m-%d")}
modified: {datetime.now().strftime("%Y-%m-%d")}
tags: []
status: "active"
---

## Contenido

[Completa esta sección]

## Relaciones

[Agrega links a otras notas si aplica]
"""

        file_path.write_text(frontmatter, encoding="utf-8")

    def _create_design_file(self) -> None:
        """Create DESIGN.md specification file in vault root."""
        design_file = self.vault_path / "DESIGN.md"
        if design_file.exists():
            return

        content = """---
title: "DESIGN - Especificación de la KB-PERSONAL"
type: "index"
created: {created}
modified: {created}
tags: [design, architecture, kb-structure]
status: "active"
---

# DESIGN — Especificación de KB-PERSONAL

**Vault:** KB-PERSONAL
**Status:** Activa

---

## 1. Objetivo del Vault

Centralizar información personal y laboral en una Knowledge Base consultable por agentes Claude. Sistema híbrido PARA + Zettelkasten para máxima flexibilidad.

---

## 2. Estructura de Carpetas

```
wolta-vault/
├── IDENTITY/               # Quién eres: perfil, valores, historia, voz
│   ├── INDEX-IDENTITY.md
│   ├── identity-profile.md
│   ├── identity-values.md
│   ├── identity-voice.md
│   └── identity-bio.md
│
├── PREFERENCES/            # Gustos, hábitos, configuraciones personales
│   ├── INDEX-PREFERENCES.md
│   ├── preferences-tools.md
│   ├── preferences-work-style.md
│   └── preferences-lifestyle.md
│
├── WORK/                   # Contexto profesional: empresa, rol, equipo
│   ├── INDEX-WORK.md
│   ├── work-overview.md
│   ├── work-current-role.md
│   ├── work-company.md
│   └── work-team.md
│
├── PROJECTS/               # Proyectos activos y pasados
│   └── INDEX-PROJECTS.md
│
├── PERSONAL-SPACE/         # Contenido cotidiano: películas, libros, frases
│   ├── INDEX-PERSONAL-SPACE.md
│   ├── personal-hobbies.md
│   └── personal-interests.md
│
├── KNOWLEDGE/              # Contenido educativo: cursos, estudios, investigaciones
│   └── INDEX-KNOWLEDGE.md
│
├── AI-SYSTEM/              # Recursos operativos del agente
│   ├── INDEX-AI-SYSTEM.md
│   ├── BOOTSTRAP/          # Población inicial de la KB
│   │   ├── INDEX-BOOTSTRAP.md
│   │   ├── BOOTSTRAP-QUESTIONNAIRE.md    # 27 preguntas
│   │   └── BOOTSTRAP-MAPPING.md          # Mapeo P→nota
│   ├── AGENTS/             # Definición de agentes
│   ├── CONTEXT/            # Contexto actual del agente
│   │   └── context-current.md
│   ├── SESSIONS/           # Historial de sesiones
│   ├── SKILLS/             # Skills y prompts disponibles
│   └── WORKFLOWS/          # Workflows y automations
│
├── TEMPLATES/              # Plantillas para nuevas notas
│   └── template-note.md
│
├── raw/                    # Staging de archivos fuente sin procesar
│   ├── processed/          # Archivos ya procesados (auditoría)
│   └── README.md           # Reglas del directorio
│
├── DESIGN.md               # Este documento (especificación del vault)
├── README.md               # Guía de inicio rápido
│
└── graphify-out/           # Grafo de conocimiento generado
    ├── graph.json          # Estructura queryable
    ├── GRAPH_REPORT.md     # Análisis del grafo
    └── graph.html          # Visualización interactiva
```

---

## 3. Frontmatter Estándar

Todos los archivos .md deben incluir:

```yaml
---
title: "Título descriptivo"
type: "index | identity | preference | work | project | knowledge | personal"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: "active | draft | archived"
context_for_claude: true | false
---
```

**Campos opcionales:**
- `index_module`: Para INDEX files, indicar módulo principal
- `related_notes`: Array de notas relacionadas

---

## 4. Sistema de Tags

**Dominios:**
- `identity` / `personal` / `work` / `ai` — categoría principal
- `professional` / `hobby` — contexto

**Temporales:**
- `active` — en uso ahora
- `draft` — borrador, incompleto
- `archived` — histórico

**Relación:**
- `blocker` — depende de otra nota
- `depends-on` — otra nota depende de esta
- `reference` — solo consulta

---

## 5. Bootstrap: Población Inicial

### Carpeta: `AI-SYSTEM/BOOTSTRAP/`

**Hub operativo para población inicial de la KB.**

1. **INDEX-BOOTSTRAP.md** — Hub de navegación y checklist
2. **BOOTSTRAP-QUESTIONNAIRE.md** — 27 preguntas reflexivas (45-90 minutos)
3. **BOOTSTRAP-MAPPING.md** — Referencia pregunta → nota

### Proceso

1. Abre BOOTSTRAP-QUESTIONNAIRE.md en Obsidian
2. Responde cada pregunta (2-5 párrafos por pregunta)
3. Consulta BOOTSTRAP-MAPPING.md para ver dónde mapea cada respuesta
4. Crea notas siguiendo el patrón del mapping
5. Ejecuta graphify para actualizar el grafo:
   ```bash
   graphify /path/to/vault --update --no-cluster
   ```

---

## 6. Grafo de Conocimiento (Graphify)

**Herramienta:** Graphify CLI
**Salida:** `graphify-out/`

**Archivos generados:**
- `graph.json` — Estructura queryable de relaciones
- `GRAPH_REPORT.md` — Análisis del grafo
- `graph.html` — Visualización interactiva

**Comando para actualizar:**
```bash
graphify /path/to/vault --update --no-cluster
```

---

## 7. Próximos Pasos

1. Abre el vault en Obsidian
2. Explora la estructura en el File Explorer
3. Lee README.md para guía rápida
4. Navega a AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md para comenzar
5. Responde BOOTSTRAP-QUESTIONNAIRE.md
6. Ejecuta graphify para actualizar el grafo

---

**Última actualización:** {created}
**Status:** Activa — Lista para uso con bootstrap completado
""".format(created=datetime.now().strftime("%Y-%m-%d"))

        design_file.write_text(content, encoding="utf-8")

    def _create_claude_md(self) -> None:
        """Create CLAUDE.md project instructions in vault root.

        This file is loaded automatically by Claude agents when the vault
        is connected as a project in Cowork. It registers available commands
        and tells the agent how to operate within the vault context.
        """
        claude_file = self.vault_path / "CLAUDE.md"
        if claude_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""# WOLTA — Instrucciones de Proyecto para el Agente Claude

Este vault es una **knowledge base personal** construida con Obsidian y diseñada para ser consultada y operada por agentes Claude. Contiene información personal, profesional y de aprendizaje del propietario.

---

## Contexto del vault

Cuando el usuario conecta este vault como proyecto, carga automáticamente este archivo. El agente debe:

1. Reconocer que está operando dentro de un vault WOLTA
2. Leer los archivos con `context_for_claude: true` para construir el contexto del usuario
3. Responder consultas usando el contenido del vault como fuente primaria de verdad
4. Usar los skills disponibles en `AI-SYSTEM/SKILLS/` para operaciones estructuradas

---

## Comandos fijos

### `/bootstrap-generate`

**Archivo:** `AI-SYSTEM/SKILLS/bootstrap-generate.md`
**Cuándo:** Cuando el usuario haya completado el cuestionario bootstrap y quiera convertir sus respuestas en notas del vault.

Triggers:
- `/bootstrap-generate`
- "genera las notas de mi knowledge base"
- "crea las notas del bootstrap"
- "poblar la kb"
- "convierte las respuestas en notas"

---

## Ingesta desde fuentes externas

El vault usa un sistema de ingesta extensible. El protocolo central está en `AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md`. Los **source adapters** son skills en `AI-SYSTEM/SKILLS/` con el prefijo `source-` que describen cómo extraer información de una fuente específica y producir bloques compatibles con el protocolo.

### Cómo responder cuando el usuario pide ingestar información

**Paso 1 — Identificar la fuente**
Determina de qué fuente viene la información: archivos locales, un directorio, una app externa (Notion, Discord, etc.), contenido de la conversación activa, o cualquier otro origen.

**Paso 2 — Buscar un adapter para esa fuente**
Lista los archivos en `AI-SYSTEM/SKILLS/` que coincidan con el patrón `source-*.md`.
Lee el que corresponda a la fuente solicitada.

**Paso 3 — Si existe el adapter**
Sigue sus instrucciones para la fase de extracción, luego continúa con `INGEST-PROTOCOL.md` para clasificación, gate, escritura y tracking.

**Paso 4 — Si NO existe el adapter**
Presenta al usuario dos opciones:
```
No tengo un adapter configurado para [fuente].
Opciones:
  a) Exportar el contenido manualmente a raw/ y ejecutar /raw-ingest
  b) Crear un adapter para [fuente] usando TEMPLATES/template-source-adapter.md
     (solo necesitas llenar las secciones marcadas — toma ~10 minutos)
```

**Paso 5 — Ingesta desde la conversación activa**
Si en el transcurso de una conversación el usuario explica algo relevante para la KB (contexto de proyecto, decisión técnica, información personal), puedes proponer ingestarlo directamente:
```
Eso parece información valiosa para tu KB.
¿Quieres que lo agregue a [nota destino sugerida]?
```
No ingestar sin confirmación del usuario. La información de la conversación activa no necesita pasar por un archivo fuente.

### Triggers generales de ingesta (cualquier fuente)

- "ingesta mi información de [fuente]"
- "explora [directorio/app] y alimenta la KB"
- "agrega esto a mi KB"
- "procesa [fuente] como notas"
- "/ingest [fuente]"

---

## Directorio raw/

`raw/` es el **adapter universal de fallback**: cualquier fuente sin adapter puede usar este directorio como puente manual. El adapter correspondiente es `AI-SYSTEM/SKILLS/source-files.md`.

Reglas operativas:
1. Los archivos en `raw/` no son notas válidas — no los leas como contexto de la KB
2. No escribas al vault sin aprobación del usuario (gate en INGEST-PROTOCOL.md)
3. Al procesar un archivo, muévelo a `raw/processed/` — nunca lo elimines
4. Atribuye la fuente: agrega `source` e `ingested` en el frontmatter de notas creadas desde `raw/`

---

## Cómo consultar la KB

1. Prioriza siempre el contenido del vault sobre tu conocimiento de entrenamiento para datos del usuario
2. Los archivos con `context_for_claude: true` son fuentes primarias
3. Si la información no está en el vault, dilo explícitamente en lugar de inferirla

---

## Estructura del vault

```
IDENTITY/           → Perfil, valores, historia, voz del propietario
PREFERENCES/        → Estilo de trabajo, herramientas, hábitos
WORK/               → Rol actual, empresa, equipo, trayectoria
PROJECTS/           → Proyectos activos, futuros y de orgullo
PERSONAL-SPACE/     → Hobbies, intereses culturales, frases
KNOWLEDGE/          → Aprendizaje actual, expertise, fuentes
AI-SYSTEM/          → Recursos operativos del agente
  BOOTSTRAP/        → Cuestionario y mapeo de ingesta inicial
  SKILLS/           → Skills del agente
    INGEST-PROTOCOL.md     → Pipeline canónico de ingesta (fuente-agnóstico)
    source-*.md            → Source adapters (uno por fuente)
    bootstrap-generate.md  → Skill de población inicial
  CONTEXT/          → Contexto dinámico de sesión
  SESSIONS/         → Historial de sesiones
  WORKFLOWS/        → Flujos de trabajo automatizados
TEMPLATES/
  template-source-adapter.md  → Plantilla para crear nuevos adapters
raw/                → Staging universal de fallback (NO leer como KB)
  processed/        → Archivos procesados (auditoría)
```

---

## Estado del bootstrap

Lee `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` → campo `status` en frontmatter.
Si `kb_populated: true`, el vault ya fue poblado. Si no, las notas aún no se han generado.

---

## Convenciones de la KB

- Todo archivo relevante tiene `context_for_claude: true` en su frontmatter
- Links internos: `[[nombre-de-nota]]`
- `status`: `active`, `draft` o `archived`
- Notas de PROJECTS con `status: archived` son históricas

---

*Generado por wolta init · {today}*
"""
        claude_file.write_text(content, encoding="utf-8")

    def _create_bootstrap_generate_skill(self) -> None:
        """Create the bootstrap-generate skill instruction file.

        Lives at AI-SYSTEM/SKILLS/bootstrap-generate.md. The agent reads this
        file when /bootstrap-generate is triggered and follows its instructions
        to populate the vault from the completed questionnaire.
        """
        skill_file = self.vault_path / "AI-SYSTEM" / "SKILLS" / "bootstrap-generate.md"
        if skill_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""---
title: "SKILL — bootstrap-generate"
type: "skill"
created: {today}
modified: {today}
tags: [skill, bootstrap, agent, kb-population]
status: "active"
context_for_claude: true
---

# SKILL: bootstrap-generate

**Propósito:** Poblar el vault con las notas iniciales de la knowledge base a partir de las respuestas del cuestionario bootstrap. Este proceso se ejecuta una sola vez, inmediatamente después de que el usuario completa `BOOTSTRAP-QUESTIONNAIRE.md`.

**Ejecutor:** Agente Claude — no el usuario.

---

## Trigger Detection

Activa este skill cuando el usuario diga cualquiera de los siguientes:

- `/bootstrap-generate`
- "genera las notas de mi knowledge base"
- "crea las notas del bootstrap"
- "poblar la kb"
- "generar notas a partir del cuestionario"
- "convierte las respuestas en notas"

---

## Pre-flight: Validación antes de ejecutar

Antes de crear cualquier archivo, verifica que se cumplan estas condiciones:

**1. El cuestionario está completo**
Lee `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md`.
Verifica que el frontmatter contenga `status: "completed"` y que las 31 preguntas tengan respuesta (no deben estar vacías ni contener solo el texto `[Tu respuesta aquí]`).

Si el cuestionario no está completo, responde:
```
El cuestionario bootstrap no está completo aún.
Navega a AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md y responde
todas las preguntas antes de ejecutar este comando.
Para responder de forma conversacional, usa: "comienza bootstrap"
```
Y detén la ejecución.

**2. El vault tiene acceso de escritura**
Confirma que puedes crear archivos en el vault. Si no tienes acceso de escritura, informa al usuario y detén la ejecución.

**3. Informar al usuario antes de proceder**
Una vez validado, muestra este mensaje y espera confirmación:
```
Listo para poblar tu knowledge base.
Voy a crear [N] notas en las carpetas:
IDENTITY, PREFERENCES, WORK, PROJECTS, PERSONAL-SPACE, KNOWLEDGE

¿Procedo? (sí / no)
```

---

## Inputs que necesitas leer

1. `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md` — fuente de todas las respuestas
2. `AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md` — tabla de mapeo pregunta → nota destino

---

## Frontmatter estándar para todas las notas

Toda nota creada por este skill debe comenzar con:

```yaml
---
title: "[Título descriptivo de la nota]"
type: "[identity | preference | work | project | personal | knowledge]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [categoria, subcategoria, tema]
status: "active"
context_for_claude: true
---
```

El campo `context_for_claude: true` es **obligatorio** en todas las notas de KB.

---

## Flujo de ejecución

### Paso 1 — Leer y parsear el cuestionario

Lee `BOOTSTRAP-QUESTIONNAIRE.md` completo. Extrae cada respuesta identificándola por su ID:
- `P.ID.1` a `P.ID.6`
- `P.PREF.1` a `P.PREF.6`
- `P.WORK.1` a `P.WORK.5`
- `P.PROJ.1` a `P.PROJ.4`
- `P.PERS.1` a `P.PERS.5`
- `P.KNOW.1` a `P.KNOW.5`

### Paso 2 — Leer el mapeo

Lee `BOOTSTRAP-MAPPING.md` para saber exactamente qué nota recibe el contenido de cada pregunta.

### Paso 3 — Agrupar respuestas por nota destino

Algunas notas reciben el contenido de múltiples preguntas. Construye internamente un mapa:

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

[proyectos activos]        ← P.PROJ.1 (uno por proyecto identificado)
[proyectos futuros]        ← P.PROJ.2 (uno por proyecto futuro)
[proyectos de orgullo]     ← P.PROJ.3 (uno por proyecto archivado)
INDEX-PROJECTS.md          ← P.PROJ.4 (visión a largo plazo)

personal-interests.md      ← P.PERS.1 + P.PERS.2 + P.PERS.4 + P.PERS.5
personal-hobbies.md        ← P.PERS.3

knowledge-current-learning.md ← P.KNOW.1
knowledge-interests.md        ← P.KNOW.2
knowledge-expertise.md        ← P.KNOW.3
knowledge-sources.md          ← P.KNOW.4
knowledge-insights.md         ← P.KNOW.5
```

### Paso 4 — Manejar notas de PROJECTS (caso especial)

`P.PROJ.1` puede mencionar múltiples proyectos activos. Para cada proyecto identificado, crea un archivo individual:
- Nombre del archivo: `project-[nombre-kebab-case].md`
- Ubicación: `PROJECTS/`
- Extrae del texto el nombre, estado y descripción de cada proyecto

Lo mismo aplica para proyectos futuros (`P.PROJ.2`) y proyectos de orgullo (`P.PROJ.3`).
`INDEX-PROJECTS.md` recibe únicamente el contenido de `P.PROJ.4`.

### Paso 5 — Crear cada nota

Para cada nota destino:

1. **Verifica si ya existe.** Si existe con contenido real, pregunta al usuario si desea sobrescribirla antes de proceder.
2. **Escribe el frontmatter** con el tipo y tags correctos para la categoría.
3. **Organiza el contenido** usando encabezados `###` para separar subtemas cuando una nota recibe múltiples respuestas.
4. **Agrega tags** siguiendo la convención `[categoría, subtipo, tema]`.
5. **Reporta progreso** al usuario conforme avanzas: `Creada: IDENTITY/identity-profile.md`

### Paso 6 — Agregar links internos

Al finalizar todas las notas, agrega links `[[nombre-de-nota]]` donde existan referencias naturales. Agrégalos al final de cada nota en una sección `## Relaciones`:

- `identity-values.md` → `[[identity-profile]]`
- `work-overview.md` → `[[work-team]]`, `[[work-current-role]]`
- `knowledge-expertise.md` → `[[work-current-role]]`
- `knowledge-interests.md` → `[[knowledge-expertise]]`
- Notas de PROJECTS → `[[INDEX-PROJECTS]]`

### Paso 7 — Reporte final

Al terminar, muestra un resumen:

```
Bootstrap completado.

Notas creadas: [N]
├── IDENTITY/          [N] notas
├── PREFERENCES/       [N] notas
├── WORK/              [N] notas
├── PROJECTS/          [N] notas
├── PERSONAL-SPACE/    [N] notas
└── KNOWLEDGE/         [N] notas

Próximo paso recomendado:
Abre el vault en Obsidian y revisa el Graph View
para verificar que las notas están conectadas correctamente.
```

Luego actualiza el frontmatter de `BOOTSTRAP-QUESTIONNAIRE.md` agregando:
- `kb_populated: true`
- `kb_populated_date: YYYY-MM-DD`

---

## Tags por categoría

| Nota | Tags |
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
| project-* (activo) | `[project, active, nombre-proyecto]` |
| project-* (futuro) | `[project, ideation, nombre-proyecto]` |
| project-* (orgullo) | `[project, archived, nombre-proyecto]` |
| INDEX-PROJECTS | `[project, index, vision]` |
| personal-interests | `[personal, interests, culture]` |
| personal-hobbies | `[personal, hobbies, creative]` |
| knowledge-current-learning | `[knowledge, learning, active]` |
| knowledge-interests | `[knowledge, interests, future]` |
| knowledge-expertise | `[knowledge, expertise, skills]` |
| knowledge-sources | `[knowledge, sources, learning]` |
| knowledge-insights | `[knowledge, insights, principles]` |

---

## Reglas

- No interrumpas el proceso para hacer preguntas intermedias, salvo la confirmación inicial y el caso de nota existente con contenido.
- Si una respuesta está vacía o es menor a 20 palabras, crea la nota igualmente con la advertencia: `> [Nota: Esta sección requiere más contenido. Actualiza la respuesta en BOOTSTRAP-QUESTIONNAIRE.md]`
- No modifiques `BOOTSTRAP-QUESTIONNAIRE.md` ni `BOOTSTRAP-MAPPING.md` durante la ejecución (solo el frontmatter al finalizar).
- No crees notas fuera de las carpetas definidas.
"""
        skill_file.write_text(content, encoding="utf-8")

    def _create_raw_ingest_skill(self) -> None:
        """Create the raw-ingest skill instruction file.

        Lives at AI-SYSTEM/SKILLS/raw-ingest.md. The agent reads this file
        when /raw-ingest is triggered and follows its instructions to process
        files from raw/ into valid KB notes.
        """
        skill_file = self.vault_path / "AI-SYSTEM" / "SKILLS" / "raw-ingest.md"
        if skill_file.exists():
            return

        today = datetime.now().strftime("%Y-%m-%d")
        content = f"""---
title: "SKILL — raw-ingest"
type: "skill"
created: {today}
modified: {today}
tags: [skill, ingestion, raw, agent]
status: "active"
context_for_claude: true
---

# SKILL: raw-ingest

**Propósito:** Procesar archivos depositados en `raw/` y convertirlos en notas válidas de la KB. Este skill se puede ejecutar múltiples veces a lo largo de la vida del vault: cada vez que el propietario quiera ingestar material nuevo.

**Ejecutor:** Agente Claude — no el usuario.
**Timebox:** 2 horas máximo por sesión de ingesta.

---

## Trigger Detection

Activa este skill cuando el usuario diga cualquiera de los siguientes:

- `/raw-ingest`
- "procesa los archivos en raw"
- "ingesta mi información personal"
- "convierte los archivos de raw en notas"
- "tengo archivos en raw para procesar"
- "hay archivos nuevos en raw"

---

## Pre-flight: Validación antes de ejecutar

**1. Verificar que existen archivos en `raw/`**
Lista los archivos en `raw/` (excluye `raw/processed/`, `raw/README.md` y `raw/.gitkeep`).

Si no hay archivos, responde:
```
No hay archivos en raw/ para procesar.
Para iniciar una ingesta, deposita archivos en raw/ y ejecuta /raw-ingest nuevamente.
Formatos soportados: .md, .txt, .pdf, .docx
```
Y detén la ejecución.

**2. Verificar acceso de escritura al vault**
Confirma que puedes crear y mover archivos. Si no, informa al usuario y detén.

---

## Paso 1 — Inventariar archivos disponibles

Lista todos los archivos en `raw/` con su nombre y extensión. Presenta al usuario:

```
Archivos encontrados en raw/:
- [nombre-archivo-1].[ext]
- [nombre-archivo-2].[ext]
...

¿Procedo a analizar todos? (sí / no / selecciona cuáles)
```

Espera confirmación antes de continuar.

---

## Paso 2 — Extraer bloques de información

Para cada archivo confirmado, lee su contenido y extrae bloques de información clasificándolos:

**Criterio de extracción — incluir si:**
- Actualiza o enriquece una nota ya existente en el vault
- Cubre un tema sin nota en el vault todavía
- Es información que el propietario usa frecuentemente con el agente (perfil, proyectos, stack, preferencias)

**Criterio de extracción — descartar si:**
- Es redundante con notas ya creadas en el bootstrap
- Es estado muy temporal ("esta semana tengo X") → va a `context-current.md` si aplica
- No aporta contexto útil para el agente

Para cada bloque extraído, registra internamente:
```
- Extracto/paráfrasis del bloque
- Categoría KB destino: IDENTITY | PREFERENCES | WORK | PROJECTS | PERSONAL-SPACE | KNOWLEDGE
- Nota destino: archivo donde irá (existente o nuevo)
- Operación: CREATE | APPEND | UPDATE
```

---

## Paso 3 — Presentar inventario al usuario (gate obligatorio)

Antes de escribir al vault, muestra el inventario completo de bloques extraídos:

```
Bloques identificados para ingestar:

[IDENTITY]
- identity-profile.md → APPEND: [descripción del bloque]
- identity-values.md  → CREATE: [descripción del bloque]

[WORK]
- work-current-role.md → UPDATE: [descripción del bloque]

[PROJECTS]
- project-nuevo.md → CREATE: [descripción del bloque]

...

Total: [N] operaciones sobre [M] notas.
¿Procedo? (sí / no / edita alguno)
```

**No escribas al vault sin aprobación explícita del usuario.**

---

## Paso 4 — Ejecutar operaciones aprobadas

Para cada operación aprobada:

### CREATE (nota nueva)

```yaml
---
title: "[Título descriptivo]"
type: "[identity | preference | work | project | personal | knowledge]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [categoria, subtipo, tema]
status: "active"
context_for_claude: true
source: "[nombre-del-archivo-fuente]"
ingested: YYYY-MM-DD
---
```

Organiza el contenido con encabezados `###` si la nota recibe múltiples bloques.
Agrega sección `## Relaciones` con links `[[nombre-de-nota]]` donde haya referencias naturales.

### APPEND (agregar a nota existente)

Agrega el nuevo contenido al final de la sección relevante de la nota.
Actualiza el campo `modified` en el frontmatter.
Agrega `source` e `ingested` como campos adicionales si no existen.

### UPDATE (reemplazar sección obsoleta)

Reemplaza la sección indicada con el contenido nuevo.
Actualiza `modified` en el frontmatter.
Preserva el resto de la nota intacto.

Reporta al usuario conforme avanzas:
```
✓ Creada: IDENTITY/identity-profile.md
✓ Actualizada: WORK/work-current-role.md
...
```

---

## Paso 5 — Mover archivos procesados

Al terminar de procesar cada archivo fuente, muévelo de `raw/` a `raw/processed/`.

```
raw/cv-nataly-2026.pdf  →  raw/processed/cv-nataly-2026.pdf
```

**No elimines los archivos.** Sirven como auditoría de qué información ingresó al vault y cuándo.

---

## Paso 6 — Registrar backlog (si aplica)

Si el timebox de 2h se agota antes de procesar todo, o si hay bloques que el usuario rechazó pero son válidos para el futuro, regístralos en `AI-SYSTEM/CONTEXT/ingestion-backlog.md`:

```markdown
---
title: "Backlog de Ingesta"
type: "system"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [system, ingestion, backlog]
status: "active"
---

## Pendientes de procesar

| Fuente | Bloque / Tema | Categoría destino | Prioridad |
| --- | --- | --- | --- |
| [nombre] | [descripción] | [CATEGORY] | Alta/Media/Baja |
```

Si el archivo ya existe, agrega los nuevos pendientes al final de la tabla.

---

## Paso 7 — Reporte de cierre

Al finalizar, muestra:

```
Ingesta completada.

Operaciones ejecutadas: [N]
├── Notas creadas:      [N]
├── Notas actualizadas: [N]
└── Notas sin cambios:  [N]

Archivos procesados: [N]
└── Movidos a raw/processed/

[Si hay backlog:]
Pendientes registrados en AI-SYSTEM/CONTEXT/ingestion-backlog.md: [N]
```

---

## Reglas

- El gate del Paso 3 es obligatorio. No escribas al vault sin aprobación del usuario.
- Detecta solapamiento antes de crear: si ya existe una nota sobre el mismo tema, prefiere APPEND o UPDATE sobre CREATE duplicado.
- Si un archivo en `raw/` no es procesable (formato incompatible, corrupto, sin contenido útil), infórmalo al usuario y continúa con el siguiente.
- No modifiques archivos en `raw/processed/` ni en `AI-SYSTEM/BOOTSTRAP/`.
- El campo `context_for_claude: true` es obligatorio en todas las notas creadas o actualizadas.
"""
        skill_file.write_text(content, encoding="utf-8")

    def _create_ingest_protocol(self) -> None:
        """Create AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md — canonical source-agnostic ingestion pipeline."""
        skills_dir = self.vault_path / "AI-SYSTEM" / "SKILLS"
        skills_dir.mkdir(parents=True, exist_ok=True)
        protocol_file = skills_dir / "INGEST-PROTOCOL.md"
        if protocol_file.exists():
            return

        content = """---
title: "INGEST-PROTOCOL — Pipeline Canónico de Ingesta"
type: "skill"
context_for_claude: true
tags: ["ingesta", "protocolo", "skill"]
status: "active"
---

# INGEST-PROTOCOL — Pipeline Canónico de Ingesta

Este archivo define el pipeline de 5 fases que el agente ejecuta para ingestar información de **cualquier fuente externa** al vault. Es fuente-agnóstico: los source adapters manejan la extracción; este protocolo toma el relevo desde los bloques ya extraídos.

---

## Contrato: IngestionBlock

Todo source adapter debe producir bloques con esta estructura antes de pasárselos al pipeline:

```
IngestionBlock {
  content:            texto o extracto del bloque
  source_id:          identificador de la fuente (path, URL, canal, etc.)
  source_type:        "file" | "directory" | "api" | "chat" | [lo que el adapter defina]
  suggested_category: IDENTITY | PREFERENCES | WORK | PROJECTS | PERSONAL-SPACE | KNOWLEDGE
  suggested_note:     nombre del archivo destino sugerido (sin extensión)
  operation:          CREATE | APPEND | UPDATE
}
```

Si el adapter no puede determinar `suggested_category` o `suggested_note`, puede dejarlos vacíos — el agente los infiere durante la Fase 2.

---

## Fase 1 — Extracción (responsabilidad del adapter)

El agente lee el source adapter correspondiente (`AI-SYSTEM/SKILLS/source-*.md`) y ejecuta sus instrucciones para producir una lista de `IngestionBlock`.

Si no existe adapter para la fuente solicitada, ofrece al usuario:
- Depositar el contenido en `raw/` y usar `source-files.md` como fallback
- Crear un adapter nuevo desde `TEMPLATES/template-source-adapter.md`

---

## Fase 2 — Clasificación

Para cada `IngestionBlock`:

1. Verifica que `suggested_category` sea una de las carpetas principales del vault. Si está vacío, inferirla del contenido.
2. Verifica que `suggested_note` sea un nombre de archivo válido (minúsculas, guiones, sin extensión). Si está vacío, inferirlo del contenido.
3. Si la categoría inferida es ambigua, usa KNOWLEDGE como fallback y documenta la ambigüedad.

---

## Fase 3 — Gate (aprobación obligatoria)

Antes de escribir al vault, presenta al usuario el inventario completo:

```
Bloques listos para ingestar:

| # | Contenido (resumen) | Destino | Operación |
|---|---------------------|---------|-----------|
| 1 | [resumen 10 palabras] | CATEGORY/nota.md | CREATE |
| 2 | ...                   | ...              | APPEND |

¿Apruebas estas operaciones? (S/n)
```

**No escribas al vault hasta recibir confirmación explícita.**
Si el usuario rechaza un bloque específico, omítelo y continúa con los demás.

---

## Fase 4 — Escritura

Para cada bloque aprobado:

**CREATE:** Crea el archivo con frontmatter mínimo:
```yaml
---
title: "[título inferido]"
type: "[tipo según categoría]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: []
status: "active"
context_for_claude: true
source: "[source_id del bloque]"
ingested: YYYY-MM-DD
---
```
Luego escribe `content` como cuerpo de la nota.

**APPEND:** Agrega `content` al final del archivo existente. Actualiza `modified` en frontmatter.

**UPDATE:** Reemplaza la sección relevante del archivo. Actualiza `modified` en frontmatter. Si no puedes identificar la sección exacta, usa APPEND y documenta la ambigüedad.

Reglas:
- Siempre verifica solapamiento antes de CREATE: si ya existe una nota sobre el mismo tema, escala a APPEND o UPDATE.
- `context_for_claude: true` es obligatorio en todas las notas creadas o actualizadas.
- `source` e `ingested` son obligatorios cuando el origen es un archivo fuente externo.

---

## Fase 5 — Post-ingesta

1. **Mover archivos fuente procesados** (si aplica): El adapter indica si los archivos fuente deben moverse. Para `raw/`, mover a `raw/processed/`.

2. **Registrar en backlog** los bloques que no pudieron procesarse (formato incompatible, ambigüedad no resuelta, rechazo del usuario). Archivo: `AI-SYSTEM/CONTEXT/ingestion-backlog.md`.

3. **Reporte de cierre:**
```
Ingesta completada desde [fuente].

Operaciones ejecutadas: [N]
├── Notas creadas:      [N]
├── Notas actualizadas: [N]
└── Notas sin cambios:  [N]

[Si hay backlog:]
Pendientes registrados en AI-SYSTEM/CONTEXT/ingestion-backlog.md: [N]
```

---

## Reglas generales

- El gate de Fase 3 es **obligatorio**. Sin aprobación del usuario, no hay escritura.
- En caso de duda sobre destino, prefiere KNOWLEDGE sobre cualquier otra categoría.
- Nunca modifiques archivos en `raw/processed/`, `AI-SYSTEM/BOOTSTRAP/`, ni este archivo.
- Si el adapter no produce bloques (fuente vacía o sin contenido útil), informa al usuario y termina sin error.
"""
        protocol_file.write_text(content, encoding="utf-8")

    def _create_source_adapter_template(self) -> None:
        """Create TEMPLATES/template-source-adapter.md — template for building new source adapters."""
        templates_dir = self.vault_path / "TEMPLATES"
        templates_dir.mkdir(parents=True, exist_ok=True)
        template_file = templates_dir / "template-source-adapter.md"
        if template_file.exists():
            return

        content = """---
title: "Plantilla: Source Adapter"
type: "template"
tags: ["template", "ingesta", "adapter"]
status: "active"
---

# Plantilla: Source Adapter

Copia este archivo a `AI-SYSTEM/SKILLS/source-[nombre].md` y completa las secciones marcadas con `[COMPLETAR]`.
Una vez completado, el agente lo usará automáticamente cuando el usuario pida ingestar desde esa fuente.

---

## Metadata del adapter

```yaml
source_id:    [COMPLETAR: identificador único, ej: "notion", "discord", "dropbox"]
source_type:  [COMPLETAR: "file" | "directory" | "api" | "chat" | otro]
description:  [COMPLETAR: una línea describiendo la fuente]
requires_mcp: [COMPLETAR: true si necesita un MCP/herramienta externa, false si el usuario exporta manualmente]
mcp_name:     [COMPLETAR si requires_mcp=true: nombre del MCP o herramienta]
```

---

## Cuándo activar este adapter

[COMPLETAR: lista de triggers de lenguaje natural que indican que el usuario quiere usar esta fuente]

Ejemplos:
- "ingesta mi información de [nombre fuente]"
- "explora [nombre fuente] y alimenta la KB"
- "[nombre fuente] tiene cosas que quiero en mi KB"

---

## Fase de extracción

Instrucciones para que el agente extraiga contenido de esta fuente y lo convierta en `IngestionBlock`.

### Pre-requisitos

[COMPLETAR: qué debe tener listo el usuario antes de que el agente pueda extraer]

Ejemplos:
- Archivo exportado depositado en `raw/`
- MCP de [nombre] conectado en Cowork
- Acceso autenticado a [URL/app]

### Pasos de extracción

[COMPLETAR: pasos concretos que el agente debe seguir]

1. [Paso 1 — cómo acceder al contenido]
2. [Paso 2 — cómo identificar qué es relevante para la KB]
3. [Paso 3 — cómo construir cada IngestionBlock]

### Criterios de relevancia

[COMPLETAR: qué contenido de esta fuente merece ingestarse y qué debe ignorarse]

### Mapeo a categorías del vault

[COMPLETAR: guía de cómo mapear el contenido de esta fuente a las categorías del vault]

| Tipo de contenido en [fuente] | Categoría del vault | Nota sugerida |
|-------------------------------|---------------------|---------------|
| [tipo 1]                      | [CATEGORY]          | [nota.md]     |
| [tipo 2]                      | [CATEGORY]          | [nota.md]     |

---

## Fase de post-extracción

[COMPLETAR: qué hacer con los archivos/datos fuente después de extraer los bloques]

Ejemplos:
- Mover archivo exportado a `raw/processed/`
- No se requiere acción (fuente externa permanece sin cambios)
- Marcar items en [fuente] como procesados

---

## Notas adicionales

[COMPLETAR: cualquier particularidad de esta fuente que el agente deba conocer]

---

*Adapter creado:* [FECHA]
*Basado en:* INGEST-PROTOCOL.md
"""
        template_file.write_text(content, encoding="utf-8")

    def _create_source_files_adapter(self) -> None:
        """Create AI-SYSTEM/SKILLS/source-files.md — reference adapter for raw/ and local directories."""
        skills_dir = self.vault_path / "AI-SYSTEM" / "SKILLS"
        skills_dir.mkdir(parents=True, exist_ok=True)
        adapter_file = skills_dir / "source-files.md"
        if adapter_file.exists():
            return

        content = """---
title: "Source Adapter: Archivos y Directorios Locales"
type: "skill"
context_for_claude: true
tags: ["ingesta", "adapter", "archivos", "raw"]
status: "active"
source_id: "files"
source_type: "file | directory"
requires_mcp: false
---

# Source Adapter: Archivos y Directorios Locales

Adapter de referencia para ingestar contenido desde archivos depositados en `raw/` o desde cualquier directorio local al que el agente tenga acceso. Es el **adapter de fallback universal**: úsalo cuando no exista un adapter específico para la fuente solicitada.

---

## Cuándo activar este adapter

- `/raw-ingest`
- "procesa los archivos en raw"
- "ingesta los archivos de raw"
- "tengo archivos en raw para procesar"
- "explora [directorio] y alimenta la KB"
- "lee [ruta de archivo] y agrégalo a mi KB"
- Cuando el usuario menciona un archivo local sin adapter específico

---

## Fase de extracción

### Pre-requisitos

Para archivos en `raw/`: el usuario debe haber depositado los archivos en el directorio `raw/` del vault.
Para directorios externos: el agente debe tener acceso de lectura a la ruta indicada.

### Pasos de extracción

**Caso A — Archivos en `raw/`:**

1. Lista todos los archivos en `raw/` (excluye `raw/processed/` y `.gitkeep`)
2. Para cada archivo, determina si es procesable:
   - Formatos soportados: `.md`, `.txt`, `.pdf`, `.docx`, cualquier texto plano
   - Si el formato no es procesable, informa al usuario y continúa con el siguiente
3. Lee el contenido de cada archivo
4. Divide el contenido en bloques temáticos (un bloque por tema identificable)
5. Para cada bloque, construye un `IngestionBlock`:
   - `source_id`: ruta relativa del archivo (`raw/nombre-archivo.ext`)
   - `source_type`: "file"
   - `suggested_category`: infiere de los temas identificados
   - `suggested_note`: infiere del contenido (nombre descriptivo en minúsculas con guiones)
   - `operation`: CREATE si no existe nota similar, APPEND o UPDATE si ya existe

**Caso B — Directorio local externo:**

1. Lista los archivos en el directorio indicado por el usuario
2. Pregunta al usuario si debe procesar subcarpetas recursivamente
3. Filtra por formatos procesables (igual que Caso A)
4. Sigue los pasos 3–5 del Caso A

### Criterios de relevancia

Incluye en la extracción:
- Información personal (identidad, valores, historia)
- Contexto profesional (proyectos, roles, empresas)
- Notas de aprendizaje (conceptos, recursos, síntesis)
- Preferencias y hábitos documentados

Ignora:
- Archivos de configuración técnica sin contenido personal
- Archivos temporales o caché
- Contenido duplicado ya presente en el vault

### Mapeo a categorías del vault

| Tipo de contenido | Categoría | Nota sugerida |
|-------------------|-----------|---------------|
| Información personal, bio, historia | IDENTITY | identity-profile.md o nueva nota |
| Valores, principios | IDENTITY | identity-values.md |
| Estilo de trabajo, herramientas | PREFERENCES | preferences-work-style.md o preferences-tools.md |
| Contexto laboral, empresa | WORK | work-company.md o work-current-role.md |
| Proyecto específico | PROJECTS | PROJECTS/[nombre-proyecto]/ |
| Hobbies, intereses personales | PERSONAL-SPACE | personal-hobbies.md o personal-interests.md |
| Aprendizaje, conceptos, recursos | KNOWLEDGE | nueva nota en KNOWLEDGE/ |

---

## Fase de post-extracción

Para archivos procesados desde `raw/`:
- Mover cada archivo procesado a `raw/processed/`
- No eliminar archivos en `raw/processed/`

Para archivos de directorios externos:
- No mover ni modificar los archivos fuente
- Solo registrar `source_id` con la ruta completa en el frontmatter de las notas creadas

---

## Notas adicionales

- Un archivo fuente puede producir múltiples bloques y por tanto múltiples notas
- Si un archivo es muy extenso (>1000 líneas), procésalo por secciones y confirma con el usuario antes de continuar
- Los archivos en `raw/` que el usuario marcó como "no procesar" (con prefijo `_`) deben ignorarse
- Este adapter es el fallback: si el usuario pide ingestar desde una fuente sin adapter, ofrece exportar el contenido a `raw/` para usarlo con este adapter
"""
        adapter_file.write_text(content, encoding="utf-8")

    def _create_readme_file(self) -> None:
        """Create README.md quick start guide in vault root."""
        readme_file = self.vault_path / "README.md"
        if readme_file.exists():
            return

        content = """# KB-PERSONAL: Guía de Inicio Rápido

Bienvenido a tu Knowledge Base Personal. Esta vault está diseñada para centralizar información personal y laboral de forma que sea consultable por agentes Claude.

---

## ¿Qué hay aquí?

**7 módulos principales + recursos de agente:**

| Carpeta | Propósito |
|---------|-----------|
| **IDENTITY/** | Quién eres (perfil, valores, voz, biografía) |
| **PREFERENCES/** | Gustos, herramientas, estilo de trabajo |
| **WORK/** | Contexto profesional (empresa, rol, equipo) |
| **PROJECTS/** | Proyectos activos y pasados |
| **PERSONAL-SPACE/** | Contenido personal (hobbies, intereses) |
| **KNOWLEDGE/** | Educación (cursos, investigaciones, aprendizaje) |
| **AI-SYSTEM/** | Recursos para agentes Claude (bootstrap, contexto, workflows) |

---

## Primeros Pasos (5 minutos)

### 1. Configura Obsidian
- Abre Obsidian
- Click: File → Open folder as vault
- Selecciona esta carpeta

### 2. Explora la estructura
- Panel izquierdo: File Explorer
- Abre cada carpeta (ej: IDENTITY/, WORK/)
- Nota los archivos INDEX-* (son hubs de cada módulo)

### 3. Lee el DESIGN
- Abre `DESIGN.md` en la raíz
- Define la especificación completa de esta vault
- Referencia para entender frontmatter, tags, estructura

---

## Próximo: Bootstrap (45-90 minutos)

La carpeta **AI-SYSTEM/BOOTSTRAP/** contiene herramientas para poblar tu vault desde el día uno.

### Flujo:

1. **Navega a:** `AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md`
   - Lee el hub de bootstrap
   - Entiende el flujo

2. **Responde:** `BOOTSTRAP-QUESTIONNAIRE.md`
   - 27 preguntas reflexivas en 6 categorías
   - 2-5 párrafos por pregunta
   - Tiempo estimado: 45-90 minutos

3. **Mapea:** `BOOTSTRAP-MAPPING.md`
   - Ve dónde va cada respuesta
   - Cada pregunta → nota destino

4. **Crea notas:**
   - Usa el template en `TEMPLATES/template-note.md`
   - Sigue el patrón de frontmatter
   - Respeta la estructura de carpetas

5. **Actualiza el grafo:**
   ```bash
   graphify /path/to/vault --update --no-cluster
   ```

---

## Estructura de Carpetas (Visual)

```
vault/
├── IDENTITY/
│   ├── INDEX-IDENTITY.md         ← Empieza aquí para conocerte
│   ├── identity-profile.md
│   ├── identity-values.md
│   ├── identity-voice.md
│   └── identity-bio.md
│
├── PREFERENCES/
│   ├── INDEX-PREFERENCES.md      ← Tus configuraciones personales
│   ├── preferences-tools.md
│   ├── preferences-work-style.md
│   └── preferences-lifestyle.md
│
├── WORK/
│   ├── INDEX-WORK.md             ← Tu contexto profesional
│   ├── work-overview.md
│   ├── work-current-role.md
│   ├── work-company.md
│   └── work-team.md
│
├── PROJECTS/
│   └── INDEX-PROJECTS.md         ← Tus proyectos (activos/pasados)
│
├── PERSONAL-SPACE/
│   ├── INDEX-PERSONAL-SPACE.md   ← Tu contenido personal
│   ├── personal-hobbies.md
│   └── personal-interests.md
│
├── KNOWLEDGE/
│   └── INDEX-KNOWLEDGE.md        ← Tu aprendizaje y educación
│
├── AI-SYSTEM/                    ← Recursos para agentes
│   ├── INDEX-AI-SYSTEM.md
│   ├── BOOTSTRAP/
│   │   ├── INDEX-BOOTSTRAP.md           ← EMPIEZA AQUÍ para bootstrap
│   │   ├── BOOTSTRAP-QUESTIONNAIRE.md   ← 27 preguntas
│   │   └── BOOTSTRAP-MAPPING.md         ← Mapeo P→nota
│   ├── AGENTS/
│   ├── CONTEXT/
│   ├── SESSIONS/
│   ├── SKILLS/
│   │   ├── bootstrap-generate.md        ← Skill: /bootstrap-generate
│   │   └── raw-ingest.md                ← Skill: /raw-ingest
│   └── WORKFLOWS/
│
├── TEMPLATES/
│   └── template-note.md          ← Plantilla para nuevas notas
│
├── raw/                          ← Staging de archivos sin procesar
│   ├── processed/                ← Archivos ya procesados (auditoría)
│   └── README.md                 ← Reglas del directorio
│
├── DESIGN.md                     ← Especificación completa
├── README.md                     ← Este archivo
│
└── graphify-out/                 ← Grafo generado (consulta por agente)
    ├── graph.json
    ├── GRAPH_REPORT.md
    └── graph.html
```

---

## Frontmatter: La Base de Todo

Cada nota `.md` necesita frontmatter YAML:

```yaml
---
title: "Tu Nota"
type: "identity | preference | work | project | knowledge | personal"
created: 2026-05-22
modified: 2026-05-22
tags: [tag1, tag2]
status: "active"
context_for_claude: true
---
```

**Campo clave:** `context_for_claude: true` → El agente la consulta

---

## Grafo de Conocimiento

Después de poplar notas con bootstrap, ejecuta:

```bash
graphify /path/to/vault --update --no-cluster
```

Esto genera:
- `graph.json` — Queryable por agentes
- `graph.html` — Abre en navegador para visualizar
- `GRAPH_REPORT.md` — Análisis de relaciones

---

## Checklist: Primera Sesión

- [ ] Obsidian configurado (File → Open folder as vault)
- [ ] Leí DESIGN.md (5 minutos)
- [ ] Exploré estructura en File Explorer
- [ ] Abrí AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md
- [ ] Empecé a responder BOOTSTRAP-QUESTIONNAIRE.md

---

## Recursos

- **DESIGN.md** — Especificación técnica completa
- **AI-SYSTEM/BOOTSTRAP/INDEX-BOOTSTRAP.md** — Hub de bootstrap
- **AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md** — Las 27 preguntas
- **AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-MAPPING.md** — Guía de mapeo
- **TEMPLATES/template-note.md** — Plantilla estándar

---

**Creado:** {created}
**Última actualización:** {created}
**Versión:** 1.0.0
""".format(created=datetime.now().strftime("%Y-%m-%d"))

        readme_file.write_text(content, encoding="utf-8")
