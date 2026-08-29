"""Integration tests for `wolta upgrade` (T2.3.3) and the v0.2.0 runner hooks."""

import hashlib
import json

from click.testing import CliRunner

import wolta.commands.upgrade as upgrade_mod
import wolta.migrations as reg
from wolta import __version__
from wolta.core.moves import Move, MoveState
from wolta.generators.structure import StructureGenerator
from wolta.migrations.base import Migration, MigrationContext


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


# --- 2.4: migrations relocate only through the context ---------------------


def _legacy_vault(tmp_path):
    """A 0.1.0-shaped vault: categories hang from the root."""
    (tmp_path / ".wolta").mkdir()
    (tmp_path / ".wolta" / "version").write_text(
        json.dumps({"schema_version": "0.1.0", "applied_migrations": []}),
        encoding="utf-8",
    )
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE\n", encoding="utf-8")
    (tmp_path / "IDENTITY").mkdir()
    (tmp_path / "IDENTITY" / "note.md").write_text("café\n", encoding="utf-8")
    (tmp_path / "WORK").mkdir()
    (tmp_path / "WORK" / "note.md").write_text("work\n", encoding="utf-8")
    return tmp_path


def _file_inventory(vault):
    found = {}
    for path in vault.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(vault).as_posix()
        if rel.startswith(".wolta/backups/"):
            continue
        found[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


class _FailAfterMove(Migration):
    target_version = "0.2.0"

    def up(self, ctx: MigrationContext):
        ctx.move("IDENTITY", "SYSTEM/IDENTITY")
        if not ctx.dry_run:
            raise RuntimeError("boom")
        return []


def test_a_migration_moves_only_through_the_context(tmp_path):
    vault = _legacy_vault(tmp_path)
    ctx = upgrade_mod._make_context(vault, dry_run=False)

    assert ctx.move("IDENTITY", "SYSTEM/IDENTITY") is MoveState.PENDING

    assert not (vault / "IDENTITY").exists()
    assert (vault / "SYSTEM" / "IDENTITY" / "note.md").read_text(encoding="utf-8") == "café\n"
    assert list(ctx.plan) == [Move("IDENTITY", "SYSTEM/IDENTITY")]


def test_context_move_is_a_noop_on_dry_run(tmp_path):
    vault = _legacy_vault(tmp_path)
    ctx = upgrade_mod._make_context(vault, dry_run=True)

    assert ctx.move("IDENTITY", "SYSTEM/IDENTITY") is MoveState.PENDING
    assert (vault / "IDENTITY" / "note.md").exists()
    assert not (vault / "SYSTEM").exists()
    assert list(ctx.plan) == []


def test_failed_structural_migration_restores_user_bytes(tmp_path, monkeypatch):
    """2.3 through the runner: an injected failure leaves the vault as it was."""
    vault = _legacy_vault(tmp_path)
    before = _file_inventory(vault)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [_FailAfterMove()])

    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(vault)])

    assert result.exit_code == 1
    assert "rollback" in result.output.lower()
    assert _file_inventory(vault) == before
    assert (vault / "IDENTITY" / "note.md").exists()
    assert not (vault / "SYSTEM").exists()
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"


# --- 2.5: multi-hop chain in a single upgrade ------------------------------


class _Hop(Migration):
    def __init__(self, target, minimum, rel):
        self.target_version = target
        self.min_version = minimum
        self.rel = rel

    def up(self, ctx: MigrationContext):
        ctx.files.write_managed(ctx.vault, self.rel, self.target_version, dry_run=ctx.dry_run)
        return [self.rel]


def test_two_hops_apply_in_a_single_upgrade(tmp_path, monkeypatch):
    """D-11 through the runner: starting at 0.0.0, both hops land in one call.

    Versions sit under the CLI's 0.1.0 so the --to-version gate does not
    get in the way; the min_version relationship is the same as 0.1.0 -> 0.2.0.
    """
    (tmp_path / ".wolta").mkdir()
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE\n", encoding="utf-8")
    first = _Hop("0.0.1", "0.0.0", "step-1.md")
    second = _Hop("0.1.0", "0.0.1", "step-2.md")
    monkeypatch.setattr(reg, "all_migrations", lambda: [first, second])

    result = CliRunner().invoke(upgrade_mod.upgrade_command, ["--vault-path", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "step-1.md").read_text(encoding="utf-8") == "0.0.1"
    assert (tmp_path / "step-2.md").read_text(encoding="utf-8") == "0.1.0"
    data = json.loads((tmp_path / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"
    assert [m["target"] for m in data["applied_migrations"]] == ["0.0.1", "0.1.0"]
