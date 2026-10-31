"""Unit tests for snapshot / rollback (T2.3.3) and inverse-plan undo (v0.2.0 2.3)."""

import hashlib

from wolta.core import files, snapshot
from wolta.core.moves import Move
from wolta.migrations.base import MigrationContext


def _vault(tmp_path):
    (tmp_path / ".wolta").mkdir()
    (tmp_path / ".wolta" / "version").write_text('{"schema_version": "0.1.0"}', encoding="utf-8")
    return tmp_path


def _inventory(vault):
    """sha256 of every file except the snapshot itself."""
    found = {}
    for path in vault.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(vault).as_posix()
        if rel.startswith(".wolta/backups/"):
            continue
        found[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def _ctx(vault, snap, dry_run=False):
    return MigrationContext(
        vault=vault,
        manifest=None,
        sections=None,
        files=files,
        dry_run=dry_run,
        snapshot_dir=snap,
    )


def test_snapshot_copies_only_tracked_plus_version(tmp_path):
    vault = _vault(tmp_path)
    (vault / "AI-SYSTEM" / "SKILLS").mkdir(parents=True)
    (vault / "AI-SYSTEM" / "SKILLS" / "INGEST-PROTOCOL.md").write_text("orig", encoding="utf-8")

    snap = snapshot.create_snapshot(vault, ["AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"])

    assert (snap / "AI-SYSTEM" / "SKILLS" / "INGEST-PROTOCOL.md").exists()
    assert (snap / ".wolta" / "version").exists()


def test_rollback_restores_modified_file(tmp_path):
    vault = _vault(tmp_path)
    target = vault / "CLAUDE.md"
    target.write_text("original", encoding="utf-8")

    snap = snapshot.create_snapshot(vault, ["CLAUDE.md"])
    target.write_text("corrupted by failed migration", encoding="utf-8")

    snapshot.rollback(vault, snap)

    assert target.read_text(encoding="utf-8") == "original"


def test_rollback_removes_created_file(tmp_path):
    vault = _vault(tmp_path)
    # file does NOT exist at snapshot time but is in the change-set
    snap = snapshot.create_snapshot(vault, ["AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"])

    # a (failed) migration created it
    created = vault / "AI-SYSTEM" / "SKILLS" / "INGEST-PROTOCOL.md"
    created.parent.mkdir(parents=True, exist_ok=True)
    created.write_text("half-created", encoding="utf-8")

    snapshot.rollback(vault, snap)

    assert not created.exists()


# --- inverse-plan rollback (v0.2.0 task 2.3 / test 10.8) -------------------


def test_rollback_puts_moved_user_bytes_back_exactly(tmp_path):
    """Done criteria of 2.3: a failure mid-move leaves the vault as it was."""
    vault = _vault(tmp_path)
    (vault / "IDENTITY").mkdir()
    (vault / "IDENTITY" / "note.md").write_text("acentos: café, ñandú\n", encoding="utf-8")
    (vault / "WORK").mkdir()
    (vault / "WORK" / "note.md").write_text("work stays put until we get there\n", encoding="utf-8")
    (vault / "DESIGN.md").write_text("# DESIGN\noriginal\n", encoding="utf-8")
    files.seed_checksums(vault, ["DESIGN.md"])
    before = _inventory(vault)

    snap = snapshot.create_snapshot(vault, ["DESIGN.md"])
    ctx = _ctx(vault, snap)
    ctx.move("IDENTITY", "SYSTEM/IDENTITY")
    ctx.move("DESIGN.md", "SYSTEM/DESIGN.md")
    ctx.rekey_checksums()
    (vault / "SYSTEM" / "DESIGN.md").write_text("# DESIGN\nhalf-written\n", encoding="utf-8")
    # ...and then the run dies before WORK is touched.

    snapshot.rollback(vault, snap)

    assert _inventory(vault) == before
    assert (vault / "IDENTITY" / "note.md").exists()
    assert (vault / "WORK" / "note.md").exists()
    assert (vault / "DESIGN.md").read_text(encoding="utf-8") == "# DESIGN\noriginal\n"
    assert not (vault / "SYSTEM").exists()


def test_rollback_without_a_move_plan_still_restores_files(tmp_path):
    """A content-only migration has no plan; the original path must keep working."""
    vault = _vault(tmp_path)
    target = vault / "CLAUDE.md"
    target.write_text("original", encoding="utf-8")
    snap = snapshot.create_snapshot(vault, ["CLAUDE.md"])
    target.write_text("changed", encoding="utf-8")

    snapshot.rollback(vault, snap)

    assert target.read_text(encoding="utf-8") == "original"


def test_a_directory_is_not_copied_into_the_snapshot(tmp_path):
    """D-04: relocating a tree is undone by rename, not by copying it."""
    vault = _vault(tmp_path)
    (vault / "IDENTITY").mkdir()
    (vault / "IDENTITY" / "note.md").write_text("user\n", encoding="utf-8")

    snap = snapshot.create_snapshot(vault, ["IDENTITY"])

    assert not (snap / "IDENTITY").exists()


def test_checksums_are_always_snapshotted(tmp_path):
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"DESIGN.md": "aaa"})

    snap = snapshot.create_snapshot(vault, [])

    assert (snap / ".wolta" / "checksums.json").exists()


def test_record_move_writes_the_plan_before_anyone_renames(tmp_path):
    vault = _vault(tmp_path)
    (vault / "IDENTITY").mkdir()
    (vault / "IDENTITY" / "note.md").write_text("user\n", encoding="utf-8")
    snap = snapshot.create_snapshot(vault, [])

    snapshot.record_move(vault, snap, Move("IDENTITY", "SYSTEM/IDENTITY"))

    # The directory is still at the source: persist-then-rename, not the reverse.
    assert (vault / "IDENTITY").exists()
    plan = (snap / snapshot.MOVE_PLAN_NAME).read_text(encoding="utf-8")
    assert "IDENTITY" in plan
    assert "SYSTEM/IDENTITY" in plan
