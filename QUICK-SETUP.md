# Wolta CLI - Inicio Rápido

**¿Primera vez?** Lee esto primero (2 minutos).

---

## ¿Qué es Wolta?

Herramienta CLI que crea un vault Obsidian con estructura predefinida para tu knowledge base personal. Una ejecución genera:
- 16 carpetas (7 categorías + AI-SYSTEM)
- 24 archivos markdown con frontmatter
- 27 preguntas bootstrap para completar tu KB
- Estructura lista para agentes Claude

---

## Instalación (elige una)

### Opción 1: pip
```bash
pip install -e .
wolta init --name mi-vault
```

### Opción 2: uv (más rápido)
```bash
uv pip install -e .
wolta init --name mi-vault
```

### Opción 3: Python directo (sin instalar)
```bash
python main.py init --name mi-vault
```

---

## Ejemplos de Uso

### Vault default
```bash
python main.py init
# Crea: wolta/
```

### Con nombre personalizado
```bash
python main.py init --name joanna
# Crea: wolta-joanna/
```

### En una ruta específica
```bash
python main.py init --vault-path ~/Documents --name personal-kb
# Crea: ~/Documents/wolta-personal-kb/
```

### Re-inicializar existente
```bash
python main.py init --name joanna --force
```

---

## Qué se genera

```
wolta-[name]/
├── IDENTITY/              (Quién eres)
├── PREFERENCES/           (Cómo te gusta trabajar)
├── WORK/                  (Tu vida profesional)
├── PROJECTS/              (Proyectos actuales)
├── PERSONAL-SPACE/        (Hobbies e intereses)
├── KNOWLEDGE/             (Áreas de aprendizaje)
├── AI-SYSTEM/
│   ├── BOOTSTRAP/         (27 preguntas)
│   ├── CONTEXT/
│   ├── AGENTS/
│   ├── SESSIONS/
│   ├── SKILLS/
│   └── WORKFLOWS/
├── TEMPLATES/             (Plantillas)
└── .wolta/                (Metadata)
```

**Total:** 24 archivos markdown listos

---

## Las 27 Preguntas Bootstrap

Se generan automáticamente en:
```
AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

Organizadas en 6 categorías:
- IDENTITY (6) - Quién eres, valores, comunicación
- PREFERENCES (6) - Día ideal, herramientas
- WORK (5) - Rol, empresa, carrera
- PROJECTS (4) - Qué haces, planes futuros
- PERSONAL-SPACE (5) - Entretenimiento, ocio
- KNOWLEDGE (5) - Aprendizaje, especialidades

---

## Próximos Pasos Después de Crear

1. **Abrir en Obsidian**
   ```
   File → Open folder as vault → [tu carpeta wolta-*]
   ```

2. **Completar Preguntas Bootstrap**
   ```
   Edita: AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
   Responde: Las 27 preguntas
   ```

3. **Llenar Categorías**
   ```
   Completa información en cada carpeta
   (IDENTITY, PREFERENCES, WORK, etc.)
   ```

4. **Usar con Claude**
   ```
   Tu KB estará lista para consultas con agentes Claude
   ```

---

## Validaciones Automáticas

✅ Nombre: Solo alfanuméricos y guiones  
✅ Longitud: Máximo 50 caracteres  
✅ Ruta: Debe existir  
✅ Permisos: Se verifica escritura  
✅ Idempotencia: No sobrescribe sin --force  

---

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Entry point |
| `pyproject.toml` | Configuración pip/uv |
| `README.md` | Documentación completa |
| `PROYECTO-COMPLETADO.md` | Detalles técnicos |

---

## Documentación

- **README.md** - Documentación completa
- **PROYECTO-COMPLETADO.md** - Detalles técnicos y arquitectura
- **INICIO-RAPIDO.md** - Este archivo

---

## ¿Problemas?

### "Command not found: wolta"
→ Usa: `python main.py init` en lugar de `wolta init`

### "Permission denied"
→ Usa: `--vault-path` en un directorio donde tengas permisos

### "Vault already initialized"
→ Usa: `--force` para re-inicializar

---

## Soporte Rápido

Comando de ayuda:
```bash
python main.py init --help
```

Versión:
```bash
python main.py --version
```

---

**¡Listo! Ahora ejecuta:**
```bash
python main.py init --name tu-nombre
```

Tu vault se creará en segundos. 🚀
