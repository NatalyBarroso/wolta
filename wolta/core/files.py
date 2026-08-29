"""Checksum-guarded writes and backups for managed files (T2.3.1 D-04).

A managed full-file may be overwritten on upgrade, but never silently over a
user's edit: if the on-disk checksum no longer matches the one wolta last
wrote, the current file is copied to `<file>.bak` before being replaced.
Checksums live in `.wolta/checksums.json`, keyed by vault-relative path.

Because the key is the path, a structural migration that relocates files has to
re-key the store along with them (`rekey_checksums`); see the note there for
what happens if it does not.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, Iterable, Optional


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _checksums_path(vault: Path) -> Path:
    return Path(vault) / ".wolta" / "checksums.json"


def load_checksums(vault: Path) -> Dict[str, str]:
    path = _checksums_path(vault)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_checksums(vault: Path, sums: Dict[str, str]) -> None:
    path = _checksums_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(sums, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_managed(
    vault: Path, rel: str, content: str, *, dry_run: bool = False
) -> Optional[str]:
    """Write a managed full-file, guarding against clobbering user edits.

    Returns `rel` if the file changed, None if the content was already current.
    On a checksum mismatch (the user edited a managed file) the current file is
    backed up to `<file>.bak` before being overwritten. Respects `dry_run`.
    """
    vault = Path(vault)
    target = vault / rel
    new_sum = sha256_text(content)

    if target.exists() and sha256(target) == new_sum:
        return None  # already current; idempotent no-op

    if dry_run:
        return rel

    sums = load_checksums(vault)
    if target.exists():
        recorded = sums.get(rel)
        on_disk = sha256(target)
        if recorded is not None and on_disk != recorded:
            backup = target.parent / (target.name + ".bak")
            shutil.copy2(target, backup)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    sums[rel] = new_sum
    save_checksums(vault, sums)
    return rel


def seed_checksums(vault: Path, rel_paths) -> None:
    """Record current checksums for the given managed files (used at init)."""
    vault = Path(vault)
    sums = load_checksums(vault)
    for rel in rel_paths:
        target = vault / rel
        if target.exists():
            sums[rel] = sha256(target)
    save_checksums(vault, sums)


def rekey_checksums(
    vault: Path, moves: Iterable, *, dry_run: bool = False
) -> Dict[str, str]:
    """Point every recorded checksum at the path its file now has.

    Takes the moves that were applied -- anything with `.src` and `.dst`
    vault-relative attributes, such as `wolta.core.moves.Move` -- and returns
    the `{old key: new key}` it rewrote.

    This is not bookkeeping, it is the other half of the move. A managed file
    whose key is left behind looks unrecorded to `write_managed`, and an
    unrecorded file is overwritten with no `.bak`: the guard against clobbering
    a user's edit turns itself off, silently, at the next upgrade.

    The recorded value never changes. A rename does not touch content, so the
    checksum that was true before the move is still true after it.
    """
    sums = load_checksums(vault)
    moves = list(moves)

    renames = {}
    for key in sums:
        for move in moves:
            relocated = _relocate(key, move)
            if relocated is not None and relocated != key:
                renames[key] = relocated
                break

    if not renames or dry_run:
        return renames

    for old, new in renames.items():
        value = sums.pop(old)
        # If the destination key is already there, an earlier run of this same
        # rekey wrote it -- two genuinely different files cannot reach here,
        # since the move primitive refuses to run when both ends exist. Keeping
        # what is already recorded is the conservative half of that choice: a
        # stale value costs at most one needless `.bak`, while dropping the key
        # would cost the backup itself.
        sums.setdefault(new, value)

    save_checksums(vault, sums)
    return renames


def _relocate(key: str, move) -> Optional[str]:
    """The key's path after `move`, or None if the move does not cover it."""
    key = key.replace("\\", "/")
    if key == move.src:
        return move.dst
    # Compared with the separator attached so that moving `WORK` leaves a
    # sibling like `WORK-ARCHIVE/notes.md` alone.
    prefix = move.src + "/"
    if key.startswith(prefix):
        return f"{move.dst}/{key[len(prefix):]}"
    return None
