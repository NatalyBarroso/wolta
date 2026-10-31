"""Whole-change snapshot and rollback for the upgrade runner (T2.3.1 D-13).

Before applying migrations, the runner copies only the files whose *content*
will change (plus `.wolta/version` and `.wolta/checksums.json`) into
`.wolta/backups/<timestamp>/`, together with a manifest recording which of
those files already existed.

Structural moves are a different kind of change (D-03/D-04): they do not
alter bytes, so they are not copied. Each one is appended to a plan in this
same snapshot directory *before* the rename, and `rollback()` undoes them
first, then restores the snapshotted files. That is the order in section 14.1
of the v0.2.0 plan: put everything back where it was, then put the original
bytes back on top.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from wolta.core import moves
from wolta.core.moves import Move, MovePlan

VERSION_REL = ".wolta/version"
CHECKSUMS_REL = ".wolta/checksums.json"
MANIFEST_NAME = "_snapshot_manifest.json"
MOVE_PLAN_NAME = "_move_plan.json"

# Always captured: the schema pointer and the managed-file guard. Losing either
# would make a rollback lie about the vault's version or silently disable the
# checksum backup on the next upgrade.
_ALWAYS_TRACKED = (VERSION_REL, CHECKSUMS_REL)


def create_snapshot(vault: Path, files_to_change: List[str]) -> Path:
    """Snapshot the content change-set and return the snapshot directory path."""
    vault = Path(vault)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    snap = vault / ".wolta" / "backups" / timestamp
    snap.mkdir(parents=True, exist_ok=True)

    tracked = list(dict.fromkeys(list(files_to_change) + list(_ALWAYS_TRACKED)))
    existed = []
    for rel in tracked:
        if _copy_file_into_snapshot(vault, snap, rel):
            existed.append(rel)

    (snap / MANIFEST_NAME).write_text(
        json.dumps({"tracked": tracked, "existed": existed}, indent=2),
        encoding="utf-8",
    )
    return snap


def record_move(vault: Path, snapshot_dir: Path, move: Move) -> None:
    """Persist `move` before it is applied, and keep a copy if it is a file.

    The plan is the source of truth for rollback, so it is written first.
    Undoing an entry that never landed is a no-op (table 8.5: neither end
    exists). Forgetting one that did land would leave the vault half moved.

    A directory move is undone by rename; there is nothing to copy. A file
    move can be followed by a rewrite, and after the inverse rename the file
    sits at `src` with the new content -- so the original bytes have to live
    in the snapshot or the restore would have nothing to put back.
    """
    vault = Path(vault)
    snap = Path(snapshot_dir)
    plan = _load_move_entries(snap)
    plan.append({"src": move.src, "dst": move.dst})
    (snap / MOVE_PLAN_NAME).write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8"
    )

    if (vault / move.src).is_file():
        _ensure_file_tracked(vault, snap, move.src)


def rollback(vault: Path, snapshot_dir: Path) -> None:
    """Restore the vault to its pre-apply state from a snapshot.

    Order (plan section 14.1): undo the recorded moves, then restore
    snapshotted files and delete files the migration had newly created.
    """
    vault = Path(vault)
    snap = Path(snapshot_dir)

    _undo_moves(vault, snap)
    _restore_files(vault, snap)


def _undo_moves(vault: Path, snap: Path) -> None:
    entries = _load_move_entries(snap)
    if not entries:
        return
    plan = MovePlan()
    for item in entries:
        plan.record(Move(item["src"], item["dst"]))
    moves.undo(vault, plan)
    for item in entries:
        _remove_empty_ancestors(vault, item["dst"])


def _restore_files(vault: Path, snap: Path) -> None:
    manifest = json.loads((snap / MANIFEST_NAME).read_text(encoding="utf-8"))
    existed = set(manifest["existed"])

    for rel in manifest["tracked"]:
        dst = vault / rel
        if rel in existed:
            src = snap / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif dst.exists() and dst.is_file():
            dst.unlink()


def _copy_file_into_snapshot(vault: Path, snap: Path, rel: str) -> bool:
    """Copy `rel` into the snapshot if it is a file. Returns whether it existed.

    Directories are skipped on purpose (D-04): a structural move is reversed
    by rename, not by copying the tree into `.wolta/backups/`.
    """
    src = vault / rel
    if not src.is_file():
        return False
    dst = snap / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _ensure_file_tracked(vault: Path, snap: Path, rel: str) -> None:
    """Add an existing file to the snapshot manifest if it is not there yet."""
    manifest_path = snap / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if rel not in manifest["tracked"]:
        manifest["tracked"].append(rel)
    if rel not in manifest["existed"] and _copy_file_into_snapshot(vault, snap, rel):
        manifest["existed"].append(rel)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def _load_move_entries(snap: Path) -> List[dict]:
    path = snap / MOVE_PLAN_NAME
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _remove_empty_ancestors(vault: Path, rel: str) -> None:
    """Drop empty directories left behind after undoing a move into `rel`.

    The destination itself is usually already gone (it was renamed back), so
    a missing path is skipped rather than treated as "not empty".
    """
    parts = Path(rel).parts
    for length in range(len(parts), 0, -1):
        candidate = "/".join(parts[:length])
        if not (vault / candidate).exists():
            continue
        if not moves.remove_if_empty(vault, candidate):
            break
