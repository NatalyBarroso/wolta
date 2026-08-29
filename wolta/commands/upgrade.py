"""`wolta upgrade` command (T2.3.3).

Upgrades an existing vault to the latest (or a target) schema version,
applying pending migrations sequentially in four phases: pre-flight,
snapshot, apply, commit/rollback (T2.3.1 D-12). No migration is applied
under --dry-run, and any failure mid-apply rolls the vault back.
"""

import os
from pathlib import Path
from typing import List, Optional

import click
from packaging.version import Version

from wolta import __version__
from wolta.core import files as core_files
from wolta.core import manifest as core_manifest
from wolta.core import sections as core_sections
from wolta.core import snapshot as core_snapshot
from wolta.core.layout import SYSTEM_ROOT
from wolta.migrations import MIN_UPGRADABLE_VERSION, pending
from wolta.migrations.base import MigrationContext
from wolta.utils.console import echo
from wolta.utils.version_manager import VersionManager

# Folder names that give away a file-sync client. A structural migration is
# the one operation these handle worst: renaming a whole tree while an upload
# of the old path is still in flight is how conflicted copies are born.
_SYNC_HINTS = {
    "onedrive": "OneDrive",
    "dropbox": "Dropbox",
    "com~apple~clouddocs": "iCloud Drive",
    "icloud drive": "iCloud Drive",
    "google drive": "Google Drive",
    "googledrive": "Google Drive",
}


def _is_vault(path: Path) -> bool:
    return (path / ".wolta").exists() or (path / "CLAUDE.md").exists()


def _pre_split(rel: str) -> Optional[str]:
    """Where `rel` lived before the 0.2.0 HUMAN/SYSTEM split, if it moved."""
    prefix = f"{SYSTEM_ROOT}/"
    return rel[len(prefix):] if rel.startswith(prefix) else None


def _managed_section_files(vault: Path) -> List[str]:
    """Managed-section files, found wherever this vault currently keeps them.

    The manifest describes the 0.2.0 layout, but the vault being upgraded is
    by definition still on an older one — a 0.1.0 vault has `DESIGN.md` at the
    root, not under `SYSTEM/`. Checking only the manifest path would skip it,
    and skipping it means corrupt markers surface mid-apply instead of here,
    where nothing has been touched yet.
    """
    found: List[str] = []
    for rel, pol in core_manifest.MANIFEST.items():
        if pol != core_manifest.Policy.MANAGED_SECTION:
            continue
        legacy = _pre_split(rel)
        for candidate in (rel, legacy):
            if candidate and (vault / candidate).is_file():
                found.append(candidate)
                break
    return found


def _sync_client(vault: Path) -> Optional[str]:
    """Name the sync client whose folder holds this vault, if any.

    Only a warning: pausing someone else's client is not the CLI's business,
    and a vault in OneDrive is a normal, supported setup. But a heads-up
    before ten directory renames is worth far more than a diagnosis after.
    """
    haystack = str(Path(vault).resolve()).replace("\\", "/").lower()
    for needle, name in _SYNC_HINTS.items():
        if f"/{needle}" in haystack:
            return name
    return None


def _make_context(vault: Path, dry_run: bool, snapshot_dir=None) -> MigrationContext:
    return MigrationContext(
        vault=vault,
        manifest=core_manifest,
        sections=core_sections,
        files=core_files,
        dry_run=dry_run,
        snapshot_dir=snapshot_dir,
    )


