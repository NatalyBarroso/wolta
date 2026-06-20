"""Unit tests for the managed-section marker engine (T2.3.3)."""

import pytest

from wolta.core.sections import MarkerError, replace_block, validate_markers

DOC = (
    "# Title\n\n"
    '<!-- wolta:managed:start id="agent-instructions" v="0.1.0" -->\n'
    "system body\n"
    '<!-- wolta:managed:end id="agent-instructions" -->\n\n'
    "## Notas del usuario\n\nuser content\n"
)


def test_validate_ok():
    validate_markers(DOC)  # no raise


def test_validate_simple_form_ok():
    validate_markers("a\n<!-- wolta-managed:start -->\nx\n<!-- wolta-managed:end -->\n")


def test_validate_unclosed_raises():
    with pytest.raises(MarkerError):
        validate_markers('<!-- wolta:managed:start id="x" -->\nbody\n')


def test_validate_unbalanced_end_raises():
    with pytest.raises(MarkerError):
        validate_markers('body\n<!-- wolta:managed:end id="x" -->\n')


def test_replace_preserves_outside_content():
    out = replace_block(DOC, "agent-instructions", "NEW BODY")
    assert "NEW BODY" in out
    assert "system body" not in out
    # everything outside the block is preserved
    assert "# Title" in out
    assert "## Notas del usuario" in out
    assert "user content" in out
    # markers remain
    assert out.count('wolta:managed:start id="agent-instructions"') == 1
    assert out.count('wolta:managed:end id="agent-instructions"') == 1


def test_replace_is_idempotent():
    once = replace_block(DOC, "agent-instructions", "NEW BODY")
    twice = replace_block(once, "agent-instructions", "NEW BODY")
    assert once == twice


def test_replace_missing_block_appends():
    out = replace_block("# Only title\n", "vault-spec", "spec body", version="0.2.0")
    assert 'wolta:managed:start id="vault-spec" v="0.2.0"' in out
    assert "spec body" in out
    assert out.count('wolta:managed:end id="vault-spec"') == 1


def test_replace_start_without_end_raises():
    broken = '<!-- wolta:managed:start id="x" -->\nbody\n'
    with pytest.raises(MarkerError):
        replace_block(broken, "x", "new")
