"""Unit tests for checksum-guarded writes (T2.3.3) and re-keying (v0.2.0 2.2)."""

from wolta.core import files, moves
from wolta.core.moves import Move

MOVE = Move(src="IDENTITY", dst="SYSTEM/IDENTITY")


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


def test_the_bytes_written_hash_to_the_checksum_recorded(tmp_path):
    """No line-ending translation between the write and the hash.

    Text mode would turn "\\n" into the platform separator on Windows, so the
    file would never hash to the value just stored for it -- and every later
    upgrade would read that as a user edit and drop a needless `.bak`.
    """
    vault = _vault(tmp_path)
    rel = "README.md"
    content = "line one\nline two\n"

    files.write_managed(vault, rel, content)

    assert (vault / rel).read_bytes() == content.encode("utf-8")
    assert files.sha256(vault / rel) == files.load_checksums(vault)[rel]


def test_no_spurious_backup_on_an_untouched_managed_file(tmp_path):
    vault = _vault(tmp_path)
    rel = "README.md"
    files.write_managed(vault, rel, "v1\nwith a newline\n")

    files.write_managed(vault, rel, "v2\nwith a newline\n")

    assert not (vault / (rel + ".bak")).exists()


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


# --- re-keying after a move (v0.2.0 task 2.2) ------------------------------


def test_keys_under_a_moved_directory_follow_it(tmp_path):
    vault = _vault(tmp_path)
    files.save_checksums(vault, {
        "IDENTITY/identity-profile.md": "aaa",
        "IDENTITY/nested/deep.md": "bbb",
    })

    renamed = files.rekey_checksums(vault, [MOVE])

    assert renamed == {
        "IDENTITY/identity-profile.md": "SYSTEM/IDENTITY/identity-profile.md",
        "IDENTITY/nested/deep.md": "SYSTEM/IDENTITY/nested/deep.md",
    }
    assert files.load_checksums(vault) == {
        "SYSTEM/IDENTITY/identity-profile.md": "aaa",
        "SYSTEM/IDENTITY/nested/deep.md": "bbb",
    }


def test_no_key_is_left_pointing_at_an_old_path(tmp_path):
    """The done criteria of 2.2, stated as its own assertion."""
    vault = _vault(tmp_path)
    categories = ["IDENTITY", "PREFERENCES", "WORK", "PROJECTS",
                  "PERSONAL-SPACE", "KNOWLEDGE", "AI-SYSTEM"]
    files.save_checksums(
        vault, {f"{name}/note.md": "x" for name in categories}
    )

    files.rekey_checksums(
        vault, [Move(name, f"SYSTEM/{name}") for name in categories]
    )

    assert all(
        key.startswith("SYSTEM/") for key in files.load_checksums(vault)
    )


def test_a_moved_file_is_rekeyed_exactly(tmp_path):
    """DESIGN.md moves on its own (8.3 step 3), not as part of a directory."""
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"DESIGN.md": "aaa"})

    files.rekey_checksums(vault, [Move("DESIGN.md", "SYSTEM/DESIGN.md")])

    assert files.load_checksums(vault) == {"SYSTEM/DESIGN.md": "aaa"}


def test_keys_outside_the_move_are_untouched(tmp_path):
    """CLAUDE.md and README.md stay at the root (D-08)."""
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"CLAUDE.md": "aaa", "README.md": "bbb"})

    assert files.rekey_checksums(vault, [MOVE]) == {}
    assert files.load_checksums(vault) == {"CLAUDE.md": "aaa", "README.md": "bbb"}


def test_a_similarly_named_sibling_is_not_dragged_along(tmp_path):
    """`IDENTITY` must not match `IDENTITY-ARCHIVE`, the classic prefix bug."""
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"IDENTITY-ARCHIVE/old.md": "aaa"})

    assert files.rekey_checksums(vault, [MOVE]) == {}
    assert "IDENTITY-ARCHIVE/old.md" in files.load_checksums(vault)


def test_rekeying_twice_changes_nothing_the_second_time(tmp_path):
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"IDENTITY/profile.md": "aaa"})

    files.rekey_checksums(vault, [MOVE])
    assert files.rekey_checksums(vault, [MOVE]) == {}
    assert files.load_checksums(vault) == {"SYSTEM/IDENTITY/profile.md": "aaa"}


def test_a_key_already_at_the_destination_wins(tmp_path):
    """Only a half-finished rekey can produce this; keep what it wrote."""
    vault = _vault(tmp_path)
    files.save_checksums(vault, {
        "IDENTITY/profile.md": "stale",
        "SYSTEM/IDENTITY/profile.md": "current",
    })

    files.rekey_checksums(vault, [MOVE])

    assert files.load_checksums(vault) == {"SYSTEM/IDENTITY/profile.md": "current"}


def test_dry_run_reports_without_writing(tmp_path):
    vault = _vault(tmp_path)
    files.save_checksums(vault, {"IDENTITY/profile.md": "aaa"})

    renamed = files.rekey_checksums(vault, [MOVE], dry_run=True)

    assert renamed == {"IDENTITY/profile.md": "SYSTEM/IDENTITY/profile.md"}
    assert files.load_checksums(vault) == {"IDENTITY/profile.md": "aaa"}


def test_a_vault_with_no_checksums_file_is_not_given_one(tmp_path):
    vault = _vault(tmp_path)

    assert files.rekey_checksums(vault, [MOVE]) == {}
    assert not (vault / ".wolta" / "checksums.json").exists()


def test_the_guard_still_backs_up_after_a_move(tmp_path):
    """Why 2.2 exists: skip the rekey and the next upgrade eats a user edit."""
    vault = _vault(tmp_path)
    rel = "IDENTITY/profile.md"
    files.write_managed(vault, rel, "v1")

    plan = moves.MovePlan()
    moves.apply(vault, MOVE, plan=plan)
    files.rekey_checksums(vault, plan)

    moved = "SYSTEM/IDENTITY/profile.md"
    (vault / moved).write_text("user edit", encoding="utf-8")
    files.write_managed(vault, moved, "v2")

    backup = vault / (moved + ".bak")
    assert backup.exists(), "the user's edit was overwritten without a backup"
    assert backup.read_text(encoding="utf-8") == "user edit"
