"""Test 10.4 -- no generated file may point at a pre-0.2.0 root path.

Most of the restructuring is not logic but prose: a couple of hundred path
references living inside the documentation that `wolta init` writes. Missing one
breaks nothing at runtime, which is exactly the problem -- the vault simply
tells the agent to look somewhere that no longer exists. This sweep is the
automated net over that whole class of mistake.
"""

import re

import pytest
from click.testing import CliRunner

from wolta.commands.init import init_command

# Directories that now hang off SYSTEM/ instead of the vault root.
MOVED_TO_SYSTEM = [
    "IDENTITY",
    "PREFERENCES",
    "WORK",
    "PROJECTS",
    "PERSONAL-SPACE",
    "KNOWLEDGE",
    "AI-SYSTEM",
    "TEMPLATES",
    "raw",
]

# One of those names used as a path segment, not already under a known space.
# The leading lookbehind rejects mid-path matches such as the `AI-SYSTEM/`
# inside `SYSTEM/AI-SYSTEM/`.
LEGACY_PATH = re.compile(
    r"(?<![\w/.-])(?<!SYSTEM/)(?<!HUMAN/)(" + "|".join(MOVED_TO_SYSTEM) + r")/"
)

# Tree diagrams express nesting rather than paths, so a bare `IDENTITY/` drawn
# underneath a `SYSTEM/` branch is correct and must not be reported.
TREE_GLYPHS = set("├└│")

# Ratchet left over from Fase 1. Fase 4 emptied it; it must stay empty.
# A new file with a legacy path fails test_no_unexpected_legacy_paths, and
# a stale entry here fails test_pending_list_has_no_stale_entries.
PENDING_PHASE_4 = {}


@pytest.fixture(scope="module")
def generated_vault(tmp_path_factory):
    root = tmp_path_factory.mktemp("sweep")
    result = CliRunner().invoke(init_command, ["--vault-path", str(root), "--name", "sweep"])
    assert result.exit_code == 0, result.output
    return root / "wolta-sweep"


@pytest.fixture(scope="module")
def legacy_hits(generated_vault):
    """Map every generated file to the legacy references it still contains."""
    hits = {}
    for path in sorted(generated_vault.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # not a text artifact; nothing to sweep
        offending = [
            line.strip()
            for line in text.splitlines()
            if not TREE_GLYPHS & set(line) and LEGACY_PATH.search(line)
        ]
        if offending:
            hits[path.relative_to(generated_vault).as_posix()] = offending
    return hits


def test_no_unexpected_legacy_paths(legacy_hits):
    unexpected = {rel: lines for rel, lines in legacy_hits.items() if rel not in PENDING_PHASE_4}
    if unexpected:
        report = "\n".join(
            f"  {rel} ({len(lines)}): {lines[0][:90]}" for rel, lines in unexpected.items()
        )
        pytest.fail(
            f"{len(unexpected)} generated file(s) still point at a pre-0.2.0 root path:\n"
            f"{report}\n"
            "Prefix the reference with SYSTEM/, or add the file to PENDING_PHASE_4 "
            "if its prose is genuinely still owned by Fase 4."
        )


def test_pending_list_has_no_stale_entries(legacy_hits):
    """Keep the ratchet honest: a file that came back clean must leave the list."""
    already_clean = sorted(set(PENDING_PHASE_4) - set(legacy_hits))
    assert not already_clean, (
        "These files no longer contain legacy paths, so they must be removed from "
        f"PENDING_PHASE_4 to keep the remaining debt accurate: {already_clean}"
    )


def test_the_sweep_would_actually_catch_a_regression():
    """Guard the guard: a detector that matches nothing would pass silently."""
    assert LEGACY_PATH.search("see `AI-SYSTEM/SKILLS/raw-ingest.md`")
    assert LEGACY_PATH.search("- [ ] Create notes in IDENTITY/ from P.ID.1")
    # ...and does not fire on paths that were already migrated.
    assert not LEGACY_PATH.search("see `SYSTEM/AI-SYSTEM/SKILLS/raw-ingest.md`")
    assert not LEGACY_PATH.search("the user's own `HUMAN/PROJECTS/` folder")


def test_claude_states_the_write_boundary(generated_vault):
    """4.1: the managed block is enough to know where the agent may write."""
    text = (generated_vault / "CLAUDE.md").read_text(encoding="utf-8")
    start = text.index('wolta:managed:start id="agent-instructions"')
    end = text.index('wolta:managed:end id="agent-instructions"')
    block = text[start:end]
    assert "## The two spaces of the vault" in block
    assert "Freely — add, edit, and remove as the work requires" in block
    assert "**Only** on an explicit instruction from the user" in block
    assert "`HUMAN/` is not part of the knowledge base." in block
    assert "The boundary is a policy, not a lock." in block


def test_design_and_readme_describe_the_two_spaces(generated_vault):
    """4.2: DESIGN.md and README.md name both spaces and the write rule."""
    design = (generated_vault / "SYSTEM" / "DESIGN.md").read_text(encoding="utf-8")
    assert "## 2. The two spaces" in design
    assert "Only when the user asks" in design
    assert "not part of the knowledge base" in design

    readme = (generated_vault / "README.md").read_text(encoding="utf-8")
    assert "## The two spaces" in readme
    assert "The agent only writes here when you ask it to" in readme
    assert "not part of the knowledge base" in readme
