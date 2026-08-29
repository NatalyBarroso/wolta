"""Migration 0.1.0 -> 0.2.0: the HUMAN/SYSTEM split (tasks 3.2, 3.3, 3.4).

Grouped by the question each block answers: does the migration refuse to start
on a vault it cannot finish, does it produce the target tree, and does it
notice when the content it moved did not arrive intact.
"""

import hashlib
import json

import pytest
from click.testing import CliRunner

import wolta.commands.upgrade as upgrade_mod
from pathlib import Path

from wolta.migrations import m_0_2_0
from wolta.migrations.m_0_2_0 import IntegrityError, MigrationV020, PreflightError

# Managed files a 0.1.0 vault has, at the paths that release used.
_MANAGED_010 = (
    "README.md",
    "raw/README.md",
    "AI-SYSTEM/SKILLS/bootstrap-generate.md",
    "AI-SYSTEM/SKILLS/raw-ingest.md",
    "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md",
    "AI-SYSTEM/SKILLS/source-files.md",
    "TEMPLATES/template-source-adapter.md",
)

_CLAUDE_010 = (
    "# WOLTA\n\n"
    '<!-- wolta:managed:start id="agent-instructions" v="0.1.0" -->\n'
    "old 0.1.0 instructions pointing at AI-SYSTEM/SKILLS/\n"
    '<!-- wolta:managed:end id="agent-instructions" -->\n\n'
    "## User notes\n\nMY OWN NOTES\n"
)

_DESIGN_010 = (
    "---\ntitle: DESIGN\n---\n\n"
    '<!-- wolta:managed:start id="vault-spec" v="0.1.0" -->\n'
    "old spec with the categories at the root\n"
    '<!-- wolta:managed:end id="vault-spec" -->\n\n'
    "## User notes\n\nMY DESIGN ADDENDUM\n"
)


@pytest.fixture
def vault(tmp_path):
    """A 0.1.0-shaped vault: everything hangs off the root, no HUMAN/."""
    (tmp_path / ".wolta").mkdir()
    (tmp_path / ".wolta" / "version").write_text(
        json.dumps({"schema_version": "0.1.0", "applied_migrations": []}),
        encoding="utf-8",
    )

    (tmp_path / "CLAUDE.md").write_text(_CLAUDE_010, encoding="utf-8")
    (tmp_path / "DESIGN.md").write_text(_DESIGN_010, encoding="utf-8")

    for category in ("IDENTITY", "PREFERENCES", "WORK", "PROJECTS",
                     "PERSONAL-SPACE", "KNOWLEDGE"):
        (tmp_path / category).mkdir()
        (tmp_path / category / f"note-{category.lower()}.md").write_text(
            f"{category} note — café\n", encoding="utf-8"
        )

    (tmp_path / "AI-SYSTEM" / "SKILLS").mkdir(parents=True)
    (tmp_path / "AI-SYSTEM" / "CONTEXT").mkdir()
    (tmp_path / "TEMPLATES").mkdir()
    (tmp_path / "raw" / "processed").mkdir(parents=True)

    for rel in _MANAGED_010:
        (tmp_path / rel).write_text(f"0.1.0 content of {rel}\n", encoding="utf-8")

    (tmp_path / ".wolta" / "checksums.json").write_text(
        json.dumps(
            {rel: _sha(tmp_path / rel) for rel in _MANAGED_010}, indent=2
        ),
        encoding="utf-8",
    )
    return tmp_path


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory(root):
    """Every file in the vault by digest, ignoring the snapshots themselves."""
    found = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".wolta/backups/"):
            continue
        found[rel] = _sha(path)
    return found


def _ctx(vault, dry_run=False):
    return upgrade_mod._make_context(vault, dry_run=dry_run)


def _run(vault, *args):
    return CliRunner().invoke(
        upgrade_mod.upgrade_command, ["--vault-path", str(vault), *args]
    )


# --- 3.1: the 0.2.0 documents are frozen, not generated --------------------


