"""Migration v0.1.0 -> v0.2.0: split the vault into HUMAN/ and SYSTEM/.

Everything `wolta init` used to drop at the vault root moves under `SYSTEM/`,
an empty `HUMAN/` is created next to it, and the documents that describe the
tree are rewritten so the vault stops telling the agent to look at paths that
no longer exist.

Three properties hold this together:

*Nothing is copied.* Each category is relocated with a single rename through
the reversible primitive (D-03/D-04), so a vault with ten thousand notes costs
the same as one with ten and every timestamp survives.

*Nothing is guessed.* If a source and its destination both exist, the vault is
either half migrated or the user already had a folder by that name. Either way
a human has to decide, so the pre-flight stops before the first rename.

*Nothing is taken on trust.* The bytes of every file are hashed before the
moves and again after them, and a single mismatch aborts the migration so the
runner rolls the whole thing back (task 3.4).

Self-contained and immutable (D-02): the 0.2.0 documents are frozen under
`data_v0_2_0/` and do not depend on `structure.py`. A migration is a historical
artifact; its result must not change as the tool evolves.
"""

from pathlib import Path
from typing import Dict, List, Tuple

from wolta.core import moves as core_moves
from wolta.core.layout import HUMAN_ROOT, SYSTEM_ROOT, system
from wolta.core.moves import Move, MoveState
from wolta.migrations.base import Migration, MigrationContext

_DATA = Path(__file__).parent / "data_v0_2_0"
_VERSION = "0.2.0"

# Everything the pre-0.2.0 CLI wrote at the root that now belongs to the agent
# space. The three root artifacts of D-08 (`.wolta/`, `CLAUDE.md`,
# `README.md`) are deliberately absent: they stay where they are.
_RELOCATED = (
    "IDENTITY",
    "PREFERENCES",
    "WORK",
    "PROJECTS",
    "PERSONAL-SPACE",
    "KNOWLEDGE",
    "AI-SYSTEM",
    "TEMPLATES",
    "raw",
    "DESIGN.md",
)

MOVES: Tuple[Move, ...] = tuple(Move(rel, system(rel)) for rel in _RELOCATED)

_GITKEEP = f"{HUMAN_ROOT}/.gitkeep"

# Managed full-files rewritten from the frozen content, keyed by where they
# live once the moves are done.
_MANAGED_FILES: Dict[str, str] = {
    "README.md": "README.md",
    system("raw/README.md"): "raw-readme.md",
    system("AI-SYSTEM/SKILLS/bootstrap-generate.md"): "bootstrap-generate.md",
    system("AI-SYSTEM/SKILLS/raw-ingest.md"): "raw-ingest.md",
    system("AI-SYSTEM/SKILLS/INGEST-PROTOCOL.md"): "INGEST-PROTOCOL.md",
    system("AI-SYSTEM/SKILLS/source-files.md"): "source-files.md",
    system("TEMPLATES/template-source-adapter.md"): "template-source-adapter.md",
}

# Managed sections: (destination, block id, frozen body). Only the text
# between the markers is replaced; whatever the user wrote outside them stays.
_MANAGED_SECTIONS: Tuple[Tuple[str, str, str], ...] = (
    ("CLAUDE.md", "agent-instructions", "claude-agent-instructions.md"),
    (system("DESIGN.md"), "vault-spec", "design-vault-spec.md"),
)

# Left out of the integrity check. An upgrade is supposed to rewrite wolta's
# own state, and the snapshot it takes lives in here too; hashing any of it
# would report the migration doing its job as corruption.
_VOLATILE = (".wolta/",)


class PreflightError(RuntimeError):
    """The vault is not in a state this migration can act on safely."""


class IntegrityError(RuntimeError):
    """A file's content did not survive the restructuring unchanged."""


def _data(name: str) -> str:
    return (_DATA / name).read_text(encoding="utf-8")


