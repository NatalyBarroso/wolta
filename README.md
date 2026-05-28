# Wolta CLI - Inicializador de Knowledge Base Personal

Herramienta de línea de comandos para inicializar y gestionar una knowledge base personal en Obsidian, integrada con agentes Claude para consultas inteligentes.

## Descripción

Wolta crea un vault estructurado en Obsidian con categorías predefinidas y preguntas bootstrap para completar tu knowledge base desde el primer día. El vault está diseñado para ser consultado por agentes Claude con comprensión contextual completa.

**Estructura del Vault:**
- **IDENTITY** - Perfil personal, valores, voz
- **PREFERENCES** - Herramientas, estilo de trabajo, lifestyle
- **WORK** - Rol actual, empresa, información del equipo
- **PROJECTS** - Proyectos activos y estado
- **PERSONAL-SPACE** - Hobbies e intereses
- **KNOWLEDGE** - Recursos de aprendizaje
- **AI-SYSTEM** - Contexto de agentes, workflows, skills
  - **BOOTSTRAP** - Preguntas iniciales para completar
  - **CONTEXT** - Contexto actual
  - **AGENTS** - Configuración de agentes
  - **SESSIONS** - Historial de sesiones
  - **SKILLS** - Habilidades personalizadas
  - **WORKFLOWS** - Flujos de trabajo

## Instalación

### Opción 1: Con pip (clásico)

```bash
pip install -e .
```

Luego usa el comando global:
```bash
wolta init
```

### Opción 2: Con uv (recomendado - más rápido)

```bash
uv pip install -e .
```

Luego usa el comando global:
```bash
wolta init
```

### Opción 3: Ejecución directa con Python

```bash
python main.py init
```

O con uv:
```bash
uv run main.py init
```

## Uso

### Inicialización básica

Inicializar un vault en el directorio actual:
```bash
wolta init
```

Crea una carpeta `wolta/` con la estructura por defecto.

### Nombre personalizado para el vault

Personaliza el nombre de la carpeta del vault:
```bash
wolta init --name joanna
```

Crea: `wolta-joanna/` en lugar de `wolta/`

### Ruta personalizada

Especifica dónde se debe crear el vault:
```bash
wolta init --vault-path ~/Documents
```

### Opciones combinadas

```bash
wolta init --vault-path ~/Documents --name my-kb
```

Crea: `~/Documents/wolta-my-kb/`

### Forzar re-inicialización

Re-inicializa un vault existente (sobrescribe):
```bash
wolta init --name joanna --force
```

## Opciones del Comando

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `--vault-path` | Path | Directorio actual | Directorio donde se creará el vault |
| `--name` | String | `wolta` | Nombre personalizado para la carpeta (crea `wolta-[name]/`) |
| `--force` | Flag | False | Fuerza la re-inicialización de un vault existente |
| `--help` | Flag | - | Muestra el mensaje de ayuda |
| `--version` | Flag | - | Muestra el número de versión |

## Validación de Nombres

Los nombres de vault deben cumplir estas reglas:
- Solo caracteres alfanuméricos y guiones
- 1-50 caracteres de largo
- No pueden empezar ni terminar con guión

**Ejemplos válidos:**
- `my-kb`
- `joanna123`
- `kb-2026`

**Ejemplos inválidos:**
- `-invalid` (comienza con guión)
- `invalid-` (termina con guión)
- `invalid name` (contiene espacios)

## Salida

Después de una inicialización exitosa:

```
✓ Vault initialized successfully!
  Vault location: ~/Documents/wolta-joanna
  Vault name: wolta-joanna

Next steps:
  1. Open the vault in Obsidian: File → Open folder as vault
  2. Navigate to: ~/Documents/wolta-joanna
  3. Complete the bootstrap questions in AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

## Estructura Generada

### Carpetas (8 principales + subcarpetas)
```
wolta-[name]/
├── IDENTITY/
├── PREFERENCES/
├── WORK/
├── PROJECTS/
├── PERSONAL-SPACE/
├── KNOWLEDGE/
├── AI-SYSTEM/
│   ├── AGENTS/
│   ├── BOOTSTRAP/
│   ├── CONTEXT/
│   ├── SESSIONS/
│   ├── SKILLS/
│   └── WORKFLOWS/
├── TEMPLATES/
└── .wolta/
```

### Archivos Creados
- Archivos INDEX para cada categoría (ej: `INDEX-IDENTITY.md`)
- Archivos específicos de categoría con frontmatter YAML
- Archivo de preguntas bootstrap: `AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md`
- Archivo de plantilla: `TEMPLATES/template-note.md`
- Marcador de configuración: `.wolta/initialized`

## Preguntas Bootstrap

Después de la inicialización, completa las preguntas bootstrap en:
```
AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

O pide al agente que comience con la generación de las plantillas de nota.
```
"Comienza con el bootstrap"
```

Estas preguntas abarcan 27 temas en 6 categorías:

- **IDENTITY** (6 preguntas) - Quién eres, valores, comunicación
- **PREFERENCES** (6 preguntas) - Tu forma de trabajar, herramientas, lifestyle
- **WORK** (5 preguntas) - Rol, empresa, equipo, carrera
- **PROJECTS** (4 preguntas) - Proyectos actuales y futuros
- **PERSONAL-SPACE** (5 preguntas) - Entretenimiento, música, aprendizaje
- **KNOWLEDGE** (5 preguntas) - Áreas de especialidad y aprendizaje

## Especificación de Frontmatter

Todos los archivos generados incluyen frontmatter YAML:

```yaml
---
title: "[File Title]"
type: "identity | preference | work | project | knowledge | personal"
created: 2026-05-19
modified: 2026-05-19
tags: []
status: "active"
---
```

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Estilo de código

Formatear con Black:
```bash
black .
```

Linter con Ruff:
```bash
ruff check .
```

## Arquitectura

- `main.py` - Punto de entrada para `python main.py` y `uv run main.py`
- `wolta/cli.py` - Grupo CLI de Click y registro de comandos
- `wolta/commands/init.py` - Implementación del comando init
- `wolta/generators/structure.py` - Generador de estructura de carpetas
- `wolta/generators/bootstrap.py` - Generador de preguntas bootstrap
- `wolta/utils/validators.py` - Utilidades de validación

## Próximos Pasos

Después de inicializar tu vault:

1. **Abrir en Obsidian** - File → Open folder as vault
2. **Configurar Obsidian** - Settings → Configura nombre del vault, templates, attachments
3. **Responder Preguntas Bootstrap** - Completa `AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md`
4. **Poblar Categorías** - Completa tu información en todas las categorías
5. **Generar Grafo de Conocimiento** - Usa Graphify CLI para representación queryable

## Licencia

Proyecto personal para gestión de knowledge base.

## Autor

Nataly Barroso (barrosonataly.dev@gmail.com)
