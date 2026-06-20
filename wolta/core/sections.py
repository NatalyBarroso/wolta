"""Managed-section marker engine (T2.3.1 D-05).

Managed sections are delimited by keyed markers:

    <!-- wolta:managed:start id="agent-instructions" v="0.1.0" -->
    ...managed content...
    <!-- wolta:managed:end id="agent-instructions" -->

The simple legacy form `<!-- wolta-managed:start -->` / `<!-- wolta-managed:end -->`
is accepted for reading as id="default". Replacement only ever touches the
content between a start/end pair; everything outside is preserved verbatim.
"""

import re
from typing import Iterator, Tuple

DEFAULT_ID = "default"


class MarkerError(Exception):
    """Raised when managed-section markers are unbalanced or malformed."""


# Combined token scanner: keyed start/end, plus simple legacy forms.
_TOKEN = re.compile(
    r'<!--\s*wolta:managed:(?P<kkind>start|end)\s+id="(?P<id>[\w-]+)"'
    r'(?:\s+v="[^"]*")?\s*-->'
    r'|<!--\s*wolta-managed:(?P<skind>start|end)(?:\s+[^>]*?)?\s*-->'
)


def _iter_markers(text: str) -> Iterator[Tuple[str, str, int, int]]:
    """Yield (kind, block_id, start_offset, end_offset) for each marker, in order."""
    for m in _TOKEN.finditer(text):
        if m.group("kkind"):
            yield m.group("kkind"), m.group("id"), m.start(), m.end()
        else:
            yield m.group("skind"), DEFAULT_ID, m.start(), m.end()


def validate_markers(text: str) -> None:
    """Validate that every start has a matching end (proper LIFO pairing).

    Raises MarkerError on an unclosed start, an end without a matching open,
    or a duplicated/overlapping open id.
    """
    stack = []
    for kind, block_id, _, _ in _iter_markers(text):
        if kind == "start":
            if block_id in stack:
                raise MarkerError(f"duplicate/nested managed block id={block_id!r}")
            stack.append(block_id)
        else:  # end
            if not stack or stack[-1] != block_id:
                raise MarkerError(f"unbalanced managed:end id={block_id!r}")
            stack.pop()
    if stack:
        raise MarkerError(f"unclosed managed block id={stack[-1]!r}")


def _keyed_start(block_id: str) -> re.Pattern:
    return re.compile(
        r'<!--\s*wolta:managed:start\s+id="' + re.escape(block_id) + r'"'
        r'(?:\s+v="[^"]*")?\s*-->'
    )


def _keyed_end(block_id: str) -> re.Pattern:
    return re.compile(
        r'<!--\s*wolta:managed:end\s+id="' + re.escape(block_id) + r'"\s*-->'
    )


def replace_block(
    text: str,
    block_id: str,
    new_body: str,
    *,
    version: str = "",
    anchor: str = "eof",
) -> str:
    """Replace the body of the managed block `block_id`, preserving the markers
    and everything outside them. Idempotent.

    If the block does not exist, a new one is appended at `anchor` ("eof").
    Raises MarkerError if a start is found without its matching end.
    """
    body = new_body.strip("\n")
    start = _keyed_start(block_id).search(text)
    if start:
        end = _keyed_end(block_id).search(text, start.end())
        if not end:
            raise MarkerError(f"managed:start id={block_id!r} has no matching end")
        start_marker = text[start.start():start.end()]
        end_marker = text[end.start():end.end()]
        return (
            text[: start.start()]
            + start_marker
            + "\n"
            + body
            + "\n"
            + end_marker
            + text[end.end():]
        )

    # Not present: append a fresh block.
    v_attr = f' v="{version}"' if version else ""
    block = (
        f'<!-- wolta:managed:start id="{block_id}"{v_attr} -->\n'
        f"{body}\n"
        f'<!-- wolta:managed:end id="{block_id}" -->\n'
    )
    if anchor == "eof":
        sep = "" if text.endswith("\n") else "\n"
        return text + sep + "\n" + block
    raise ValueError(f"unsupported anchor: {anchor!r}")
