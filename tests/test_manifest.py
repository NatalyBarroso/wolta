"""Unit tests for the file classification manifest (T2.3.3)."""

import pytest

from wolta.core.manifest import Policy, classify


@pytest.mark.parametrize(
    "rel,expected",
    [
        ("README.md", Policy.MANAGED),
        ("raw/README.md", Policy.MANAGED),
        ("AI-SYSTEM/SKILLS/bootstrap-generate.md", Policy.MANAGED),
        ("AI-SYSTEM/SKILLS/raw-ingest.md", Policy.MANAGED),
        ("AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md", Policy.MANAGED),
        ("AI-SYSTEM/SKILLS/source-files.md", Policy.MANAGED),
        ("TEMPLATES/template-source-adapter.md", Policy.MANAGED),
        ("CLAUDE.md", Policy.MANAGED_SECTION),
        ("DESIGN.md", Policy.MANAGED_SECTION),
    ],
)
def test_managed_files(rel, expected):
    assert classify(rel) == expected


def test_source_files_exact_beats_glob():
    # source-files.md is the system adapter (managed); other source-*.md are user-owned
    assert classify("AI-SYSTEM/SKILLS/source-files.md") == Policy.MANAGED
    assert classify("AI-SYSTEM/SKILLS/source-notion.md") == Policy.USER_OWNED


@pytest.mark.parametrize(
    "rel",
    [
        "IDENTITY/identity-profile.md",
        "WORK/work-overview.md",
        ".wolta/config.md",
        "TEMPLATES/template-note.md",
        "raw/processed/whatever.md",
        "AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md",
        "some/unknown/file.md",
    ],
)
def test_default_is_user_owned(rel):
    assert classify(rel) == Policy.USER_OWNED


def test_windows_separators_normalized():
    assert classify("AI-SYSTEM\\SKILLS\\source-files.md") == Policy.MANAGED
