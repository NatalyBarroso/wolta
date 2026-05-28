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

        # Create reference documents
        self._create_design_file()
        self._create_readme_file()

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
│   └── WORKFLOWS/
│
├── TEMPLATES/
│   └── template-note.md          ← Plantilla para nuevas notas
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
