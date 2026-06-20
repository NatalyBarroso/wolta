"""Whole-change snapshot and rollback for the upgrade runner (T2.3.1 D-13).

Before applying migrations, the runner copies only the files that the pending
migrations will touch (plus `.wolta/version`) into `.wolta/backups/<timestamp>/`,
together with a manifest recording which of those files already existed. If a
migration fails midway, `rollback()` restores modified files and removes files
that the migration had newly created.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

VERSION_REL = ".wolta/version"
MANIFEST_NAME = "_snapshot_manifest.json"


def create_snapshot(vault: Path, files_to_change: List[str]) -> Path:
    """Snapshot the change-set and return the snapshot directory path."""
    vault = Path(vault)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    snap = vault / ".wolta" / "backups" / timestamp
    snap.mkdir(parents=True, exist_ok=True)

    tracked = list(dict.fromkeys(list(files_to_change) + [VERSION_REL]))
    existed = []
    for rel in tracked:
        src = vault / rel
        if src.exists():
            existed.append(rel)
            dst = snap / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    (snap / MANIFEST_NAME).write_text(
        json.dumps({"tracked": tracked, "existed": existed}, indent=2),
        encoding="utf-8",
    )
    return snap


def rollback(vault: Path, snapshot_dir: Path) -> None:
    """Restore the vault to its pre-apply state from a snapshot.

    Files that existed are restored from the snapshot; files that were created
    by a (failed) migration are deleted.
    """
    vault = Path(vault)
    snap = Path(snapshot_dir)
    manifest = json.loads((snap / MANIFEST_NAME).read_text(encoding="utf-8"))
    existed = set(manifest["existed"])

    for rel in manifest["tracked"]:
        dst = vault / rel
        if rel in existed:
            src = snap / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            # the migration created this file; undo the creation
            if dst.exists():
                dst.unlink()
