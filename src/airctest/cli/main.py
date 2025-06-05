"""Command-line interface for aircheckdata utilities."""
import sys

import click

from airctest import get_columns, list_datasets, load_dataset


@click.group(help="aircheckdata - A utility for loading AIRCHECK data from Python environment and interacting with them.")
def cli():
    """Command-line interface group for aircheckdata utilities."""
    pass


@cli.command(name="list")
def list_command():
    """List all available datasets."""
    try:
        click.echo("Available datasets:")
        for dataset in list_datasets():
            click.echo(f" - {dataset}")
    except Exception as e:
        click.echo(f"❌ Error listing datasets: {e}", err=True)
        sys.exit(1)


@cli.command(name="columns")
@click.argument("partner", required=False, default="HitGen")
@click.argument("dataset", required=False, default="WDR91")
def columns_command(partner, dataset):
    """List columns of a specific dataset."""
    try:
        click.echo(f"Listing columns for dataset: {dataset}")
        columns = get_columns(partner_name=partner,dataset_name=dataset)
        for column in columns:
            click.echo(f" - {column}")
    except Exception as e:
        click.echo(f"❌ Error retrieving columns: {e}", err=True)
        click.echo(
            "💡 Tip: If your dataset name has spaces or special characters, wrap it in quotes.", err=True)
        sys.exit(1)


@cli.command(name="load")
@click.argument("dataset", required=False, default="WDR91")
@click.option("--columns", "-c", help="Comma-separated list of columns to load.")
def load_command(dataset, columns):
    """Load a specific dataset optionally with specific columns."""
    try:
        column_list = None
        print(f"Loading dataset: {dataset} with columns: {columns}")
        if columns:
            column_list = [col.strip() for col in columns.split(",")]

        click.echo(f"Loading dataset: {dataset}")
        if column_list:
            click.echo(f"With columns: {column_list}")

        df = load_dataset(dataset_name=dataset, columns=column_list)
        click.echo(
            f"✅ Loaded dataset {dataset} with {len(df)} rows and {len(df.columns)} columns.")
    except Exception as e:
        click.echo(f"❌ Error loading dataset: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
