"""Unit tests for checksum-guarded writes (T2.3.3)."""

from wolta.core import files


def _vault(tmp_path):
    (tmp_path / ".wolta").mkdir()
    return tmp_path


def test_write_creates_file_and_records_checksum(tmp_path):
    vault = _vault(tmp_path)
    rel = "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"

    changed = files.write_managed(vault, rel, "v1 content")

    assert changed == rel
    assert (vault / rel).read_text(encoding="utf-8") == "v1 content"
    assert files.load_checksums(vault)[rel] == files.sha256_text("v1 content")


def test_write_is_noop_when_unchanged(tmp_path):
    vault = _vault(tmp_path)
    rel = "README.md"
    files.write_managed(vault, rel, "same")

    assert files.write_managed(vault, rel, "same") is None


def test_dry_run_does_not_write(tmp_path):
    vault = _vault(tmp_path)
    rel = "README.md"

    result = files.write_managed(vault, rel, "content", dry_run=True)

    assert result == rel
    assert not (vault / rel).exists()


def test_backup_created_when_user_edited(tmp_path):
    vault = _vault(tmp_path)
    rel = "AI-SYSTEM/SKILLS/source-files.md"
    # wolta writes v1 and records its checksum
    files.write_managed(vault, rel, "v1")
    # user edits the file out-of-band
    (vault / rel).write_text("user edit", encoding="utf-8")

    # wolta upgrades to v2 -> must back up the user edit
    changed = files.write_managed(vault, rel, "v2")

    assert changed == rel
    backup = vault / (rel + ".bak")
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "user edit"
    assert (vault / rel).read_text(encoding="utf-8") == "v2"


def test_seed_checksums(tmp_path):
    vault = _vault(tmp_path)
    rel = "README.md"
    (vault / rel).write_text("seeded", encoding="utf-8")

    files.seed_checksums(vault, [rel, "does/not/exist.md"])

    sums = files.load_checksums(vault)
    assert sums[rel] == files.sha256_text("seeded")
    assert "does/not/exist.md" not in sums
