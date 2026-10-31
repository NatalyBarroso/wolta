# Changelog

## 0.2.0 — 2026-08-30

The vault is split at the root by **ownership**. `HUMAN/` is the user's space and is born empty. `SYSTEM/` is the knowledge base and the agent's tooling. `.wolta/`, `CLAUDE.md`, and `README.md` stay at the root.

A 0.1.0 vault is upgraded in place: each category is renamed into `SYSTEM/`, checksums are re-keyed, and the generated docs are refreshed. User notes are not copied and their sha256 does not change.

```
wolta upgrade --vault-path /path/to/vault
wolta upgrade --vault-path /path/to/vault --dry-run
```

### After you upgrade — three things the CLI does not do

1. **Obsidian paths.** Review Settings for the templates folder, the attachments folder, and daily notes. `.obsidian/` is yours; the upgrade leaves it alone, so saved searches and starred notes may still point at the old root.
2. **graphify-out/.** `graph.json` still has the pre-move paths. Regenerate:
   ```bash
   graphify /path/to/vault --update --no-cluster
   ```
3. **Your working folder.** If you want drafts and exports inside the vault, move that folder into `HUMAN/` yourself. `wolta init` does not adopt an external folder.

The write boundary is a policy in `CLAUDE.md`, not a filesystem lock. `HUMAN/` is an ingestion source, not automatic KB context.

### If you need to go back (before `HUMAN/` has your files)

There is no automatic downgrade. Until you put your own files in `HUMAN/`, the tree is reversible:

1. Move `SYSTEM/IDENTITY`, `PREFERENCES`, `WORK`, `PROJECTS`, `PERSONAL-SPACE`, `KNOWLEDGE`, `AI-SYSTEM`, `TEMPLATES`, and `raw` back to the vault root.
2. Move `SYSTEM/DESIGN.md` back to `DESIGN.md`.
3. Remove the empty `SYSTEM/` and `HUMAN/` (keep them if you already added files).
4. Set `.wolta/version` `schema_version` to `0.1.0`.

The upgrade also left a snapshot in `.wolta/backups/<timestamp>/` with the documents it rewrote. Once `HUMAN/` has your own content, reverting is no longer a clean rename.

### What did not change

- Note content, timestamps, and wikilinks between notes.
- User-owned skills and templates.
- The CLI version was already `0.2.0` so the runner can select this hop.
