"""fauxdata generate command."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fauxdata.generator import generate_dataset
from fauxdata.output import default_output_path, export_dataset, write_stdout
from fauxdata.schema import load_schema
from fauxdata.validator import validate_dataset

console = Console()


def run(
    schema_path: str,
    rows: Optional[int] = None,
    out: Optional[str] = None,
    fmt: Optional[str] = None,
    seed: Optional[int] = None,
    validate: bool = False,
):
    """Generate a fake dataset from a YAML schema."""
    schema = load_schema(schema_path)

    n = rows if rows is not None else schema.rows
    rng_seed = seed if seed is not None else schema.seed
    output_fmt = fmt or schema.output_format
    output_path = out or schema.output_path or default_output_path(schema.name, output_fmt)

    stdout_mode = output_path == "-"

    if not stdout_mode:
        rprint(Panel(f"[bold cyan]fauxdata generate[/bold cyan]  [dim]{schema_path}[/dim]", expand=False))

    if stdout_mode:
        df = generate_dataset(schema, rows=n, seed=rng_seed)
        write_stdout(df, output_fmt)
        return

    with console.status(f"[bold green]Generating {n} rows...[/bold green]"):
        df = generate_dataset(schema, rows=n, seed=rng_seed)

    _print_schema_table(schema, n, rng_seed)

    saved = export_dataset(df, output_path, output_fmt)
    rprint(f"\n[green]Saved[/green] [bold]{saved}[/bold]  ([dim]{output_fmt}, {n} rows[/dim])")

    if validate:
        _run_validation(df, schema)


def _print_schema_table(schema, n: int, seed):
    t = Table(title=f"Schema: {schema.name}", show_header=True, header_style="bold magenta")
    t.add_column("Column", style="cyan")
    t.add_column("Type")
    t.add_column("Preset/Pattern/Values")
    t.add_column("Min")
    t.add_column("Max")
    t.add_column("Unique")
    t.add_column("Null%")

    for col in schema.columns:
        if col.pattern:
            preset_val = f"pattern:{col.pattern}"
        elif col.preset:
            preset_val = col.preset
        elif col.values:
            preset_val = str(col.values)
        else:
            preset_val = "-"
        null_pct = f"{int(col.null_probability * 100)}%" if col.null_probability else "-"
        t.add_row(
            col.name,
            col.col_type,
            preset_val,
            str(col.min) if col.min is not None else "-",
            str(col.max) if col.max is not None else "-",
            "yes" if col.unique else "no",
            null_pct,
        )

    console.print(t)
    rprint(f"  rows=[bold]{n}[/bold]  seed=[bold]{seed}[/bold]  locale=[bold]{schema.locale}[/bold]")


def _run_validation(df, schema):
    rprint("\n[bold]Running validation...[/bold]")
    all_passed, results = validate_dataset(df, schema)

    if not results:
        rprint("[yellow]No validation rules defined.[/yellow]")
        return

    t = Table(title="Validation Results", show_header=True, header_style="bold")
    t.add_column("#")
    t.add_column("Rule", style="cyan")
    t.add_column("Column")
    t.add_column("Passed", justify="right")
    t.add_column("Failed", justify="right")
    t.add_column("Status")

    for r in results:
        status = "[green]PASS[/green]" if r["ok"] else "[red]FAIL[/red]"
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
