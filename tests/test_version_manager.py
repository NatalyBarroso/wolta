"""Unit tests for VersionManager (T2.3.2)."""

import json

from wolta.utils.version_manager import SCHEMA_DEFAULT, VersionManager


def test_legacy_vault_without_version_file(tmp_path):
    """A vault with no .wolta/version is assumed to be at SCHEMA_DEFAULT."""
    vm = VersionManager(str(tmp_path))
    assert vm.get_vault_version() == SCHEMA_DEFAULT


def test_initialize_writes_full_state(tmp_path):
    vm = VersionManager(str(tmp_path))
    vm.initialize("0.1.0")

    assert vm.get_vault_version() == "0.1.0"
    data = json.loads((tmp_path / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1.0"
    assert data["wolta_cli_version"] == "0.1.0"
    assert data["initialized_at"] is not None
    assert data["last_upgrade_at"] is None
    assert data["applied_migrations"] == []


def test_set_vault_version_updates_schema_and_timestamp(tmp_path):
    vm = VersionManager(str(tmp_path))
    vm.initialize("0.1.0")

    vm.set_vault_version("0.2.0")

    assert vm.get_vault_version() == "0.2.0"
    data = json.loads((tmp_path / ".wolta" / "version").read_text(encoding="utf-8"))
    assert data["last_upgrade_at"] is not None
    # the audit trail / cli version are preserved
    assert data["wolta_cli_version"] == "0.1.0"
