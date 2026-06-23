---
wolta_version: "0.1.0"
title: "Template: Source Adapter"
type: "template"
tags: ["template", "ingestion", "adapter"]
status: "active"
---

# Template: Source Adapter

Copy this file to `AI-SYSTEM/SKILLS/source-[name].md` and complete the sections marked with `[FILL IN]`.
Once completed, the agent will use it automatically when the user asks to ingest from that source.

---

## Adapter metadata

```yaml
source_id:    [FILL IN: unique identifier, e.g. "notion", "discord", "dropbox"]
source_type:  [FILL IN: "file" | "directory" | "api" | "chat" | other]
description:  [FILL IN: one line describing the source]
requires_mcp: [FILL IN: true if it needs an external MCP/tool, false if the user exports manually]
mcp_name:     [FILL IN if requires_mcp=true: name of the MCP or tool]
```

---

## When to activate this adapter

[FILL IN: list of natural-language triggers that indicate the user wants to use this source]

Examples:
- "ingest my information from [source name]"
- "explore [source name] and feed the KB"
- "[source name] has things I want in my KB"

---

## Extraction phase

Instructions for the agent to extract content from this source and turn it into `IngestionBlock`s.

### Pre-requisites

[FILL IN: what the user must have ready before the agent can extract]

Examples:
- Exported file dropped in `raw/`
- [name] MCP connected in Cowork
- Authenticated access to [URL/app]

### Extraction steps

[FILL IN: concrete steps the agent must follow]

1. [Step 1 — how to access the content]
2. [Step 2 — how to identify what is relevant for the KB]
3. [Step 3 — how to build each IngestionBlock]

### Relevance criteria

[FILL IN: what content from this source is worth ingesting and what should be ignored]

### Mapping to vault categories

[FILL IN: guide on how to map this source's content to the vault categories]

| Content type in [source] | Vault category | Suggested note |
|--------------------------|----------------|----------------|
| [type 1]                 | [CATEGORY]     | [note.md]      |
| [type 2]                 | [CATEGORY]     | [note.md]      |

---

## Post-extraction phase

[FILL IN: what to do with the source files/data after extracting the blocks]

Examples:
- Move the exported file to `raw/processed/`
- No action required (external source remains unchanged)
- Mark items in [source] as processed

---

## Additional notes

[FILL IN: any particularity of this source the agent should know]

---

*Adapter created:* [DATE]
*Based on:* INGEST-PROTOCOL.md
