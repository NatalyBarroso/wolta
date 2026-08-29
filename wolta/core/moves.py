"""Idempotent, reversible moves for structural migrations (v0.2.0 D-03/D-04).

Relocating a vault is done by renaming directories, not by copying files: a
rename is instant no matter how many notes are inside, preserves every
timestamp and attribute for free, and its inverse is another rename. Copying
hundreds of files would multiply by hundreds the chances of failing halfway.

Two properties make an interrupted run survivable. Each move is decided from
what is actually on disk, so a second run skips whatever is already done; and
each move is recorded in a plan whose inverse undoes exactly what happened.

The module refuses to guess. A source and a destination that both exist mean
either a previous run stopped midway or the user already had something by that
name, and merging the two blindly could destroy data, so that case raises
instead of picking a winner.
"""

import errno
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, List, Optional

RETRIES = 3
RETRY_DELAY = 0.5

# A lock held by a sync client or an open editor shows up as one of these.
_TRANSIENT_ERRNOS = frozenset({errno.EACCES, errno.EBUSY, errno.EPERM})


class MoveState(str, Enum):
    """Where a single move stands, per table 8.5 of the v0.2.0 plan."""

    PENDING = "pending"    # source is there, destination is free -> move it
    DONE = "done"          # already at the destination -> nothing to do
    CONFLICT = "conflict"  # both exist -> stop, a human has to look
    ABSENT = "absent"      # neither exists -> nothing to do


class MoveConflict(RuntimeError):
    """Source and destination both exist; resolving it automatically is unsafe."""


class MoveLocked(RuntimeError):
    """The path stayed locked after every retry."""


@dataclass(frozen=True)
class Move:
    """A rename expressed in vault-relative paths."""

    src: str
    dst: str

    def inverse(self) -> "Move":
        return Move(src=self.dst, dst=self.src)

    def __str__(self) -> str:
        return f"{self.src} -> {self.dst}"


@dataclass
class MovePlan:
    """The moves attempted so far, in order, so they can be walked backwards."""

    moves: List[Move] = field(default_factory=list)

    def record(self, move: Move) -> None:
        self.moves.append(move)

    def inverse(self) -> List[Move]:
        """The moves that undo this plan, last one first."""
        return [move.inverse() for move in reversed(self.moves)]

    def __iter__(self):
        return iter(self.moves)

    def __len__(self) -> int:
        return len(self.moves)


def state(vault: Path, move: Move) -> MoveState:
    """Classify a move from what is on disk right now."""
    vault = Path(vault)
    src_exists = (vault / move.src).exists()
    dst_exists = (vault / move.dst).exists()

    if src_exists:
        return MoveState.CONFLICT if dst_exists else MoveState.PENDING
    return MoveState.DONE if dst_exists else MoveState.ABSENT


def conflicts(vault: Path, moves: Iterable[Move]) -> List[Move]:
    """The moves that cannot proceed because both ends exist."""
    return [move for move in moves if state(vault, move) is MoveState.CONFLICT]


def apply(
    vault: Path,
    move: Move,
    *,
    plan: Optional[MovePlan] = None,
    dry_run: bool = False,
    retries: int = RETRIES,
    delay: float = RETRY_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> MoveState:
    """Perform one move if it is still pending, and report the state found.

    Returns the state that was detected, so a caller can tell a move that was
    carried out (`PENDING`) from one that had already happened (`DONE`) or that
    had nothing to move (`ABSENT`). Raises on `CONFLICT`.
    """
    vault = Path(vault)
    detected = state(vault, move)

    if detected is MoveState.CONFLICT:
        raise MoveConflict(
            f"both ends of '{move}' exist. Either a previous migration stopped "
            f"midway or '{move.dst}' was created independently; resolve it by "
            f"hand before retrying."
        )
    if detected is not MoveState.PENDING or dry_run:
        return detected

    src = vault / move.src
    dst = vault / move.dst
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Recorded before the rename rather than after. Undoing a move that never
    # happened is a no-op under the same state rule, while forgetting one that
    # did happen would strand the vault half migrated with no way back.
    if plan is not None:
        plan.record(move)

    _rename_with_retry(src, dst, retries=retries, delay=delay, sleep=sleep)
    return detected


def apply_all(
    vault: Path,
    moves: Iterable[Move],
    *,
    plan: Optional[MovePlan] = None,
    dry_run: bool = False,
    retries: int = RETRIES,
    delay: float = RETRY_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> List[MoveState]:
    """Perform a batch, refusing to start if any move in it conflicts.

    Every conflict is found before the first rename, so a batch that cannot
    complete never gets the chance to half-complete.
    """
    moves = list(moves)
    blocked = conflicts(vault, moves)
    if blocked:
        listed = ", ".join(f"'{move}'" for move in blocked)
        raise MoveConflict(
            f"{len(blocked)} move(s) have both ends present and were not "
            f"attempted: {listed}. Resolve them by hand before retrying."
        )

    return [
        apply(vault, move, plan=plan, dry_run=dry_run,
              retries=retries, delay=delay, sleep=sleep)
        for move in moves
    ]


def undo(
    vault: Path,
    plan: MovePlan,
    *,
    retries: int = RETRIES,
    delay: float = RETRY_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> List[MoveState]:
    """Walk a plan backwards, returning everything it moved to where it was.

    Safe to run against a plan that is ahead of reality: entries whose move
    never landed classify as `ABSENT` or `DONE` and are skipped.
    """
    return [
        apply(vault, move, retries=retries, delay=delay, sleep=sleep)
        for move in plan.inverse()
    ]


def remove_if_empty(vault: Path, rel: str) -> bool:
    """Delete a directory only if nothing is left in it. Returns whether it went.

    Undoing `create SYSTEM/, then move into it` is not finished while the empty
    `SYSTEM/` is still standing, and this keeps that cleanup from being
    open-coded as an `rmtree` that a stray file could turn destructive.
    """
    target = Path(vault) / rel
    if not target.is_dir() or any(target.iterdir()):
        return False
    target.rmdir()
    return True


def _rename_with_retry(
    src: Path,
    dst: Path,
    *,
    retries: int,
    delay: float,
    sleep: Callable[[float], None],
) -> None:
    last: Optional[OSError] = None
    for attempt in range(retries + 1):
        try:
            src.rename(dst)
            return
        except OSError as exc:
            # Only back off for the kind of failure that waiting can fix;
            # anything else is a real error and retrying just hides it.
            if exc.errno not in _TRANSIENT_ERRNOS:
                raise
            last = exc
            if attempt < retries:
                sleep(delay)

    raise MoveLocked(
        f"'{src}' was still locked after {retries + 1} attempts. A sync client "
        f"(OneDrive, Dropbox) or an open editor is probably holding it: pause "
        f"the sync, close the file and run the upgrade again."
    ) from last