def test_frozen_documents_exist_and_do_not_import_the_generator():
    """Done criteria of 3.1: data_v0_2_0/ is self-contained (D-02)."""
    data = Path(m_0_2_0.__file__).parent / "data_v0_2_0"
    for name in ("README.md", "claude-agent-instructions.md", "design-vault-spec.md"):
        assert (data / name).is_file(), name
    source = Path(m_0_2_0.__file__).read_text(encoding="utf-8")
    assert "wolta.generators" not in source


# --- 3.2: the migration refuses to start on a vault it cannot finish -------


def test_a_collision_stops_before_anything_moves(vault):
    """Both ends on disk is ambiguous, and guessing could merge two trees."""
    (vault / "SYSTEM" / "WORK").mkdir(parents=True)
    before = _inventory(vault)

    with pytest.raises(PreflightError) as exc:
        MigrationV020().up(_ctx(vault))

    assert "WORK -> SYSTEM/WORK" in str(exc.value)
    assert _inventory(vault) == before
    # Not even the moves that would have succeeded were attempted.
    assert (vault / "IDENTITY").is_dir()
    assert not (vault / "SYSTEM" / "IDENTITY").exists()


def test_a_space_name_taken_by_a_file_is_refused(vault):
    (vault / "HUMAN").write_text("this is not a folder\n", encoding="utf-8")

    with pytest.raises(PreflightError, match="not a directory"):
        MigrationV020().up(_ctx(vault))


def test_a_human_space_the_user_already_filled_is_refused(vault):
    """8.2.2: merging into a folder the user created would be destructive."""
    (vault / "HUMAN").mkdir()
    (vault / "HUMAN" / "my-projects").mkdir()
    before = _inventory(vault)

    with pytest.raises(PreflightError, match="HUMAN"):
        MigrationV020().up(_ctx(vault))

    assert _inventory(vault) == before
    assert (vault / "IDENTITY").is_dir()


def test_a_system_space_the_user_already_filled_is_refused(vault):
    """SYSTEM/ with content and no destination already moved = not a resume."""
    (vault / "SYSTEM").mkdir()
    (vault / "SYSTEM" / "scratch.md").write_text("mine\n", encoding="utf-8")
    before = _inventory(vault)

    with pytest.raises(PreflightError, match="SYSTEM"):
        MigrationV020().up(_ctx(vault))

    assert _inventory(vault) == before


def test_an_empty_system_folder_is_not_a_collision(vault):
    (vault / "SYSTEM").mkdir()

    MigrationV020().up(_ctx(vault))

    assert (vault / "SYSTEM" / "IDENTITY").is_dir()


def test_a_half_migrated_vault_is_finished_rather_than_refused(vault):
    """An interrupted run left some categories moved: pick up where it stopped."""
    (vault / "SYSTEM").mkdir()
    (vault / "IDENTITY").rename(vault / "SYSTEM" / "IDENTITY")

    MigrationV020().up(_ctx(vault))

    assert (vault / "SYSTEM" / "IDENTITY" / "note-identity.md").is_file()
    assert (vault / "SYSTEM" / "WORK" / "note-work.md").is_file()


def test_the_runner_reports_a_blocked_vault_without_touching_it(vault, monkeypatch):
    """The refusal happens in the dry pass, so it lands before the snapshot."""
    (vault / "SYSTEM" / "WORK").mkdir(parents=True)
    before = _inventory(vault)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [MigrationV020()])

    result = _run(vault)

    assert result.exit_code == 1
    assert "cannot be upgraded" in result.output
    assert "Nothing was modified" in result.output
    assert not (vault / ".wolta" / "backups").exists()
    assert _inventory(vault) == before


