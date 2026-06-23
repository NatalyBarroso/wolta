"""Tests for the v0.0.x -> v0.1.0 migration (T2.3.4)."""

import json

from click.testing import CliRunner

import wolta.commands.upgrade as upgrade_mod
from wolta.core import files as core_files
from wolta.core import manifest as core_manifest
from wolta.core import sections as core_sections
from wolta.migrations.base import MigrationContext
from wolta.migrations.m_0_1_0 import MigrationV010

INGEST = "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"
SOURCE_FILES = "AI-SYSTEM/SKILLS/source-files.md"
TEMPLATE_ADAPTER = "TEMPLATES/template-source-adapter.md"
NEW_FILES = [INGEST, SOURCE_FILES, TEMPLATE_ADAPTER]


def _ctx(vault, dry_run=False):
    (vault / ".wolta").mkdir(exist_ok=True)
    return MigrationContext(
        vault=vault,
        manifest=core_manifest,
        sections=core_sections,
        files=core_files,
        dry_run=dry_run,
    )


def test_adds_three_files_with_version():
    import tempfile
    from pathlib import Path

    vault = Path(tempfile.mkdtemp())
    changed = MigrationV010().up(_ctx(vault))

    for rel in NEW_FILES:
        assert (vault / rel).exists()
        assert 'wolta_version: "0.1.0"' in (vault / rel).read_text(encoding="utf-8")
    assert set(NEW_FILES).issubset(set(changed))


def test_idempotent_second_run(tmp_path):
    MigrationV010().up(_ctx(tmp_path))
    changed = MigrationV010().up(_ctx(tmp_path))
    assert changed == []  # nothing left to do


def test_claude_with_markers_preserves_user_content(tmp_path):
    claude = (
        "# WOLTA\n\n"
        '<!-- wolta:managed:start id="agent-instructions" v="0.0.9" -->\n'
        "OLD managed body\n"
        '<!-- wolta:managed:end id="agent-instructions" -->\n\n'
        "## Notas del usuario\n\nMI NOTA PERSONAL\n"
    )
    (tmp_path / "CLAUDE.md").write_text(claude, encoding="utf-8")

    MigrationV010().up(_ctx(tmp_path))

    out = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "MI NOTA PERSONAL" in out          # user content preserved
    assert "OLD managed body" not in out       # managed block replaced
    assert "personal knowledge base" in out    # new 0.1.0 body present
    assert out.count('wolta:managed:start id="agent-instructions"') == 1


def test_claude_legacy_without_markers_appends_block(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Old\n\nlegacy instructions\n", encoding="utf-8")

    MigrationV010().up(_ctx(tmp_path))

    out = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "legacy instructions" in out                      # not destroyed
    assert 'wolta:managed:start id="agent-instructions"' in out  # block added


def test_dry_run_writes_nothing(tmp_path):
    MigrationV010().up(_ctx(tmp_path, dry_run=True))
    for rel in NEW_FILES:
        assert not (tmp_path / rel).exists()


def test_end_to_end_upgrade_from_legacy(tmp_path):
    # pre-versioning vault (no .wolta/version) -> 0.0.0
    (tmp_path / ".wolta").mkdir()
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(tmp_path)])

    assert result.exit_code == 0
    data = json.loads((tmp_path / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"
    assert [m["target"] for m in data["applied_migrations"]] == ["0.1.0"]