class MigrationV020(Migration):
    target_version = _VERSION
    min_version = "0.1.0"

    def planned_moves(self, ctx: MigrationContext) -> List[Move]:
        return [
            move
            for move in MOVES
            if core_moves.state(ctx.vault, move) is MoveState.PENDING
        ]

    def up(self, ctx: MigrationContext) -> List[str]:
        self._preflight(ctx)

        # Taken before the first rename and compared against the same census
        # afterwards. Under --dry-run there is nothing to compare, and hashing
        # a whole vault to throw the result away would make the preview slow
        # for no reason.
        baseline = {} if ctx.dry_run else self._census(ctx)

        changed: List[str] = self._create_human_space(ctx)
        self._relocate_into_system(ctx)
        ctx.rekey_checksums()
        changed += self._refresh_documents(ctx)

        if not ctx.dry_run:
            self._verify(ctx, baseline, changed)
        return changed

    # ---------------------------------------------------------------- 3.2

    def _preflight(self, ctx: MigrationContext) -> None:
        """Refuse to start on a vault this migration cannot finish.

        Runs first in both passes, and the dry pass happens before the runner
        takes its snapshot — so an abort here is an abort with the vault
        untouched, which is the whole point of checking.
        """
        for rel in (HUMAN_ROOT, SYSTEM_ROOT):
            path = ctx.vault / rel
            if path.exists() and not path.is_dir():
                raise PreflightError(
                    f"'{rel}' already exists and is not a directory. The 0.2.0 "
                    f"layout needs that name for a folder: rename the file and "
                    f"run the upgrade again."
                )

        blocked = core_moves.conflicts(ctx.vault, MOVES)
        if blocked:
            listed = "; ".join(f"'{move}'" for move in blocked)
            raise PreflightError(
                f"{len(blocked)} relocation(s) have both ends on disk and were "
                f"not attempted: {listed}. Either an earlier upgrade stopped "
                f"midway or the vault already had something by that name. "
                f"Merge or remove one side by hand and try again."
            )

        # A folder the user created themselves is not ours to merge into.
        # Conflicts are already handled above; an interrupted run leaves
        # destinations under SYSTEM/, which table 8.5 classifies as DONE.
        human = ctx.vault / HUMAN_ROOT
        if human.is_dir():
            extras = [p.name for p in human.iterdir() if p.name != ".gitkeep"]
            if extras:
                raise PreflightError(
                    f"'{HUMAN_ROOT}/' already has content ({extras[0]}). "
                    f"That folder is the user's space and this upgrade will "
                    f"not merge into it. Move those files out, then retry."
                )

        system = ctx.vault / SYSTEM_ROOT
        if system.is_dir() and any(system.iterdir()):
            resumed = any(
                core_moves.state(ctx.vault, move) is MoveState.DONE for move in MOVES
            )
            if not resumed:
                raise PreflightError(
                    f"'{SYSTEM_ROOT}/' already exists with content that this "
                    f"upgrade did not put there. Merging into it would mix "
                    f"two trees. Rename or empty it, then retry."
                )

    # ---------------------------------------------------------------- 3.3

    def _create_human_space(self, ctx: MigrationContext) -> List[str]:
        """Create the user space (D-06): a directory and nothing else.

        `HUMAN/` is the user's to shape, so wolta seeds no README and no
        categories in it. The `.gitkeep` is there only so the folder survives
        in a git-tracked vault.
        """
        keep = ctx.vault / _GITKEEP
        if keep.exists():
            return []
        if not ctx.dry_run:
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.touch()
        return [_GITKEEP]

    def _relocate_into_system(self, ctx: MigrationContext) -> None:
        """Move each root artifact into the agent space, one rename each.

        Goes through `ctx.move` rather than the batch helper so that every
        rename is written to the snapshot's plan before it happens; the batch
        pre-check it gives up is the conflict scan the pre-flight already ran.
        """
        for move in MOVES:
            ctx.move(move.src, move.dst)

    def _refresh_documents(self, ctx: MigrationContext) -> List[str]:
        changed: List[str] = []

        for rel, data_name in _MANAGED_FILES.items():
            target = self._where(ctx, rel)
            written = ctx.files.write_managed(
                ctx.vault, target, _data(data_name), dry_run=ctx.dry_run
            )
            if written:
                changed.append(target)

        for rel, block_id, data_name in _MANAGED_SECTIONS:
            changed += self._refresh_section(
                ctx, self._where(ctx, rel), block_id, _data(data_name)
            )

        return changed

    def _refresh_section(
        self, ctx: MigrationContext, rel: str, block_id: str, body: str
    ) -> List[str]:
        path = ctx.vault / rel
        if not path.is_file():
            # An upgrade migrates the vault it is given; it does not
            # reconstruct documents that `init` is responsible for creating.
            return []

        current = path.read_text(encoding="utf-8")
        updated = ctx.sections.replace_block(current, block_id, body, version=_VERSION)
        if updated == current:
            return []
        ctx.files.write_managed(ctx.vault, rel, updated, dry_run=ctx.dry_run)
        return [rel]

    def _where(self, ctx: MigrationContext, rel: str) -> str:
        """The path a document occupies right now, migrated or not.

        The dry pass runs before anything has moved, and its output is exactly
        what the runner snapshots. Reporting `SYSTEM/DESIGN.md` there would
        back up a path that does not exist yet and leave the real `DESIGN.md`
        with no copy to restore from.
        """
        if (ctx.vault / rel).exists():
            return rel
        for move in MOVES:
            legacy = core_moves.relocate(rel, move.inverse())
            if legacy is not None and (ctx.vault / legacy).exists():
                return legacy
        return rel

    # ---------------------------------------------------------------- 3.4

    def _census(self, ctx: MigrationContext) -> Dict[str, str]:
        return ctx.files.inventory(ctx.vault, skip=_VOLATILE)

    def _verify(
        self, ctx: MigrationContext, baseline: Dict[str, str], rewritten: List[str]
    ) -> None:
        """Confirm that the restructuring moved bytes without changing them.

        A rename cannot alter content, so every file hashed before the moves
        must be found afterwards, at its relocated path, with the same digest.
        The only exceptions are the documents this migration deliberately
        rewrote. Anything else is a bug in the move plan or a filesystem that
        did not do what it was asked, and both are reasons to roll back rather
        than to hand the user a vault that is quietly missing a note.
        """
        expected = {
            core_moves.relocate_all(rel, MOVES): digest
            for rel, digest in baseline.items()
        }
        for rel in rewritten:
            expected.pop(rel, None)
            expected.pop(core_moves.relocate_all(rel, MOVES), None)

        actual = self._census(ctx)

        missing = sorted(rel for rel in expected if rel not in actual)
        altered = sorted(
            rel
            for rel, digest in expected.items()
            if rel in actual and actual[rel] != digest
        )
        if not missing and not altered:
            return

        raise IntegrityError(
            "the restructuring did not preserve the vault's content — "
            + "; ".join(_describe(missing, "missing") + _describe(altered, "altered"))
        )


def _describe(paths: List[str], label: str) -> List[str]:
    if not paths:
        return []
    shown = ", ".join(paths[:5])
    more = f" (+{len(paths) - 5} more)" if len(paths) > 5 else ""
    return [f"{len(paths)} file(s) {label}: {shown}{more}"]
