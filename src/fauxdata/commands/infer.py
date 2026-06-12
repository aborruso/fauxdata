"""fauxdata infer command - build a YAML schema from a real dataset.

Uses pointblank's ``schema_from_tbl`` (>=0.25) to infer rich constraints
(min/max, unique, null rate, allowed values, presets, string lengths) from an
existing table, then serializes them into a fauxdata YAML schema that can be
fed back to ``fauxdata generate``.
"""

from __future__ import annotations

from pathlib import Path

import pointblank as pb
import polars as pl
import typer
import yaml
from rich import print as rprint
from rich.panel import Panel

# Polars dtype name (str) -> fauxdata col_type
_DTYPE_MAP = {
    "Int": "int",
    "UInt": "int",
    "Float": "float",
    "String": "string",
    "Utf8": "string",
    "Boolean": "bool",
    "Datetime": "datetime",
    "Date": "date",
}


def _col_type_from_dtype(dtype: str) -> str:
    """Map a pointblank/polars dtype name to a fauxdata col_type."""
    for prefix, ctype in _DTYPE_MAP.items():
        if dtype.startswith(prefix):
            return ctype
    return "string"


def _field_to_spec(field) -> dict:
    """Convert an inferred pointblank Field into a fauxdata column spec dict."""
    attrs = vars(field)
    col_type = _col_type_from_dtype(attrs.get("dtype", "String"))
    spec: dict = {"type": col_type}

    if attrs.get("unique"):
        spec["unique"] = True
    if attrs.get("nullable"):
        spec["nullable"] = True
    np = attrs.get("null_probability")
    if np:
        spec["null_probability"] = round(float(np), 4)

    if col_type in ("int", "float"):
        if attrs.get("min_val") is not None:
            spec["min"] = attrs["min_val"]
        if attrs.get("max_val") is not None:
            spec["max"] = attrs["max_val"]
        if attrs.get("allowed"):
            spec["values"] = list(attrs["allowed"])

    elif col_type in ("date", "datetime"):
        if attrs.get("min_date") is not None:
            spec["min"] = str(attrs["min_date"])
        if attrs.get("max_date") is not None:
            spec["max"] = str(attrs["max_date"])

    elif col_type == "string":
        if attrs.get("preset"):
            spec["preset"] = attrs["preset"]
        elif attrs.get("allowed"):
            spec["values"] = list(attrs["allowed"])
        elif attrs.get("pattern"):
            spec["pattern"] = attrs["pattern"]
        if attrs.get("min_length") is not None:
            spec["min_length"] = attrs["min_length"]
        if attrs.get("max_length") is not None:
            spec["max_length"] = attrs["max_length"]

    return spec


def _build_validation(columns: list[tuple[str, dict]]) -> list[dict]:
    """Derive validation rules from the inferred column specs."""
    rules: list[dict] = []

    not_null = [name for name, spec in columns if not spec.get("nullable")]
    if not_null:
        rules.append({"rule": "col_vals_not_null", "columns": not_null})

    for name, spec in columns:
        if spec["type"] in ("int", "float") and "min" in spec and "max" in spec:
            rules.append({"rule": "col_vals_between", "column": name,
                          "min": spec["min"], "max": spec["max"]})

    for name, spec in columns:
        if "values" in spec:
            rules.append({"rule": "col_vals_in_set", "column": name, "values": list(spec["values"])})

    unique_cols = [name for name, spec in columns if spec.get("unique")]
    if unique_cols:
        rules.append({"rule": "rows_distinct", "columns": unique_cols})

    return rules


def _load_table(path: str) -> pl.DataFrame:
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        # try_parse_dates so date/datetime columns are typed (not frozen as categorical strings)
        return pl.read_csv(path, try_parse_dates=True)
    if ext == "parquet":
        return pl.read_parquet(path)
    if ext == "json":
        return pl.read_json(path)
    if ext in ("jsonl", "ndjson"):
        return pl.read_ndjson(path)
    rprint(f"[red]Unsupported file format: .{ext}[/red]")
    raise typer.Exit(code=1)


def run(
    dataset_path: str,
    out: str | None = None,
    name: str | None = None,
    rows: int | None = None,
    fmt: str = "csv",
    categorical_threshold: float = 20,
    detect_presets: bool = True,
    sample_size: int | None = None,
):
    """Infer a fauxdata YAML schema from a real dataset."""
    rprint(Panel(
        f"[bold cyan]fauxdata infer[/bold cyan]  [dim]{dataset_path}[/dim]",
        expand=False,
    ))

    df = _load_table(dataset_path)
    rprint(f"  Loaded [bold]{len(df)}[/bold] rows, [bold]{len(df.columns)}[/bold] columns")

    pb_schema = pb.schema_from_tbl(
        df,
        categorical_threshold=categorical_threshold,
        detect_presets=detect_presets,
        sample_size=sample_size,
    )

    columns = [(col_name, _field_to_spec(field)) for col_name, field in pb_schema.columns]

    schema_name = name or Path(dataset_path).stem
    out_rows = rows if rows is not None else len(df)

    schema_dict = {
        "name": schema_name,
        "description": f"Inferred from {Path(dataset_path).name}",
        "rows": out_rows,
        "seed": 42,
        "output": {"format": fmt, "path": f"{schema_name}.{fmt}"},
        "columns": {col_name: spec for col_name, spec in columns},
        "validation": _build_validation(columns),
    }

    text = yaml.safe_dump(schema_dict, sort_keys=False, allow_unicode=True, default_flow_style=False)

    out_path = out or f"{schema_name}.yml"
    if out_path == "-":
        import sys
        sys.stdout.write(text)
        return

    Path(out_path).write_text(text)
    rprint(f"[green]Created[/green] [bold]{out_path}[/bold] "
           f"([bold]{len(columns)}[/bold] columns, "
           f"[bold]{len(schema_dict['validation'])}[/bold] validation rules)")
    rprint("[dim]Generate synthetic data with:[/dim]")
    rprint(f"  [cyan]fauxdata generate {out_path} --validate[/cyan]")
    rprint(f"schema_path: {out_path}")
