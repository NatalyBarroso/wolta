"""Initialize command for wolta CLI."""

import os
from pathlib import Path
from typing import Optional

import click

from wolta.generators.bootstrap import BootstrapGenerator
from wolta.generators.structure import StructureGenerator
from wolta.generators.templates import TemplateGenerator
from wolta.utils.validators import (
    is_vault_initialized,
    validate_vault_name,
    validate_vault_path,
)


@click.command(name="init")
@click.option(
    "--vault-path",
    default=None,
    help="Path where the vault will be created (default: current directory)",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--name",
    default="wolta",
    help='Custom name for the vault folder. Creates wolta-[name]/ (default: "wolta")',
    type=str,
)
@click.option(
    "--force",
    is_flag=True,
    help="Force re-initialization of an existing vault",
)
def init_command(
    vault_path: Optional[str],
    name: str,
    force: bool,
) -> None:
    """
    Initialize a new Obsidian vault for personal knowledge base.

    Creates folder structure based on T0.1.1 specification:
    - IDENTITY, PREFERENCES, WORK, PROJECTS, PERSONAL-SPACE, KNOWLEDGE, AI-SYSTEM
    - Generates bootstrap questions from official specification
    - Prepares for Claude agent integration
    """
    # Determine vault path
    if vault_path is None:
        vault_path = os.getcwd()

    # Validate vault path
    is_valid, error_msg = validate_vault_path(vault_path)
    if not is_valid:
        click.echo(click.style(f"Error: {error_msg}", fg="red"), err=True)
        raise SystemExit(1)

    # Validate vault name
    is_valid, error_msg = validate_vault_name(name)
    if not is_valid:
        click.echo(click.style(f"Error: {error_msg}", fg="red"), err=True)
        raise SystemExit(1)

    # Construct full vault path
    vault_folder_name = f"wolta-{name}" if name != "wolta" else name
    full_vault_path = Path(vault_path) / vault_folder_name

    # Check if vault already exists
    if full_vault_path.exists():
        if is_vault_initialized(str(full_vault_path)) and not force:
            click.echo(
                click.style(
                    f"Error: Vault already initialized at {full_vault_path}",
                    fg="red",
                ),
                err=True,
            )
            click.echo("Use --force to re-initialize", err=True)
            raise SystemExit(1)

        if not force:
            click.echo(
                click.style(
                    f"Error: Directory already exists: {full_vault_path}",
                    fg="red",
                ),
                err=True,
            )
            click.echo("Use --force to overwrite", err=True)
            raise SystemExit(1)

    # Create vault directory
    try:
        full_vault_path.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        click.echo(click.style(f"Error creating vault directory: {e}", fg="red"), err=True)
        raise SystemExit(1)

    with click.progressbar(
        length=4,
        label="Initializing vault",
        show_pos=True,
    ) as bar:
        # Step 1: Generate folder structure
        try:
            structure_gen = StructureGenerator(str(full_vault_path))
            structure_gen.generate()
            bar.update(1)
        except Exception as e:
            click.echo(click.style(f"Error generating structure: {e}", fg="red"), err=True)
            raise SystemExit(1)

        # Step 2: Generate bootstrap questions
        try:
            bootstrap_gen = BootstrapGenerator(str(full_vault_path))
            bootstrap_gen.generate()
            bar.update(1)
        except Exception as e:
            click.echo(
                click.style(f"Error generating bootstrap questions: {e}", fg="red"),
                err=True,
            )
            raise SystemExit(1)

        # Step 3: Generate note templates
        try:
            template_gen = TemplateGenerator(str(full_vault_path))
            template_gen.generate()
            bar.update(1)
        except Exception as e:
            click.echo(
                click.style(f"Error generating templates: {e}", fg="red"),
                err=True,
            )
            raise SystemExit(1)

        # Step 4: Create initialization marker
        try:
            marker_dir = full_vault_path / ".wolta"
            marker_dir.mkdir(exist_ok=True)
            marker_file = marker_dir / "initialized"
            marker_file.touch()
            bar.update(1)
        except Exception as e:
            click.echo(click.style(f"Error creating marker file: {e}", fg="red"), err=True)
            raise SystemExit(1)

    # Success message
    click.echo()
    click.echo(click.style("✓ Vault initialized successfully!", fg="green", bold=True))
    click.echo(f"  Vault location: {click.style(str(full_vault_path), fg='cyan')}")
    click.echo(f"  Vault name: {click.style(vault_folder_name, fg='cyan')}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Open the vault in Obsidian: File → Open folder as vault")
    click.echo(f"  2. Navigate to: {full_vault_path}")
    click.echo("  3. Complete the bootstrap questions in AI-SYSTEM/BOOTSTRAP/BOOTSTRAP-QUESTIONNAIRE.md")
