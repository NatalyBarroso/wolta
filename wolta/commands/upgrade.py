"""`wolta upgrade` command (T2.3.3).

Upgrades an existing vault to the latest (or a target) schema version,
applying pending migrations sequentially in four phases: pre-flight,
snapshot, apply, commit/rollback (T2.3.1 D-12). No migration is applied
under --dry-run, and any failure mid-apply rolls the vault back.
"""

import os
from pathlib import Path
from typing import List

import click
from packaging.version import Version

from wolta import __version__
from wolta.core import files as core_files
from wolta.core import manifest as core_manifest
from wolta.core import sections as core_sections
from wolta.core import snapshot as core_snapshot
from wolta.migrations import MIN_UPGRADABLE_VERSION, pending
from wolta.migrations.base import MigrationContext
from wolta.utils.version_manager import VersionManager


def _is_vault(path: Path) -> bool:
    return (path / ".wolta").exists() or (path / "CLAUDE.md").exists()


def _managed_section_files(vault: Path) -> List[str]:
    return [
        rel
        for rel, pol in core_manifest.MANIFEST.items()
        if pol == core_manifest.Policy.MANAGED_SECTION and (vault / rel).exists()
    ]


def _make_context(vault: Path, dry_run: bool) -> MigrationContext:
    return MigrationContext(
        vault=vault,
        manifest=core_manifest,
        sections=core_sections,
        files=core_files,
        dry_run=dry_run,
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
        click.echo(
            click.style(
                f"Error: {vault} no parece un vault wolta (falta .wolta/ o CLAUDE.md).",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    vm = VersionManager(str(vault))
    current = vm.get_vault_version()
    target = to_version or __version__

    # ---------------- Fase 1: pre-flight (sin modificar nada) ----------------
    if Version(target) > Version(__version__):
        click.echo(
            click.style(
                f"Error: --to-version {target} es mayor que la versión del CLI "
                f"({__version__}). Actualiza wolta-cli para migrar a esa versión.",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)

    if Version(current) < Version(MIN_UPGRADABLE_VERSION):
        click.echo(
            click.style(
                f"El vault está en {current}. La versión mínima para upgrade "
                f"automático es {MIN_UPGRADABLE_VERSION}.",
                fg="red",
            ),
            err=True,
        )
        click.echo(
            "Camino recomendado: instala un wolta-cli antiguo que aún tenga las "
            "migraciones, actualiza por escalones y vuelve a la última versión.",
            err=True,
        )
        raise SystemExit(1)

    for rel in _managed_section_files(vault):
        try:
            core_sections.validate_markers((vault / rel).read_text(encoding="utf-8"))
        except core_sections.MarkerError as exc:
            click.echo(
                click.style(f"Error: markers managed corruptos en {rel}: {exc}", fg="red"),
                err=True,
            )
            click.echo("Corrige los markers y reintenta. No se modificó nada.", err=True)
            raise SystemExit(1)

    pend = pending(current, target)

    if not pend:
        click.echo(click.style(f"✓ El vault ya está al día (schema {current}).", fg="green"))
        return

    # Pase dry para calcular el conjunto de archivos a tocar (sin escribir).
    dry_ctx = _make_context(vault, dry_run=True)
    files_to_change: List[str] = []
    for migration in pend:
        files_to_change += migration.up(dry_ctx)
    files_to_change = list(dict.fromkeys(files_to_change))

    if dry_run:
        _report(current, target, pend, files_to_change, applied=False)
        return

    # ---------------- Fase 2: snapshot ----------------
    snap = core_snapshot.create_snapshot(vault, files_to_change)

    # ---------------- Fase 3: apply ----------------
    real_ctx = _make_context(vault, dry_run=False)
    changed_all: List[str] = []
    try:
        for migration in pend:
            changed = migration.up(real_ctx)
            vm.record_migration(migration.target_version, changed)
            changed_all += changed
    except Exception as exc:  # noqa: BLE001 - any failure must roll back
        core_snapshot.rollback(vault, snap)
        click.echo(click.style(f"Error durante la migración: {exc}", fg="red"), err=True)
        click.echo(
            click.style("Se restauró el vault a su estado previo (rollback).", fg="yellow"),
            err=True,
        )
        raise SystemExit(1)

    # ---------------- Fase 4: commit / report ----------------
    changed_all = list(dict.fromkeys(changed_all))
    _report(current, target, pend, changed_all, applied=True, snapshot=snap)


def _report(current, target, pend, files, *, applied, snapshot=None) -> None:
    head = "UPGRADE APLICADO" if applied else "DRY-RUN — NO se aplicó nada"
    click.echo(click.style(f"== {head} ==", bold=True))
    click.echo(f"Versión: {current} -> {target}")
    click.echo(
        f"Migraciones ({len(pend)}): " + ", ".join(m.target_version for m in pend)
    )
    if files:
        click.echo("Archivos:")
        for rel in files:
            click.echo(f"  - {rel}")
    else:
        click.echo("Archivos: (ninguno)")
    if applied and snapshot is not None:
        click.echo(f"Backup: {snapshot}")
