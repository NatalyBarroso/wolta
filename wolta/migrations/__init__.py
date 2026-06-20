"""Migration registry for the Wolta upgrade system (T2.3.3).

Discovers migration modules (named `m_*`) shipped inside this package,
orders them by semantic version, and selects the ones pending for a given
vault. Migrations live with the CLI, never inside the vault (D-09).
"""

import importlib
import pkgutil
from typing import List

from packaging.version import Version

from wolta.migrations.base import Migration, MigrationContext

# Floor of support for the whole migration set (D-11). While the migration
# chain is complete this stays at "0.1.0" and excludes nobody; it is raised
# only when old migrations are squashed/removed.
MIN_UPGRADABLE_VERSION = "0.1.0"

__all__ = ["MIN_UPGRADABLE_VERSION", "all_migrations", "pending", "MigrationContext"]


def all_migrations() -> List[Migration]:
    """Discover and instantiate every `m_*` migration, ordered by semver.

    Ordering uses `packaging.version.Version`, never string comparison, so
    `0.10.0` sorts after `0.2.0` (R-04, D-06).
    """
    found: List[Migration] = []
    for _, mod_name, _ in pkgutil.iter_modules(__path__):
        if not mod_name.startswith("m_"):
            continue
        module = importlib.import_module(f"{__name__}.{mod_name}")
        for obj in vars(module).values():
            if (
                isinstance(obj, type)
                and issubclass(obj, Migration)
                and obj is not Migration
            ):
                found.append(obj())
    return sorted(found, key=lambda m: Version(m.target_version))


def pending(current: str, target: str) -> List[Migration]:
    """Migrations to apply to move a vault from `current` up to `target`.

    Selects those with `current < target_version <= target` and whose
    `min_version` precondition is satisfied (`current >= min_version`),
    in ascending semver order.
    """
    cur = Version(current)
    tgt = Version(target)
    return [
        m
        for m in all_migrations()
        if cur < Version(m.target_version) <= tgt and cur >= Version(m.min_version)
    ]
