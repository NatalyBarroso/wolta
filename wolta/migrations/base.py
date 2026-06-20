"""Migration contract for the Wolta upgrade system (T2.3.3).

A migration takes the vault from the previous schema state to its
`target_version`. Migrations never write to the vault directly: they go
through the helpers carried in `MigrationContext`, which enforce the
managed/user-owned classification (T2.3.1).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class MigrationContext:
    """Everything a migration needs to apply itself safely.

    Attributes:
        vault: Path to the vault root.
        manifest: the `wolta.core.manifest` module (file classification).
        sections: the `wolta.core.sections` module (managed-section engine).
        files: the `wolta.core.files` module (checksum-guarded writes).
        dry_run: when True, no file is modified.
    """

    vault: Path
    manifest: Any
    sections: Any
    files: Any
    dry_run: bool = False


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
