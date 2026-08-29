"""Console output must not crash on a terminal that cannot encode its glyphs."""

import os
import subprocess
import sys

import pytest

from wolta.utils import console

# What a redirected stdout uses on Windows, and where the original bug appeared.
NARROW = "cp1252"


def test_utf8_keeps_the_glyphs():
    assert console.safe("✓ done → next", encoding="utf-8") == "✓ done → next"


def test_narrow_encoding_falls_back_to_ascii():
    assert console.safe("✓ done → next", encoding=NARROW) == "[OK] done -> next"


def test_ascii_is_untouched():
    assert console.safe("plain message", encoding=NARROW) == "plain message"


def test_unmapped_glyph_degrades_instead_of_raising():
    # No entry in the fallback table, so it cannot be translated -- but the
    # point is that it must not propagate a UnicodeEncodeError.
    result = console.safe("progress ▓▓░", encoding=NARROW)
    result.encode(NARROW)  # the whole promise: the caller can write this out


def test_unknown_encoding_is_left_alone():
    assert console.safe("✓ done", encoding="not-a-real-codec") == "✓ done"


@pytest.mark.parametrize("command", ["init", "upgrade"])
def test_commands_exit_zero_when_stdout_cannot_encode_the_glyphs(tmp_path, command):
    """The original bug: the vault got created, then the success message crashed.

    Runs in a subprocess because the failure lives in the real stdout encoding,
    which CliRunner replaces with a buffer of its own.
    """
    env = {**os.environ, "PYTHONIOENCODING": NARROW}
    vault = tmp_path / "wolta-demo"

    init = subprocess.run(
        [sys.executable, "-m", "wolta.cli", "init",
         "--vault-path", str(tmp_path), "--name", "demo"],
        capture_output=True,
        env=env,
    )
    assert init.returncode == 0, init.stderr.decode(NARROW, errors="replace")
    assert (vault / "SYSTEM").is_dir()

    if command == "upgrade":
        # Exercises the "already up to date" message, which also carries a glyph.
        up = subprocess.run(
            [sys.executable, "-m", "wolta.cli", "upgrade", "--vault-path", str(vault)],
            capture_output=True,
            env=env,
        )
        assert up.returncode == 0, up.stderr.decode(NARROW, errors="replace")
