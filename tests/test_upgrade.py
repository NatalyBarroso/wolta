"""Integration tests for `wolta upgrade` (T2.3.3).

Uses the click CliRunner and synthetic migrations (no real migration exists
until T2.3.4), injected by monkeypatching the command's `pending`.
"""

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
    assert "al día" in result.output
    assert not (vault / ".wolta" / "backups").exists()


def test_legacy_vault_without_version_no_error(tmp_path):
    # minimal vault: .wolta/ exists but no version file; a CLAUDE.md with no markers
    (tmp_path / ".wolta").mkdir()
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE\n\nno markers here\n", encoding="utf-8")

    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(tmp_path)])

    assert result.exit_code == 0
    assert "al día" in result.output


def test_dry_run_does_not_modify(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_ApplyMig()])

    result = CliRunner().invoke(
        upgrade_mod.upgrade_command, ["--vault-path", str(vault), "--dry-run"]
    )

    assert result.exit_code == 0
    assert "DRY-RUN" in result.output
    assert _ApplyMig.REL in result.output
    # nothing written, no snapshot, version untouched
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
    assert "UPGRADE APLICADO" in result.output
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
    # the half-written file was created then rolled back (removed)
    assert not (vault / _FailMig.REL).exists()
    # version unchanged
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == __version__
    assert data["applied_migrations"] == []


def test_to_version_above_cli_is_rejected(tmp_path):
    vault = _make_vault(tmp_path)
    result = CliRunner().invoke(
        upgrade_mod.upgrade_command, ["--vault-path", str(vault), "--to-version", "9.9.9"]
    )

    assert result.exit_code == 1
    assert "mayor que la versión del CLI" in result.output


def test_corrupt_markers_abort_in_preflight(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    # break CLAUDE.md markers: a start with no end
    (vault / "CLAUDE.md").write_text(
        '# X\n<!-- wolta:managed:start id="agent-instructions" -->\nbody\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_ApplyMig()])

    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])

    assert result.exit_code == 1
    assert "markers" in result.output.lower()
    assert not (vault / ".wolta" / "backups").exists()
    assert not (vault / _ApplyMig.REL).exists()
