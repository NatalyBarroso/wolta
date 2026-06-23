"""Integration test: a freshly generated vault carries version tracking and
managed markers (T2.3.2 done criteria)."""

import json

import pytest
import yaml

from wolta import __version__
from wolta.generators.structure import StructureGenerator

# Managed full-file artifacts that must carry `wolta_version` in frontmatter.
MANAGED_FRONTMATTER_FILES = [
    "AI-SYSTEM/SKILLS/bootstrap-generate.md",
    "AI-SYSTEM/SKILLS/raw-ingest.md",
    "AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md",
    "AI-SYSTEM/SKILLS/source-files.md",
    "TEMPLATES/template-source-adapter.md",
]


@pytest.fixture
def vault(tmp_path):
    StructureGenerator(str(tmp_path)).generate()
    return tmp_path


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{path} has no frontmatter"
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)


def test_version_file_written_with_cli_version(vault):
    version_file = vault / ".wolta" / "version"
    assert version_file.exists()
    data = json.loads(version_file.read_text(encoding="utf-8"))
    assert data["schema_version"] == __version__


def test_claude_md_has_balanced_managed_markers(vault):
    text = (vault / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.count('wolta:managed:start id="agent-instructions"') == 1
    assert text.count('wolta:managed:end id="agent-instructions"') == 1
    # the user section sits OUTSIDE the managed block
    assert "## User notes" in text


def test_design_md_has_balanced_managed_markers(vault):
    text = (vault / "DESIGN.md").read_text(encoding="utf-8")
    assert text.count('wolta:managed:start id="vault-spec"') == 1
    assert text.count('wolta:managed:end id="vault-spec"') == 1


def test_managed_files_have_wolta_version(vault):
    for rel in MANAGED_FRONTMATTER_FILES:
        fm = _frontmatter(vault / rel)
        assert fm.get("wolta_version") == __version__, rel


def test_config_md_has_no_authoritative_version(vault):
    text = (vault / ".wolta" / "config.md").read_text(encoding="utf-8")
    assert "Version: 0.1.0" not in text
