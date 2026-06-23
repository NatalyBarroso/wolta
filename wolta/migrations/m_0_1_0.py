"""Migration v0.0.x -> v0.1.0 (T2.3.4).

Brings a pre-versioning vault up to schema 0.1.0: adds the extensible-ingest
files if missing and refreshes the CLAUDE.md managed section while preserving
anything outside the markers.

Self-contained and immutable (D-02): the 0.1.0 content is frozen under
`data_v0_1_0/` and does NOT depend on the current `structure.py`. A migration
is a historical artifact; its result must never change as the tool evolves.
"""

from pathlib import Path
from typing import List

from wolta.migrations.base import Migration, MigrationContext

_DATA = Path(__file__).parent / "data_v0_1_0"

# Frozen 0.1.0 artifacts -> vault-relative destination.
_NEW_FILES = {
    "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md": "INGEST-PROTOCOL.md",
    "AI-SYSTEM/SKILLS/source-files.md": "source-files.md",
    "TEMPLATES/template-source-adapter.md": "template-source-adapter.md",
}

_CLAUDE_REL = "CLAUDE.md"
_CLAUDE_BLOCK_ID = "agent-instructions"
_CLAUDE_VERSION = "0.1.0"


def _data(name: str) -> str:
    return (_DATA / name).read_text(encoding="utf-8")


class MigrationV010(Migration):
    target_version = "0.1.0"
    min_version = "0.0.0"

    def up(self, ctx: MigrationContext) -> List[str]:
        changed: List[str] = []
        # 1) Add the three ingest-architecture files if missing (idempotent).
        for rel, data_name in _NEW_FILES.items():
            if not (ctx.vault / rel).exists():
                ctx.files.write_managed(
                    ctx.vault, rel, _data(data_name), dry_run=ctx.dry_run
                )
                changed.append(rel)
        # 2) Refresh the CLAUDE.md managed section.
        changed += self._update_claude_md(ctx)
        return changed

    def _update_claude_md(self, ctx: MigrationContext) -> List[str]:
        path = ctx.vault / _CLAUDE_REL
        body = _data("claude-agent-instructions.md")

        if not path.exists():
            new = (
                "# WOLTA — Project Instructions for the Claude Agent\n\n"
                f'<!-- wolta:managed:start id="{_CLAUDE_BLOCK_ID}" v="{_CLAUDE_VERSION}" -->\n'
                f"{body}\n"
                f'<!-- wolta:managed:end id="{_CLAUDE_BLOCK_ID}" -->\n\n'
                "## User notes\n"
            )
            ctx.files.write_managed(ctx.vault, _CLAUDE_REL, new, dry_run=ctx.dry_run)
            return [_CLAUDE_REL]

        current = path.read_text(encoding="utf-8")
        # replace_block updates the block in place if the markers exist,
        # or appends a new managed block at EOF if they don't (legacy file).
        # Either way, content outside the markers is preserved.
        updated = ctx.sections.replace_block(
            current, _CLAUDE_BLOCK_ID, body, version=_CLAUDE_VERSION
        )
        if updated != current:
            ctx.files.write_managed(ctx.vault, _CLAUDE_REL, updated, dry_run=ctx.dry_run)
            return [_CLAUDE_REL]
        return []
