"""Integration tests for `wolta upgrade` (T2.3.3)."""

import json

from click.testing import CliRunner

import wolta.commands.upgrade as upgrade_mod
from wolta import __version__
from wolta.generators.structure import StructureGenerator
from wolta.migrations.base import Migration


def _make_vault(tmp_path):
    StructureGenerator(str(tmp_path)).generate()
    return tmp_path


class _ApplyMig(Migration):
    target_version = "0.2.0"
    REL = "AI-SYSTEM/SKILLS/new-skill.md"

    def up(self, ctx):
        ctx.files.write_managed(ctx.vault, self.REL, "new content", dry_run=ctx.dry_run)
        return [self.REL]


class _FailMig(Migration):
    target_version = "0.2.0"
    REL = "AI-SYSTEM/SKILLS/half.md"

    def up(self, ctx):
        if not ctx.dry_run:
            ctx.files.write_managed(ctx.vault, self.REL, "half-written", dry_run=False)
            raise RuntimeError("boom")
        return [self.REL]


def test_upgrade_up_to_date_is_noop(tmp_path):
    vault = _make_vault(tmp_path)
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])
    assert result.exit_code == 0
    assert "already up to date" in result.output
    assert not (vault / ".wolta" / "backups").exists()


def test_legacy_vault_without_version_migrates_to_010(tmp_path):
    (tmp_path / ".wolta").mkdir()
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE\n\nold instructions\n", encoding="utf-8")
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(tmp_path)])
    assert result.exit_code == 0
    assert "UPGRADE APPLIED" in result.output
    data = json.loads((tmp_path / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"
    assert (tmp_path / "AI-SYSTEM" / "SKILLS" / "INGEST-PROTOCOL.md").exists()
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "old instructions" in claude
    assert 'wolta:managed:start id="agent-instructions"' in claude


def test_dry_run_does_not_modify(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_ApplyMig()])
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault), "--dry-run"])
    assert result.exit_code == 0
    assert "DRY-RUN" in result.output
    assert not (vault / _ApplyMig.REL).exists()
    assert not (vault / ".wolta" / "backups").exists()
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == __version__
    assert data["applied_migrations"] == []


def test_apply_migration_updates_vault(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_ApplyMig()])
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])
    assert result.exit_code == 0
    assert "UPGRADE APPLIED" in result.output
    assert (vault / _ApplyMig.REL).read_text(encoding="utf-8") == "new content"
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.2.0"
    assert [m["target"] for m in data["applied_migrations"]] == ["0.2.0"]


def test_failed_migration_rolls_back(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_FailMig()])
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])
    assert result.exit_code == 1
    assert "rollback" in result.output.lower()
    assert not (vault / _FailMig.REL).exists()
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == __version__
    assert data["applied_migrations"] == []


def test_to_version_above_cli_is_rejected(tmp_path):
    vault = _make_vault(tmp_path)
    result = CliRunner().invoke(upgrade_mod.upgrade_command,
                                ["--vault-path", str(vault), "--to-version", "9.9.9"])
    assert result.exit_code == 1
    assert "greater than the CLI version" in result.output


def test_corrupt_markers_abort_in_preflight(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    (vault / "CLAUDE.md").write_text(
        '# X\n<!-- wolta:managed:start id="agent-instructions" -->\nbody\n', encoding="utf-8")
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_ApplyMig()])
    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])
    assert result.exit_code == 1
    assert "markers" in result.output.lower()
    assert not (vault / ".wolta" / "backups").exists()
    assert not (vault / _ApplyMig.REL).exists()
