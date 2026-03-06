"""Shared fixtures for fauxdata tests."""

import pytest
import polars as pl

from fauxdata.schema import SchemaConfig, ColumnSchema, ValidationRule


@pytest.fixture
def minimal_schema():
    """A minimal SchemaConfig with one int and one string column."""
    return SchemaConfig(
        name="test",
        rows=10,
        seed=42,
        locale="US",
        output_format="csv",
        columns=[
            ColumnSchema(name="id", col_type="int", min=1, max=100, unique=True),
            ColumnSchema(name="name", col_type="string", preset="name"),
        ],
    )


@pytest.fixture
def simple_df():
    """A small deterministic DataFrame for validation tests."""
    return pl.DataFrame({
        "id": [1, 2, 3],
        "age": [25, 40, 55],
        "email": ["a@b.com", "c@d.com", "e@f.com"],
    })


@pytest.fixture
def people_schema_path():
    """Path to the existing people.yml schema."""
    from pathlib import Path
    return str(Path(__file__).parent.parent / "schemas" / "people.yml")
