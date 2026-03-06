"""Data generation using pointblank native API."""

from __future__ import annotations

import pointblank as pb
import polars as pl

from fauxdata.schema import ColumnSchema, SchemaConfig


def generate_dataset(schema: SchemaConfig, rows: int | None = None, seed: int | None = None) -> pl.DataFrame:
    """Generate a Polars DataFrame from a SchemaConfig using pointblank."""
    n = rows if rows is not None else schema.rows
    rng_seed = seed if seed is not None else schema.seed

    pb_schema = _build_pb_schema(schema)
    country = schema.locale or "US"

    df = pb.generate_dataset(pb_schema, n=n, seed=rng_seed, country=country)
    return df


def _build_pb_schema(schema: SchemaConfig) -> pb.Schema:
    """Convert a SchemaConfig to a pointblank Schema."""
    kwargs = {}
    for col in schema.columns:
        kwargs[col.name] = _col_to_field(col)
    return pb.Schema(**kwargs)


def _col_to_field(col: ColumnSchema):
    """Convert a ColumnSchema to a pointblank field spec."""
    nullable = col.nullable or (col.null_probability is not None and col.null_probability > 0)
    unique = col.unique
    # Build optional kwargs only when null_probability is explicitly set
    np_kwargs = {"null_probability": col.null_probability} if col.null_probability is not None else {}

    if col.col_type == "int":
        return pb.int_field(
            min_val=int(col.min) if col.min is not None else None,
            max_val=int(col.max) if col.max is not None else None,
            nullable=nullable,
            unique=unique,
            **np_kwargs,
        )

    elif col.col_type == "float":
        return pb.float_field(
            min_val=float(col.min) if col.min is not None else None,
            max_val=float(col.max) if col.max is not None else None,
            nullable=nullable,
            unique=unique,
            **np_kwargs,
        )

    elif col.col_type == "bool":
        return pb.bool_field(nullable=nullable, **np_kwargs)

    elif col.col_type == "date":
        return pb.date_field(
            min_date=str(col.min) if col.min is not None else None,
            max_date=str(col.max) if col.max is not None else None,
            nullable=nullable,
            unique=unique,
            **np_kwargs,
        )

    elif col.col_type == "datetime":
        return pb.datetime_field(
            min_date=str(col.min) if col.min is not None else None,
            max_date=str(col.max) if col.max is not None else None,
            nullable=nullable,
            unique=unique,
            **np_kwargs,
        )

    elif col.col_type == "string":
        if col.values:
            return pb.string_field(allowed=col.values, nullable=nullable, **np_kwargs)
        elif col.pattern:
            return pb.string_field(pattern=col.pattern, nullable=nullable, unique=unique, **np_kwargs)
        elif col.preset:
            return pb.string_field(preset=col.preset, nullable=nullable, unique=unique, **np_kwargs)
        else:
            return pb.string_field(nullable=nullable, unique=unique, **np_kwargs)

    else:
        return pb.string_field(nullable=nullable, **np_kwargs)
