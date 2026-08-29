"""Top-level layout of a Wolta vault (v0.2.0 D-06/D-08).

A vault has two root spaces with different owners:

    wolta-[name]/
    ├── HUMAN/     the user's space; no fixed structure, born empty
    ├── SYSTEM/    the agent's space; holds the KB categories and its tooling
    ├── .wolta/    vault marker and schema state
    ├── CLAUDE.md  loaded automatically when the vault is opened as a project
    └── README.md  entry point for a person who opens the folder

`.wolta/` and `CLAUDE.md` must stay at the root: one identifies the vault, the
other is auto-loaded by the agent. `README.md` stays because it is the first
thing a human sees. Everything else the CLI generates lives under `SYSTEM/`.

These names are defined here, and only here, because the structure generator,
the file manifest, the migrations and the tests all need to agree on them.
"""

SYSTEM_ROOT = "SYSTEM"
HUMAN_ROOT = "HUMAN"

# Vault-relative paths that stay at the root (D-08).
ROOT_ARTIFACTS = (
    ".wolta",
    "CLAUDE.md",
    "README.md",
)


def system(rel: str) -> str:
    """Prefix a vault-relative path with the agent space.

    >>> system("AI-SYSTEM/SKILLS/raw-ingest.md")
    'SYSTEM/AI-SYSTEM/SKILLS/raw-ingest.md'
    """
    return f"{SYSTEM_ROOT}/{rel}"


def human(rel: str) -> str:
    """Prefix a vault-relative path with the user space."""
    return f"{HUMAN_ROOT}/{rel}"
