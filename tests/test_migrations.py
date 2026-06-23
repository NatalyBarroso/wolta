"""Unit tests for the migration registry (T2.3.3).

Uses synthetic Migration subclasses (no concrete migrations exist until
T2.3.4), monkeypatching the registry's discovery.
"""

import wolta.migrations as reg
from wolta.migrations.base import Migration


def _mig(target, min_version="0.0.0"):
    class _M(Migration):
        pass

    _M.target_version = target
    _M.min_version = min_version
    return _M()


def test_first_migration_is_v010():
    # T2.3.4 ships the first concrete migration (m_0_1_0, target 0.1.0)
    targets = [m.target_version for m in reg.all_migrations()]
    assert "0.1.0" in targets


def test_pending_orders_by_semver(monkeypatch):
    migs = [_mig("0.10.0"), _mig("0.2.0"), _mig("0.3.0")]
    monkeypatch.setattr(reg, "all_migrations", lambda: sorted(
        migs, key=lambda m: __import__("packaging.version", fromlist=["Version"]).Version(m.target_version)
    ))
    result = reg.pending("0.1.0", "0.10.0")
    assert [m.target_version for m in result] == ["0.2.0", "0.3.0", "0.10.0"]


def test_pending_range_is_exclusive_on_current_inclusive_on_target(monkeypatch):
    migs = [_mig("0.2.0"), _mig("0.3.0"), _mig("0.4.0")]
    monkeypatch.setattr(reg, "all_migrations", lambda: migs)

    assert [m.target_version for m in reg.pending("0.2.0", "0.3.0")] == ["0.3.0"]
    assert reg.pending("0.4.0", "0.4.0") == []
    assert [m.target_version for m in reg.pending("0.1.0", "0.4.0")] == [
        "0.2.0",
        "0.3.0",
        "0.4.0",
    ]


def test_pending_respects_min_version(monkeypatch):
    # a migration that requires the vault to be at >= 0.3.0 already
    migs = [_mig("0.5.0", min_version="0.3.0")]
    monkeypatch.setattr(reg, "all_migrations", lambda: migs)

    assert reg.pending("0.1.0", "0.5.0") == []          # below min_version -> excluded
    assert [m.target_version for m in reg.pending("0.3.0", "0.5.0")] == ["0.5.0"]


def test_min_upgradable_version_constant():
    # 0.0.0 so pre-versioning vaults are eligible for the 0.0.x -> 0.1.0 migration
    assert reg.MIN_UPGRADABLE_VERSION == "0.0.0"
