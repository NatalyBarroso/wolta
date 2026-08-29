"""Console output that survives a non-UTF-8 stdout.

On Windows `sys.stdout` is UTF-8 while attached to a console, but falls back to
the ANSI code page (cp1252) the moment the output is piped or redirected. The
check mark and arrow used in status messages have no cp1252 equivalent, so
writing them raised UnicodeEncodeError and made `wolta init` exit non-zero even
though the vault had been created correctly.

Forcing UTF-8 on the stream would trade the crash for mojibake in whatever reads
the pipe, so instead we emit only what the stream can encode and fall back to
ASCII when it cannot.
"""

import sys
from typing import Any, Optional

import click

# Glyphs used in status messages, with a stand-in for narrow encodings.
_FALLBACKS = {
    "✓": "[OK]",
    "→": "->",
    "—": "-",
}


def safe(text: str, encoding: Optional[str] = None) -> str:
    """Return `text` with anything `encoding` cannot represent replaced.

    Defaults to the encoding of the current stdout. It is a parameter so that
    callers -- tests above all -- can ask about a specific encoding without
    reassigning `sys.stdout`, which pytest resets between phases anyway.
    """
    if encoding is None:
        encoding = getattr(sys.stdout, "encoding", None)
    if not encoding:
        return text
    try:
        text.encode(encoding)
        return text
    except LookupError:  # unknown encoding name; not our problem to guess
        return text
    except UnicodeEncodeError:
        pass

    for glyph, fallback in _FALLBACKS.items():
        text = text.replace(glyph, fallback)
    # Whatever is still unrepresentable degrades instead of raising.
    return text.encode(encoding, errors="replace").decode(encoding)


def echo(message: Any = None, **kwargs: Any) -> None:
    """`click.echo` that never fails on an unencodable character."""
    if isinstance(message, str):
        message = safe(message)
    click.echo(message, **kwargs)