def test_corrupt_markers_are_caught_in_the_pre_split_layout(vault, monkeypatch):
    """DESIGN.md is still at the root here, which is where it must be checked.

    Looking only at the manifest path (`SYSTEM/DESIGN.md`) would find nothing
    and let the broken markers blow up mid-apply instead of in pre-flight.
    """
    (vault / "DESIGN.md").write_text(
        '<!-- wolta:managed:start id="vault-spec" -->\nno end marker\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [MigrationV020()])

    result = _run(vault)

    assert result.exit_code == 1
    assert "markers" in result.output.lower()
    assert "DESIGN.md" in result.output
    assert not (vault / "SYSTEM").exists()


# --- 3.3: a 0.1.0 vault comes out shaped like section 4.1 of the plan ------


def test_the_agent_space_collects_everything_that_was_at_the_root(vault):
    MigrationV020().up(_ctx(vault))

    for rel in ("IDENTITY", "PREFERENCES", "WORK", "PROJECTS", "PERSONAL-SPACE",
                "KNOWLEDGE", "AI-SYSTEM", "TEMPLATES", "raw", "DESIGN.md"):
        assert not (vault / rel).exists(), f"{rel} should have left the root"
        assert (vault / "SYSTEM" / rel).exists(), f"{rel} should be under SYSTEM/"


def test_the_user_space_is_created_empty(vault):
    MigrationV020().up(_ctx(vault))

    human = vault / "HUMAN"
    assert human.is_dir()
    assert [p.name for p in human.iterdir()] == [".gitkeep"]


def test_the_root_artifacts_stay_at_the_root(vault):
    MigrationV020().up(_ctx(vault))

    assert (vault / ".wolta" / "version").is_file()
    assert (vault / "CLAUDE.md").is_file()
    assert (vault / "README.md").is_file()
    assert not (vault / "SYSTEM" / "README.md").exists()


def test_user_notes_cross_the_move_byte_for_byte(vault):
    before = {
        rel: digest
        for rel, digest in _inventory(vault).items()
        if rel.startswith(("IDENTITY/", "WORK/", "KNOWLEDGE/"))
    }

    MigrationV020().up(_ctx(vault))

    for rel, digest in before.items():
        assert _sha(vault / "SYSTEM" / rel) == digest, rel


def test_checksums_follow_their_files(vault):
    """A key left behind turns off the .bak guard for that file (task 2.2)."""
    MigrationV020().up(_ctx(vault))

    sums = json.loads((vault / ".wolta" / "checksums.json").read_text(encoding="utf-8"))
    assert "SYSTEM/AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md" in sums
    assert "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md" not in sums
    assert "README.md" in sums  # stayed at the root, so its key stays too


def test_a_user_edit_is_backed_up_after_the_move(vault):
    """10.9: the re-keyed guard still creates a .bak on the next write."""
    from wolta.core import files

    MigrationV020().up(_ctx(vault))
    moved = "SYSTEM/AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"
    (vault / moved).write_text("user edit\n", encoding="utf-8")
    files.write_managed(vault, moved, "v2 after 0.2.0\n")

    backup = vault / (moved + ".bak")
    assert backup.is_file()
    assert backup.read_text(encoding="utf-8") == "user edit\n"


def test_the_documents_describe_the_new_tree(vault):
    MigrationV020().up(_ctx(vault))

    claude = (vault / "CLAUDE.md").read_text(encoding="utf-8")
    assert "MY OWN NOTES" in claude                      # outside the markers
    assert "old 0.1.0 instructions" not in claude        # inside them, replaced
    assert "SYSTEM/AI-SYSTEM/SKILLS/" in claude
    assert 'wolta:managed:start id="agent-instructions" v="0.2.0"' in claude

    design = (vault / "SYSTEM" / "DESIGN.md").read_text(encoding="utf-8")
    assert "MY DESIGN ADDENDUM" in design
    assert "old spec with the categories" not in design
    assert 'wolta:managed:start id="vault-spec" v="0.2.0"' in design

    readme = (vault / "README.md").read_text(encoding="utf-8")
    assert "SYSTEM/DESIGN.md" in readme
    assert "HUMAN/" in readme


def test_running_it_twice_changes_nothing_the_second_time(vault):
    MigrationV020().up(_ctx(vault))
    after_first = _inventory(vault)

    assert MigrationV020().up(_ctx(vault)) == []
    assert _inventory(vault) == after_first


def test_dry_run_touches_nothing_and_reports_pre_move_paths(vault):
    """The dry pass output is what the runner snapshots, so it has to name the
    paths the files still occupy — backing up `SYSTEM/DESIGN.md` before the
    move would copy nothing and leave the real one unprotected."""
    before = _inventory(vault)

    changed = MigrationV020().up(_ctx(vault, dry_run=True))

    assert _inventory(vault) == before
    assert not (vault / "SYSTEM").exists()
    assert not (vault / "HUMAN").exists()
    assert "DESIGN.md" in changed
    assert "SYSTEM/DESIGN.md" not in changed


def test_dry_run_lists_the_planned_moves(vault, monkeypatch):
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [MigrationV020()])

    result = _run(vault, "--dry-run")

    assert result.exit_code == 0, result.output
    assert "Moves:" in result.output
    assert "IDENTITY -> SYSTEM/IDENTITY" in result.output
    assert "DESIGN.md -> SYSTEM/DESIGN.md" in result.output
    assert not (vault / "SYSTEM").exists()


