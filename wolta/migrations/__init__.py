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

# Floor of support for the whole migration set (D-11). Set to "0.0.0" so that
# pre-versioning vaults (treated as 0.0.0) are eligible for the 0.0.x -> 0.1.0
# migration (T2.3.4 D-01). It is raised only when old migrations are squashed.
MIN_UPGRADABLE_VERSION = "0.0.0"

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

    Walks the registry in semver order and keeps each migration whose
    `target_version` sits in `(running, target]` and whose `min_version` is
    satisfied by `running` -- the version the vault will be at when that
    migration fires, not the version it started the run at (D-11). Without
    that accumulation a 0.0.0 vault would pick `m_0_1_0` and drop
    `m_0_2_0` (`min_version = 0.1.0`), then report success at 0.2.0 while
    still sitting on 0.1.0.
    """
    running = Version(current)
    tgt = Version(target)
    selected: List[Migration] = []
    for m in all_migrations():
        target_v = Version(m.target_version)
        if running < target_v <= tgt and running >= Version(m.min_version):
            selected.append(m)
            running = target_v
    return selected
