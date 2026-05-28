"""Validation utilities for wolta CLI."""

import re
from pathlib import Path
from typing import Tuple


def validate_vault_name(name: str) -> Tuple[bool, str]:
    """
    Validate vault name format.

    Rules:
    - Only alphanumeric characters and hyphens
    - Length: 1-50 characters
    - Cannot start or end with hyphen

    Args:
        name: The vault name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Vault name cannot be empty"

    if len(name) > 50:
        return False, "Vault name cannot exceed 50 characters"

    if name.startswith('-') or name.endswith('-'):
        return False, "Vault name cannot start or end with a hyphen"

    pattern = r'^[a-zA-Z0-9-]+$'
    if not re.match(pattern, name):
        return False, "Vault name can only contain alphanumeric characters and hyphens"

    return True, ""


def validate_vault_path(path: str) -> Tuple[bool, str]:
    """
    Validate that the vault path exists and is writable.

    Args:
        path: The vault path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    vault_path = Path(path)

    if not vault_path.exists():
        return False, f"Vault path does not exist: {path}"

    if not vault_path.is_dir():
        return False, f"Vault path is not a directory: {path}"

    # Check if writable by trying to create a test file
    test_file = vault_path / ".wolta_write_test"
    try:
        test_file.touch()
        test_file.unlink()
        return True, ""
    except (PermissionError, OSError) as e:
        return False, f"Vault path is not writable: {e}"


def is_vault_initialized(vault_root: str) -> bool:
    """
    Check if a vault has already been initialized.

    Checks for the existence of .wolta/initialized marker file.

    Args:
        vault_root: Root path of the vault directory

    Returns:
        True if vault is initialized, False otherwise
    """
    marker_file = Path(vault_root) / ".wolta" / "initialized"
    return marker_file.exists()
