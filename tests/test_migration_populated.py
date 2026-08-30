"""Test 10.6 -- a vault with real volume keeps every user byte.

The Phase 3 suite migrates a handful of synthetic notes. This one is the
stop-the-line check of section 10: thirty or more user notes, accents, long
names, a skill the user added themselves, and a sha256 that must not move.

A second test walks the frozen copy of wolta-joanna when that bank is on
disk (task 0.2). It never touches the original vault.
"""

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from wolta.commands.upgrade import upgrade_command
from wolta.core.files import inventory, sha256
from wolta.core.manifest import Policy, classify
from wolta.core.moves import relocate_all
from wolta.migrations.m_0_2_0 import MOVES

# wolta-cli/tests/this.py -> 50.2 WOLTA/TEST/banco-0.2/...
_FROZEN = (
    Path(__file__).resolve().parents[2]
    / "TEST"
    / "banco-0.2"
    / "wolta-joanna-frozen-0.1.0"
)

_CATEGORIES = (
    "IDENTITY",
    "PREFERENCES",
    "WORK",
    "PROJECTS",
    "PERSONAL-SPACE",
    "KNOWLEDGE",
)

_MANAGED_010 = (
    "README.md",
    "raw/README.md",
    "AI-SYSTEM/SKILLS/bootstrap-generate.md",
    "AI-SYSTEM/SKILLS/raw-ingest.md",
    "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md",
    "AI-SYSTEM/SKILLS/source-files.md",
    "TEMPLATES/template-source-adapter.md",
)

_MARKERS = (
    "# WOLTA\n\n"
    '<!-- wolta:managed:start id="agent-instructions" v="0.1.0" -->\n'
    "old instructions\n"
    '<!-- wolta:managed:end id="agent-instructions" -->\n\n'
    "## User notes\n\nkeep me\n"
)

_DESIGN = (
    "---\ntitle: DESIGN\n---\n\n"
    '<!-- wolta:managed:start id="vault-spec" v="0.1.0" -->\n'
    "old spec\n"
    '<!-- wolta:managed:end id="vault-spec" -->\n'
)


def _seed_010(root: Path) -> None:
    (root / ".wolta").mkdir()
    (root / ".wolta" / "version").write_text(
        json.dumps({"schema_version": "0.1.0", "applied_migrations": []}),
        encoding="utf-8",
    )
    (root / "CLAUDE.md").write_text(_MARKERS, encoding="utf-8")
    (root / "DESIGN.md").write_text(_DESIGN, encoding="utf-8")
    for rel in _MANAGED_010:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"managed 0.1.0 {rel}\n", encoding="utf-8")
    (root / "raw" / "processed").mkdir(parents=True, exist_ok=True)


def _user_notes(vault: Path):
    """Pre-move paths whose post-move policy is still USER_OWNED."""
    notes = []
    for rel in inventory(vault, skip=(".wolta/",)):
        after = relocate_all(rel, MOVES)
        if classify(after) is Policy.USER_OWNED:
            notes.append(rel)
    return notes


def _upgrade(vault: Path):
    return CliRunner().invoke(upgrade_command, ["--vault-path", str(vault)])


def test_thirty_plus_user_notes_keep_their_bytes(tmp_path):
    """10.6: more than thirty user notes, none of them change."""
    vault = tmp_path / "populated"
    vault.mkdir()
    _seed_010(vault)

    written = []
    # Five notes in each of the six content categories = 30, plus extras.
    for category in _CATEGORIES:
        folder = vault / category
        folder.mkdir(exist_ok=True)
        for i in range(1, 6):
            rel = f"{category}/nota-{i:02d}-año-café.md"
            (vault / rel).write_text(
                f"# {category} {i}\n\ncontenido con acentos: niño, año, café.\n",
                encoding="utf-8",
            )
            written.append(rel)

    long_dir = vault / "PROJECTS" / "un-proyecto-con-nombre-muy-largo-y-ñ"
    long_dir.mkdir(parents=True, exist_ok=True)
    long_note = long_dir / "decision-técnica-2026.md"
    long_note.write_text("decisión: seguir con el rename, no copiar.\n", encoding="utf-8")
    written.append(long_note.relative_to(vault).as_posix())

    extra_skill = vault / "AI-SYSTEM" / "SKILLS" / "source-whatsapp.md"
    extra_skill.parent.mkdir(parents=True, exist_ok=True)
    extra_skill.write_text("# adapter del usuario\nno tocar\n", encoding="utf-8")
    written.append(extra_skill.relative_to(vault).as_posix())

    raw = vault / "raw" / "exportación-ñoño.txt"
    raw.write_text("fuente cruda\n", encoding="utf-8")
    written.append(raw.relative_to(vault).as_posix())

    notes = _user_notes(vault)
    assert len(notes) >= 30, notes
    before = {rel: sha256(vault / rel) for rel in notes}

    result = _upgrade(vault)
    assert result.exit_code == 0, result.output

    missing = []
    altered = []
    for rel, digest in before.items():
        moved = vault / relocate_all(rel, MOVES)
        if not moved.is_file():
            missing.append(rel)
        elif sha256(moved) != digest:
            altered.append(rel)

    assert not missing, f"user notes went missing: {missing[:5]}"
    assert not altered, f"user notes changed: {altered[:5]}"

    data = json.loads((vault / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.2.0"
    assert [p.name for p in (vault / "HUMAN").iterdir()] == [".gitkeep"]
    for category in _CATEGORIES:
        assert not (vault / category).exists()
        assert (vault / "SYSTEM" / category).is_dir()


@pytest.mark.skipif(not _FROZEN.is_dir(), reason="task 0.2 frozen copy is not on this machine")
def test_frozen_joanna_copy_keeps_user_bytes(tmp_path):
    """10.6 against the real notes, on a disposable copy of the bank.

    The frozen tree stays at 0.1.0. This test copies it into tmp and upgrades
    that copy. The live vault is never opened.
    """
    work = tmp_path / "joanna"
    shutil.copytree(_FROZEN, work)

    notes = _user_notes(work)
    assert len(notes) >= 30, f"bank has only {len(notes)} user-owned files"
    before = {rel: sha256(work / rel) for rel in notes}

    result = _upgrade(work)
    assert result.exit_code == 0, result.output

    altered = [
        rel
        for rel, digest in before.items()
        if sha256(work / relocate_all(rel, MOVES)) != digest
    ]
    missing = [rel for rel in before if not (work / relocate_all(rel, MOVES)).is_file()]
    assert not missing, missing[:8]
    assert not altered, altered[:8]

    data = json.loads((work / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.2.0"
    assert (work / "HUMAN" / ".gitkeep").is_file()
    assert (work / "SYSTEM" / "IDENTITY").is_dir()
    # Skills the user added themselves are not in the managed list.
    assert (work / "SYSTEM" / "AI-SYSTEM" / "SKILLS" / "bug-report.md").is_file()
    assert (work / "SYSTEM" / "AI-SYSTEM" / "SKILLS" / "session-log.md").is_file()
