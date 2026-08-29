"""Unit tests for the file classification manifest (T2.3.3, v0.2.0 task 1.2)."""

import pytest

from wolta.core.manifest import Policy, classify


@pytest.mark.parametrize(
    "rel,expected",
    [
        ("README.md", Policy.MANAGED),
        ("SYSTEM/raw/README.md", Policy.MANAGED),
        ("SYSTEM/AI-SYSTEM/SKILLS/bootstrap-generate.md", Policy.MANAGED),
        ("SYSTEM/AI-SYSTEM/SKILLS/raw-ingest.md", Policy.MANAGED),
        ("SYSTEM/AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md", Policy.MANAGED),
        ("SYSTEM/AI-SYSTEM/SKILLS/source-files.md", Policy.MANAGED),
        ("SYSTEM/TEMPLATES/template-source-adapter.md", Policy.MANAGED),
        ("CLAUDE.md", Policy.MANAGED_SECTION),
        ("SYSTEM/DESIGN.md", Policy.MANAGED_SECTION),
    ],
)
def test_managed_files(rel, expected):
    assert classify(rel) == expected


def test_source_files_exact_beats_glob():
    # source-files.md is the system adapter (managed); other source-*.md are user-owned
    assert classify("SYSTEM/AI-SYSTEM/SKILLS/source-files.md") == Policy.MANAGED
    assert classify("SYSTEM/AI-SYSTEM/SKILLS/source-notion.md") == Policy.USER_OWNED


@pytest.mark.parametrize(
    "rel",
    [
        "HUMAN/notes.md",
        "HUMAN/clients/acme/contract.md",
        "HUMAN/deeply/nested/tree/of/the/users/own.md",
        # A name that collides with a managed artifact is still user-owned:
        # ownership follows the space, not the filename.
        "HUMAN/DESIGN.md",
        "HUMAN/AI-SYSTEM/SKILLS/raw-ingest.md",
    ],
)
def test_human_space_is_never_managed(rel):
    assert classify(rel) == Policy.USER_OWNED


@pytest.mark.parametrize(
    "rel",
    [
        "SYSTEM/IDENTITY/identity-profile.md",
        "SYSTEM/WORK/work-overview.md",
        ".wolta/config.md",
        "SYSTEM/TEMPLATES/template-note.md",
        "SYSTEM/raw/processed/whatever.md",
        "SYSTEM/AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md",
        "some/unknown/file.md",
    ],
)
def test_default_is_user_owned(rel):
    assert classify(rel) == Policy.USER_OWNED


@pytest.mark.parametrize(
    "rel",
    [
        "raw/README.md",
        "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md",
        "TEMPLATES/template-source-adapter.md",
        "DESIGN.md",
    ],
)
def test_legacy_root_paths_are_no_longer_managed(rel):
    """Pre-0.2.0 locations must not stay managed once the file has moved.

    Leaving them in would let an upgrade write to a path the vault abandoned.
    """
    assert classify(rel) == Policy.USER_OWNED


def test_windows_separators_normalized():
    assert classify("SYSTEM\\AI-SYSTEM\\SKILLS\\source-files.md") == Policy.MANAGED
    assert classify("HUMAN\\notes.md") == Policy.USER_OWNED
