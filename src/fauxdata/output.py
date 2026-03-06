"""Export functions for fauxdata datasets."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def normalize_fmt(fmt: str) -> str:
    """Normalize format aliases."""
    if fmt == "jsonlines":
        return "jsonl"
    return fmt


def export_dataset(df: pl.DataFrame, path: str | Path, fmt: str) -> Path:
    """Export a DataFrame to the given format and path. Returns the output path."""
    fmt = normalize_fmt(fmt)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        df.write_csv(out)
    elif fmt == "parquet":
        df.write_parquet(out)
    elif fmt == "json":
        df.write_json(out)
    elif fmt == "jsonl":
        df.write_ndjson(out)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use csv, parquet, json, jsonl, or jsonlines.")

    return out


def write_stdout(df: pl.DataFrame, fmt: str) -> None:
    """Write a DataFrame to stdout."""
    import sys
    fmt = normalize_fmt(fmt)
    if fmt == "csv":
        sys.stdout.write(df.write_csv())
    elif fmt == "json":
        sys.stdout.write(df.write_json())
    elif fmt == "jsonl":
        sys.stdout.write(df.write_ndjson())
    elif fmt == "parquet":
        import io
        buf = io.BytesIO()
        df.write_parquet(buf)
        sys.stdout.buffer.write(buf.getvalue())
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use csv, parquet, json, or jsonl.")


def default_output_path(schema_name: str, fmt: str) -> str:
    return f"{schema_name}.{normalize_fmt(fmt)}"