@click.command(name="upgrade")
@click.option(
    "--vault-path",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to the vault (default: current directory).",
)
@click.option("--dry-run", is_flag=True, help="Show what would change without applying it.")
@click.option(
    "--to-version",
    default=None,
    help="Target schema version (default: the latest the CLI knows).",
)
def upgrade_command(vault_path, dry_run, to_version) -> None:
    """Upgrade an existing vault to the latest (or a target) schema version."""
    vault = Path(vault_path or os.getcwd())

    if not _is_vault(vault):
        echo(
            click.style(
                f"Error: {vault} does not look like a wolta vault (missing .wolta/ or CLAUDE.md).",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    vm = VersionManager(str(vault))
    current = vm.get_vault_version()
    target = to_version or __version__

    # ---------------- Phase 1: pre-flight (without modifying anything) ----------------
    if Version(target) > Version(__version__):
        echo(
            click.style(
                f"Error: --to-version {target} is greater than the CLI version "
                f"({__version__}). Update wolta-cli to migrate to that version.",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    if Version(current) < Version(MIN_UPGRADABLE_VERSION):
        echo(
            click.style(
                f"The vault is at {current}. The minimum version for an automatic "
                f"upgrade is {MIN_UPGRADABLE_VERSION}.",
                fg="red",
            ),
            err=True,
        )
        echo(
            "Recommended path: install an old wolta-cli that still has the "
            "migrations, upgrade in steps, and return to the latest version.",
            err=True,
        )
        raise SystemExit(1)

    for rel in _managed_section_files(vault):
        try:
            core_sections.validate_markers((vault / rel).read_text(encoding="utf-8"))
        except core_sections.MarkerError as exc:
            echo(
                click.style(f"Error: corrupt managed markers in {rel}: {exc}", fg="red"),
                err=True,
            )
            echo("Fix the markers and try again. Nothing was modified.", err=True)
            raise SystemExit(1)

    pend = pending(current, target)

    if not pend:
        echo(click.style(f"✓ The vault is already up to date (schema {current}).", fg="green"))
        return

    # Dry pass to compute the set of files to touch (without writing). It also
    # runs each migration's own pre-flight, so a vault that cannot be upgraded
    # says so here — before the snapshot, with nothing modified.
    dry_ctx = _make_context(vault, dry_run=True)
    files_to_change: List[str] = []
    planned_moves: List = []
    try:
        for migration in pend:
            files_to_change += migration.up(dry_ctx)
            planned_moves += migration.planned_moves(dry_ctx)
    except Exception as exc:  # noqa: BLE001 - report any refusal as a clean abort
        echo(
            click.style(f"Error: the vault cannot be upgraded yet: {exc}", fg="red"),
            err=True,
        )
        echo("Nothing was modified.", err=True)
        raise SystemExit(1)
    files_to_change = list(dict.fromkeys(files_to_change))

    if dry_run:
        _report(current, target, pend, files_to_change, applied=False, moves=planned_moves)
        return

    client = _sync_client(vault)
    if client and planned_moves:
        echo(
            click.style(
                f"Warning: this vault is inside {client}. Pausing the sync while "
                f"the upgrade runs avoids conflicted copies of the moved folders.",
                fg="yellow",
            )
        )

    # ---------------- Phase 2: snapshot ----------------
    snap = core_snapshot.create_snapshot(vault, files_to_change)

    # ---------------- Phase 3: apply ----------------
    real_ctx = _make_context(vault, dry_run=False, snapshot_dir=snap)
    changed_all: List[str] = []
    try:
        for migration in pend:
            changed = migration.up(real_ctx)
            vm.record_migration(migration.target_version, changed)
            changed_all += changed
    except Exception as exc:  # noqa: BLE001 - any failure must roll back
        core_snapshot.rollback(vault, snap)
        echo(click.style(f"Error during the migration: {exc}", fg="red"), err=True)
        echo(
            click.style("The vault was restored to its previous state (rollback).", fg="yellow"),
            err=True,
        )
        raise SystemExit(1)

    # ---------------- Phase 4: commit / report ----------------
    changed_all = list(dict.fromkeys(changed_all))
    _report(
        current, target, pend, changed_all,
        applied=True, snapshot=snap, moves=planned_moves,
    )


def _report(current, target, pend, files, *, applied, snapshot=None, moves=()) -> None:
    head = "UPGRADE APPLIED" if applied else "DRY-RUN — nothing was applied"
    echo(click.style(f"== {head} ==", bold=True))
    echo(f"Version: {current} -> {target}")
    echo(
        f"Migrations ({len(pend)}): " + ", ".join(m.target_version for m in pend)
    )
    if moves:
        echo("Moves:")
        for move in moves:
            echo(f"  - {move}")
    if files:
        echo("Files:")
        for rel in files:
            echo(f"  - {rel}")
    else:
        echo("Files: (none)")
    if applied and snapshot is not None:
        echo(f"Backup: {snapshot}")
