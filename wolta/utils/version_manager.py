"""Version tracking for Wolta vaults.

Single reader/writer of `.wolta/version`, the source of truth for the vault
schema version (decision D-08 of T2.3.1). The version lives here, not in
`.wolta/config.md` (which is user-owned).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Version assumed for vaults initialized before version tracking existed
# (no `.wolta/version` file present). See R-02 of T2.3.1.
SCHEMA_DEFAULT = "0.1.0"


class VersionManager:
    """Reads and writes the `.wolta/version` JSON state file for a vault."""

    def __init__(self, vault_path: str) -> None:
        """
        Args:
            vault_path: Path to the vault root directory.
        """
        self.vault_path = Path(vault_path)
        self.path = self.vault_path / ".wolta" / "version"

    def _read_raw(self) -> Dict[str, Any]:
        """Return the full version dict, or a legacy default if the file is absent."""
        if not self.path.exists():
            return {
                "schema_version": SCHEMA_DEFAULT,
                "wolta_cli_version": None,
                "initialized_at": None,
                "last_upgrade_at": None,
                "applied_migrations": [],
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: Dict[str, Any]) -> None:
        """Persist the version dict as pretty-printed JSON."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def get_vault_version(self) -> str:
        """Return the current schema version of the vault.

        Vaults without a `.wolta/version` file are assumed to be at
        SCHEMA_DEFAULT (legacy handling).
        """
        return self._read_raw()["schema_version"]

    def set_vault_version(self, version: str) -> None:
        """Update the schema version and stamp `last_upgrade_at`."""
        data = self._read_raw()
        data["schema_version"] = version
        data["last_upgrade_at"] = datetime.now().isoformat()
        self._write(data)

    def initialize(self, cli_version: str) -> None:
        """Write the initial `.wolta/version` for a freshly created vault."""
        self._write(
            {
                "schema_version": cli_version,
                "wolta_cli_version": cli_version,
                "initialized_at": datetime.now().isoformat(),
                "last_upgrade_at": None,
                "applied_migrations": [],
            }
        )
