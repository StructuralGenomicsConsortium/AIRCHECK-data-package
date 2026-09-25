"""Command-line interface for aircheckdata."""

import logging
from collections.abc import Callable
from functools import wraps

import click

from aircheckdata import (
    AircheckDataError,
    __version__,
    clear_cache,
    default_cache_dir,
    get_columns,
    list_datasets,
    list_partners,
    load_dataset,
)
from aircheckdata.main import DEFAULT_DATASET, DEFAULT_PARTNER

_HINT = "If a dataset name has spaces or special characters, wrap it in quotes."


def _handle_errors(func: Callable) -> Callable:
    """Turn library errors into a clean message and exit status 1."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AircheckDataError, ValueError) as exc:
            raise click.ClickException(f"{exc}\n{_HINT}") from exc

    return wrapper


@click.group(help="Load AIRCHECK datasets from the command line.")
@click.version_option(__version__, prog_name="aircheckdata")
@click.option("-v", "--verbose", is_flag=True, help="Show download/read log messages.")
def cli(verbose: bool) -> None:
    """Root command group."""
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING, format="%(message)s"
    )


@cli.command(name="partners")
@_handle_errors
def partners_command() -> None:
    """List all dataset providers."""
    for partner in list_partners():
        click.echo(partner)


@cli.command(name="list")
@click.argument("partner", default=DEFAULT_PARTNER)
@_handle_errors
def list_command(partner: str) -> None:
    """List datasets available from PARTNER (default: HitGen)."""
    for name, description in list_datasets(partner).items():
        click.echo(f"{name}: {description}")


@cli.command(name="columns")
@click.argument("partner", default=DEFAULT_PARTNER)
@click.argument("dataset", default=DEFAULT_DATASET)
@_handle_errors
def columns_command(partner: str, dataset: str) -> None:
    """List the columns of PARTNER/DATASET (default: HitGen WDR91)."""
    for column in get_columns(partner, dataset):
        click.echo(f"{column['name']}: {column['description']}")


@cli.command(name="load")
@click.argument("partner", default=DEFAULT_PARTNER)
@click.argument("dataset", default=DEFAULT_DATASET)
@click.option(
    "-c",
    "--columns",
    help="Comma-separated list of columns to load.",
)
@click.option("--no-progress", is_flag=True, help="Hide the download progress bar.")
@click.option("--no-cache", is_flag=True, help="Do not keep the downloaded file.")
@_handle_errors
def load_command(
    partner: str, dataset: str, columns: str | None, no_progress: bool, no_cache: bool
) -> None:
    """Download PARTNER/DATASET into the cache and print its shape."""
    column_list = [c.strip() for c in columns.split(",")] if columns else None
    df = load_dataset(
        partner,
        dataset,
        columns=column_list,
        show_progress=not no_progress,
        use_cache=not no_cache,
    )
    click.echo(
        f"Loaded {partner}/{dataset}: {len(df)} rows x {len(df.columns)} columns."
    )


@cli.command(name="cache")
@click.option("--clear", is_flag=True, help="Delete all cached datasets.")
def cache_command(clear: bool) -> None:
    """Show the cache directory, or clear it with --clear."""
    if clear:
        removed = clear_cache()
        click.echo(f"Removed {removed} cached file(s).")
    else:
        click.echo(default_cache_dir())


if __name__ == "__main__":
    cli()
