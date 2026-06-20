"""Unit tests for snapshot / rollback (T2.3.3)."""

from wolta.core import snapshot


def _vault(tmp_path):
    (tmp_path / ".wolta").mkdir()
    (tmp_path / ".wolta" / "version").write_text('{"schema_version": "0.1.0"}', encoding="utf-8")
    return tmp_path


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
