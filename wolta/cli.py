"""CLI entrypoint for wolta command-line tool."""

import click

from wolta import __version__
from wolta.commands.init import init_command


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="wolta")
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    Wolta - CLI tool for initializing personal knowledge bases in Obsidian.

    Initialize a new vault with: wolta init [OPTIONS]
    """
    # Show help if no command is provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register commands
main.add_command(init_command)


if __name__ == "__main__":
    main()
