"""The vault is split into HUMAN/ and SYSTEM/ (v0.2.0, task 1.1).

Checks the tree an initialized vault must produce: which artifacts live in the
user space, which in the agent space, and which must stay at the root (D-08).
"""

import json

import pytest
from click.testing import CliRunner

from wolta.commands.init import init_command
from wolta.core.layout import HUMAN_ROOT, SYSTEM_ROOT
from wolta.core.manifest import MANIFEST, Policy
from wolta.generators.structure import StructureGenerator

CATEGORIES = [
    "IDENTITY",
    "PREFERENCES",
    "WORK",
    "PROJECTS",
    "PERSONAL-SPACE",
    "KNOWLEDGE",
    "AI-SYSTEM",
]

AI_SYSTEM_SUBCATEGORIES = [
    "AGENTS",
    "BOOTSTRAP",
    "CONTEXT",
    "SESSIONS",
    "SKILLS",
    "WORKFLOWS",
]

# Anything the CLI used to drop in the root and now belongs to the agent space.
MOVED_TO_SYSTEM = CATEGORIES + ["TEMPLATES", "raw", "DESIGN.md"]


@pytest.fixture
def vault(tmp_path):
    StructureGenerator(str(tmp_path)).generate()
    return tmp_path


def test_human_space_is_born_empty(vault):
    """D-06: the user shapes HUMAN/, so wolta only leaves a .gitkeep in it."""
    human = vault / HUMAN_ROOT
    assert human.is_dir()
    assert [p.name for p in human.iterdir()] == [".gitkeep"]


def test_categories_live_under_system(vault):
    for category in CATEGORIES:
        assert (vault / SYSTEM_ROOT / category).is_dir(), category


def test_ai_system_subcategories_live_under_system(vault):
    for sub in AI_SYSTEM_SUBCATEGORIES:
        assert (vault / SYSTEM_ROOT / "AI-SYSTEM" / sub).is_dir(), sub


def test_agent_infrastructure_lives_under_system(vault):
    system = vault / SYSTEM_ROOT
    assert (system / "TEMPLATES" / "template-note.md").is_file()
    assert (system / "TEMPLATES" / "template-source-adapter.md").is_file()
    assert (system / "raw" / "processed").is_dir()
    assert (system / "raw" / "README.md").is_file()
    assert (system / "DESIGN.md").is_file()
    assert (system / "AI-SYSTEM" / "SKILLS" / "INGEST-PROTOCOL.md").is_file()


def test_root_artifacts_stay_at_the_root(vault):
    """`.wolta/` marks the vault and CLAUDE.md is auto-loaded from the root."""
    assert (vault / ".wolta" / "version").is_file()
    assert (vault / "CLAUDE.md").is_file()
    assert (vault / "README.md").is_file()


def test_nothing_is_left_behind_in_the_root(vault):
    for rel in MOVED_TO_SYSTEM:
        assert not (vault / rel).exists(), f"{rel} should have moved to {SYSTEM_ROOT}/"


@pytest.fixture
def initialized_vault(tmp_path):
    result = CliRunner().invoke(
        init_command, ["--vault-path", str(tmp_path), "--name", "test"]
    )
    assert result.exit_code == 0, result.output
    return tmp_path / "wolta-test"


def test_init_command_produces_the_split_layout(initialized_vault):
    """End-to-end: the three generators agree on where things go."""
    vault = initialized_vault
    system = vault / SYSTEM_ROOT

    assert (vault / HUMAN_ROOT).is_dir()
    assert (system / "AI-SYSTEM" / "BOOTSTRAP" / "BOOTSTRAP-QUESTIONNAIRE.md").is_file()
    assert (system / "TEMPLATES").is_dir()
    assert (vault / ".wolta" / "initialized").is_file()

    for rel in MOVED_TO_SYSTEM:
        assert not (vault / rel).exists(), f"{rel} should have moved to {SYSTEM_ROOT}/"


def test_seeded_checksums_match_the_files_on_disk(initialized_vault):
    """The manifest keys and the real layout must not drift apart (task 1.4).

    `seed_checksums()` skips paths it cannot find, so a stale manifest key does
    not fail init — it silently leaves that file unprotected against being
    clobbered on upgrade. Comparing the seeded keys against the manifest is what
    makes that silence audible.
    """
    vault = initialized_vault
    sums = json.loads((vault / ".wolta" / "checksums.json").read_text(encoding="utf-8"))

    managed = {rel for rel, pol in MANIFEST.items() if pol == Policy.MANAGED}
    assert set(sums) == managed

    for rel in sums:
        assert (vault / rel).is_file(), f"{rel} is in the manifest but not on disk"


def test_seeded_checksums_use_system_paths(initialized_vault):
    """Anchor on a literal path: catches manifest and layout moving in step but wrong."""
    sums = json.loads(
        (initialized_vault / ".wolta" / "checksums.json").read_text(encoding="utf-8")
    )
    assert "SYSTEM/AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md" in sums
    assert "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md" not in sums
    assert "README.md" in sums  # stays at the root (D-08)