def test_the_runner_upgrades_a_010_vault_end_to_end(vault):
    """Through the real registry: no monkeypatching of `pending`."""
    result = _run(vault)

    assert result.exit_code == 0, result.output
    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.2.0"
    assert [m["target"] for m in data["applied_migrations"]] == ["0.2.0"]
    assert (vault / "SYSTEM" / "AI-SYSTEM" / "SKILLS").is_dir()
    assert (vault / "HUMAN").is_dir()


# --- 3.4: the content is checked, not assumed ------------------------------


def test_verify_accepts_a_move_that_preserved_everything(vault):
    migration = MigrationV020()
    baseline = migration._census(_ctx(vault))
    migration.up(_ctx(vault))

    # No exception: every hashed file was found again at its relocated path.
    migration._verify(_ctx(vault), baseline, rewritten=["CLAUDE.md", "README.md",
                                                        "SYSTEM/DESIGN.md"])


def test_verify_reports_a_file_that_lost_its_content(vault):
    migration = MigrationV020()
    baseline = migration._census(_ctx(vault))
    migration.up(_ctx(vault))
    (vault / "SYSTEM" / "WORK" / "note-work.md").write_text("rewritten\n", encoding="utf-8")

    with pytest.raises(IntegrityError, match="altered"):
        migration._verify(_ctx(vault), baseline, rewritten=["CLAUDE.md", "README.md",
                                                            "SYSTEM/DESIGN.md"])


def test_verify_reports_a_file_that_went_missing(vault):
    migration = MigrationV020()
    baseline = migration._census(_ctx(vault))
    migration.up(_ctx(vault))
    (vault / "SYSTEM" / "WORK" / "note-work.md").unlink()

    with pytest.raises(IntegrityError, match="missing"):
        migration._verify(_ctx(vault), baseline, rewritten=["CLAUDE.md", "README.md",
                                                            "SYSTEM/DESIGN.md"])


def test_a_digest_that_does_not_match_rolls_the_whole_upgrade_back(vault, monkeypatch):
    """One altered sha256 is enough to abandon the migration.

    The corruption is injected into the post-move census rather than into a
    file, so the vault on disk is genuinely intact and the rollback can be
    checked byte for byte. What is under test is the reaction to a mismatch,
    not the snapshot's ability to restore a file nobody declared.
    """
    before = _inventory(vault)
    monkeypatch.setattr(upgrade_mod, "pending", lambda c, t: [MigrationV020()])

    real_census = MigrationV020._census
    passes = []

    def flaky_census(self, ctx):
        census = real_census(self, ctx)
        passes.append(1)
        if len(passes) > 1:  # the pass taken after the moves
            census["SYSTEM/IDENTITY/note-identity.md"] = "0" * 64
        return census

    monkeypatch.setattr(MigrationV020, "_census", flaky_census)

    result = _run(vault)

    assert result.exit_code == 1
    assert "did not preserve" in result.output
    assert "rollback" in result.output.lower()

    assert _inventory(vault) == before
    assert (vault / "IDENTITY" / "note-identity.md").is_file()
    assert (vault / "DESIGN.md").read_text(encoding="utf-8") == _DESIGN_010
    assert not (vault / "SYSTEM").exists()
    assert not (vault / "HUMAN" / ".gitkeep").exists()

    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"
