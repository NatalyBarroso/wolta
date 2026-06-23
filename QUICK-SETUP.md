# Wolta CLI - Quick Start

**First time?** Read this first (2 minutes).

---

## What is Wolta?

A CLI tool that creates an Obsidian vault with a predefined structure for your personal knowledge base. A single run generates:
- 16 folders (7 categories + AI-SYSTEM)
- 24 markdown files with frontmatter
- 27 bootstrap questions to complete your KB
- A structure ready for Claude agents

---

## Installation (choose one)

### Option 1: pip
```bash
pip install -e .
wolta init --name my-vault
```

### Option 2: uv (faster)
```bash
uv pip install -e .
wolta init --name my-vault
```

### Option 3: Plain Python (no install)
```bash
python main.py init --name my-vault
```

---

## Usage Examples

### Default vault
```bash
python main.py init
# Creates: wolta/
```

### With a custom name
```bash
python main.py init --name joanna
# Creates: wolta-joanna/
```

### At a specific path
```bash
python main.py init --vault-path ~/Documents --name personal-kb
# Creates: ~/Documents/wolta-personal-kb/
```

### Re-initialize an existing one
```bash
python main.py init --name joanna --force
```

---

## What gets generated

```
wolta-[name]/
├── IDENTITY/              (Who you are)
├── PREFERENCES/           (How you like to work)
├── WORK/                  (Your professional life)
├── PROJECTS/              (Current projects)
├── PERSONAL-SPACE/        (Hobbies and interests)
├── KNOWLEDGE/             (Learning areas)
├── AI-SYSTEM/
│   ├── BOOTSTRAP/         (27 questions)
│   ├── CONTEXT/
│   ├── AGENTS/
│   ├── SESSIONS/
│   ├── SKILLS/
│   └── WORKFLOWS/
├── TEMPLATES/             (Templates)
└── .wolta/                (Metadata)
```

**Total:** 24 markdown files ready

---

## The 27 Bootstrap Questions

They are generated automatically in:
```
AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
```

Organized into 6 categories:
- IDENTITY (6) - Who you are, values, communication
- PREFERENCES (6) - Ideal day, tools
- WORK (5) - Role, company, career
- PROJECTS (4) - What you do, future plans
- PERSONAL-SPACE (5) - Entertainment, leisure
- KNOWLEDGE (5) - Learning, specialties

---

## Next Steps After Creating

1. **Open in Obsidian**
   ```
   File → Open folder as vault → [your wolta-* folder]
   ```

2. **Complete the Bootstrap Questions**
   ```
   Edit: AI-SYSTEM/BOOTSTRAP/bootstrap-questions.md
   Answer: All 27 questions
   ```

3. **Fill in the Categories**
   ```
   Complete the information in each folder
   (IDENTITY, PREFERENCES, WORK, etc.)
   ```

4. **Use with Claude**
   ```
   Your KB will be ready for queries with Claude agents
   ```

---

## Automatic Validations

✅ Name: Only alphanumerics and hyphens  
✅ Length: Maximum 50 characters  
✅ Path: Must exist  
✅ Permissions: Write access is checked  
✅ Idempotency: Does not overwrite without --force  

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `pyproject.toml` | pip/uv configuration |
| `README.md` | Full documentation |
| `PROYECTO-COMPLETADO.md` | Technical details |

---

## Documentation

- **README.md** - Full documentation
- **PROYECTO-COMPLETADO.md** - Technical details and architecture
- **QUICK-SETUP.md** - This file

---

## Trouble?

### "Command not found: wolta"
→ Use: `python main.py init` instead of `wolta init`

### "Permission denied"
→ Use: `--vault-path` in a directory where you have permissions

### "Vault already initialized"
→ Use: `--force` to re-initialize

---

## Quick Support

Help command:
```bash
python main.py init --help
```

Version:
```bash
python main.py --version
```

---

**Done! Now run:**
```bash
python main.py init --name your-name
```

Your vault will be created in seconds. 🚀
