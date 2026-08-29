"""Migration contract for the Wolta upgrade system (T2.3.3).

A migration takes the vault from the previous schema state to its
`target_version`. Migrations never write to the vault directly: they go
through the helpers carried in `MigrationContext`, which enforce the
managed/user-owned classification (T2.3.1) and, from v0.2.0, the reversible
move primitive (D-03/D-04).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from wolta.core import moves
from wolta.core import snapshot as core_snapshot
from wolta.core.moves import Move, MovePlan, MoveState


@dataclass
class MigrationContext:
    """Everything a migration needs to apply itself safely.

    Attributes:
        vault: Path to the vault root.
        manifest: the `wolta.core.manifest` module (file classification).
        sections: the `wolta.core.sections` module (managed-section engine).
        files: the `wolta.core.files` module (checksum-guarded writes).
        dry_run: when True, no file is modified.
        snapshot_dir: the runner's snapshot for this apply; moves are
            persisted there so rollback can find them after a failure.
        plan: the moves recorded so far, used to re-key checksums.
    """

    vault: Path
    manifest: Any
    sections: Any
    files: Any
    dry_run: bool = False
    snapshot_dir: Optional[Path] = None
    plan: MovePlan = field(default_factory=MovePlan)

    def move(self, src: str, dst: str) -> MoveState:
        """Relocate a vault-relative path through the reversible primitive.

        The filesystem is never touched from the migration: a rename, a
        no-op, or a conflict all go through here so the plan and the
        snapshot stay aligned with what actually happened.
        """
        relocation = Move(src, dst)
        # Persist only a move that is about to happen. Recording a DONE or
        # ABSENT entry would make rollback invert something this run never
        # did -- and invert of DONE is a live rename the other way.
        if (
            not self.dry_run
            and self.snapshot_dir is not None
            and moves.state(self.vault, relocation) is MoveState.PENDING
        ):
            core_snapshot.record_move(self.vault, self.snapshot_dir, relocation)
        return moves.apply(
            self.vault, relocation, plan=self.plan, dry_run=self.dry_run
        )

    def rekey_checksums(self) -> dict:
        """Point recorded checksums at the paths this context has moved."""
        return self.files.rekey_checksums(
            self.vault, self.plan, dry_run=self.dry_run
        )


class Migration:
    """Base class for a single schema migration.

    Subclasses set `target_version` (and optionally `min_version`) and
    implement `up()`. `up()` must be idempotent: running it on a vault that
    already has the change applied must not modify anything.
    """

    target_version: str = ""
    min_version: str = "0.0.0"

    def up(self, ctx: MigrationContext) -> List[str]:
        """Apply the migration. Return the list of relative paths modified."""
        raise NotImplementedError

    def planned_moves(self, ctx: MigrationContext) -> List[Move]:
        """The relocations `up()` would still perform on `ctx.vault`.

        Reported separately from `up()`'s return value because the two answer
        different questions. That list is the set of files whose *bytes* change
        and is what the runner snapshots; a rename changes no bytes, so putting
        moves in there would have the runner back up paths for no reason. This
        is what `--dry-run` needs in order to show the user where their notes
        are about to go.
        """
        return []
