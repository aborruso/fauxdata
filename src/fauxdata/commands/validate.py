"""fauxdata validate command."""

from __future__ import annotations

import polars as pl
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fauxdata import jsonmode
from fauxdata.schema import load_schema
from fauxdata.validator import validate_dataset

console = Console()


def run(dataset_path: str, schema_path: str, json_out: bool = False):
    """Validate an existing dataset against a YAML schema."""
    schema = load_schema(schema_path)

    if not json_out:
        rprint(Panel(
            f"[bold cyan]fauxdata validate[/bold cyan]  [dim]{dataset_path}[/dim]",
            expand=False,
        ))

    ext = dataset_path.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        df = pl.read_csv(dataset_path)
    elif ext == "parquet":
        df = pl.read_parquet(dataset_path)
    elif ext == "json":
        df = pl.read_json(dataset_path)
    elif ext in ("jsonl", "ndjson"):
        df = pl.read_ndjson(dataset_path)
    else:
        if json_out:
            jsonmode.fail(f"Unsupported file format: .{ext}")
        rprint(f"[red]Unsupported file format: .{ext}[/red]")
        raise typer.Exit(code=1)

    if json_out:
        all_passed, results = validate_dataset(df, schema)
        jsonmode.emit({"passed": all_passed, "rows": len(df), "results": results})
        if not all_passed:
            raise typer.Exit(code=1)
        return

    rprint(f"  Loaded [bold]{len(df)}[/bold] rows, [bold]{len(df.columns)}[/bold] columns")

    if not schema.validation_rules:
        rprint("[yellow]No validation rules defined in schema.[/yellow]")
        raise typer.Exit()

    all_passed, results = validate_dataset(df, schema)

    t = Table(title="Validation Results", show_header=True, header_style="bold")
    t.add_column("#")
    t.add_column("Rule", style="cyan")
    t.add_column("Column")
    t.add_column("Passed", justify="right")
    t.add_column("Failed", justify="right")
    t.add_column("Status")

    for r in results:
        if r["ok"]:
            status = "[green]PASS[/green]"
        elif not r["evaluated"]:
            status = "[red]NOT RUN[/red]"
        else:
            status = "[red]FAIL[/red]"
        t.add_row(
            str(r["step"]),
            r["rule"],
            r["column"],
            str(r["passed"]),
            str(r["failed"]),
            status,
        )

    console.print(t)

    if all_passed:
        rprint("[bold green]All validation rules passed.[/bold green]")
    else:
        rprint("[bold red]Some validation rules failed.[/bold red]")
        raise typer.Exit(code=1)
