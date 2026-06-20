"""Checksum-guarded writes and backups for managed files (T2.3.1 D-04).

A managed full-file may be overwritten on upgrade, but never silently over a
user's edit: if the on-disk checksum no longer matches the one wolta last
wrote, the current file is copied to `<file>.bak` before being replaced.
Checksums live in `.wolta/checksums.json`.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, Optional


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
