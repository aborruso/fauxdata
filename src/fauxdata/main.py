"""fauxdata CLI entry point."""

from __future__ import annotations

from typing import Optional

import pyfiglet
import typer
from rich import print as rprint
from rich.console import Console

from fauxdata import __version__

app = typer.Typer(
    name="fauxdata",
    help="Generate and validate fake datasets from YAML schemas.",
    add_completion=False,
)
console = Console()


def _banner():
    banner = pyfiglet.figlet_format("fauxdata", font="slant")
    rprint(f"[bold cyan]{banner}[/bold cyan]")
    rprint("[dim]Generate and validate realistic fake datasets[/dim]\n")


def _version_callback(value: bool):
    if value:
        rprint(f"fauxdata {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    if ctx.invoked_subcommand is None:
        _banner()
        rprint(ctx.get_help())


@app.command(
    "init",
    epilog=(
        "Examples:\n\n"
        "  fauxdata init --name people\n\n"
        "  fauxdata init --name orders --rows 500 --format parquet\n\n"
        "  fauxdata init --name events --description 'clickstream events' --rows 10000 --format jsonl --yes\n"
    ),
)
def init_cmd(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Schema name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Short description"),
    rows: Optional[str] = typer.Option(None, "--rows", "-r", help="Default number of rows (default: 1000)"),
    fmt: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: csv, parquet, json, jsonl (default: csv)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Overwrite existing file without confirmation"),
):
    """Create a schema template (interactive if flags are omitted)."""
    from fauxdata.commands.init import run
    run(name=name, description=description, rows=rows, fmt=fmt, yes=yes)


@app.command(
    "generate",
    epilog=(
        "Examples:\n\n"
        "  fauxdata generate people.yml\n\n"
        "  fauxdata generate people.yml --rows 500 --format csv --out out.csv\n\n"
        "  fauxdata generate people.yml --seed 42 --validate\n\n"
        "  fauxdata generate people.yml --out - --format jsonl | jq .\n\n"
        "  fauxdata generate people.yml --dry-run\n"
    ),
)
def generate_cmd(
    schema: str = typer.Argument(..., help="Path to YAML schema file"),
    rows: Optional[int] = typer.Option(None, "--rows", "-r", help="Number of rows to generate"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Output file path (use - for stdout)"),
    fmt: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: csv, parquet, json, jsonl"),
    seed: Optional[int] = typer.Option(None, "--seed", "-s", help="Random seed for reproducibility"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Run validation after generating"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be generated without writing files"),
):
    """Generate a fake dataset from a YAML schema."""
    from fauxdata.commands.generate import run
    run(schema_path=schema, rows=rows, out=out, fmt=fmt, seed=seed, validate=validate, dry_run=dry_run)


@app.command(
    "validate",
    epilog=(
        "Examples:\n\n"
        "  fauxdata validate people.csv people.yml\n\n"
        "  fauxdata validate out/orders.parquet schemas/orders.yml\n"
    ),
)
def validate_cmd(
    dataset: str = typer.Argument(..., help="Path to dataset file (csv, parquet, json, jsonl)"),
    schema: str = typer.Argument(..., help="Path to YAML schema file"),
):
    """Validate an existing dataset against a YAML schema."""
    from fauxdata.commands.validate import run
    run(dataset_path=dataset, schema_path=schema)


@app.command(
    "preview",
    epilog=(
        "Examples:\n\n"
        "  fauxdata preview people.csv\n\n"
        "  fauxdata preview people.parquet --rows 20\n"
    ),
)
def preview_cmd(
    dataset: str = typer.Argument(..., help="Path to dataset file"),
    rows: int = typer.Option(10, "--rows", "-r", help="Number of rows to preview"),
):
    """Show a preview and column statistics for a dataset."""
    from fauxdata.commands.preview import run
    run(dataset_path=dataset, rows=rows)
