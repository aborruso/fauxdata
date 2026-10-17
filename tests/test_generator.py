"""Integration tests for dataset generation."""

import pytest
import polars as pl

from fauxdata.generator import generate_dataset
from fauxdata.schema import SchemaConfig, ColumnSchema


def _make_schema(columns, rows=10, seed=42):
    return SchemaConfig(name="test", rows=rows, seed=seed, locale="US",
                        output_format="csv", columns=columns)


def test_generate_returns_dataframe(minimal_schema):
    df = generate_dataset(minimal_schema, rows=10, seed=42)
    assert isinstance(df, pl.DataFrame)


def test_generate_row_count(minimal_schema):
    df = generate_dataset(minimal_schema, rows=20, seed=42)
    assert df.height == 20


def test_generate_column_names(minimal_schema):
    df = generate_dataset(minimal_schema, rows=5, seed=42)
    assert "id" in df.columns
    assert "name" in df.columns


def test_generate_int_column():
    schema = _make_schema([ColumnSchema(name="age", col_type="int", min=18, max=65)])
    df = generate_dataset(schema)
    assert df["age"].dtype in (pl.Int64, pl.Int32)
    assert df["age"].min() >= 18
    assert df["age"].max() <= 65


def test_generate_float_column():
    schema = _make_schema([ColumnSchema(name="score", col_type="float", min=0.0, max=1.0)])
    df = generate_dataset(schema)
    assert df["score"].dtype in (pl.Float64, pl.Float32)
    assert df["score"].min() >= 0.0
    assert df["score"].max() <= 1.0


def test_generate_bool_column():
    schema = _make_schema([ColumnSchema(name="active", col_type="bool")])
    df = generate_dataset(schema)
    assert df["active"].dtype == pl.Boolean


def test_generate_date_column():
    schema = _make_schema([
        ColumnSchema(name="signup", col_type="date", min="2020-01-01", max="2024-12-31")
    ])
    df = generate_dataset(schema)
    assert df["signup"].dtype == pl.Date


def test_generate_string_preset():
    schema = _make_schema([ColumnSchema(name="email", col_type="string", preset="email")])
    df = generate_dataset(schema)
    assert df["email"].dtype == pl.String
    # basic email shape check
    assert df["email"].str.contains("@").all()


def test_generate_string_values():
    schema = _make_schema([
        ColumnSchema(name="status", col_type="string", values=["open", "closed"])
    ])
    df = generate_dataset(schema, rows=50)
    unique_vals = set(df["status"].unique().to_list())
    assert unique_vals <= {"open", "closed"}


def test_generate_unique_column():
    schema = _make_schema([ColumnSchema(name="id", col_type="int", min=1, max=9999, unique=True)])
    df = generate_dataset(schema, rows=50)
    assert df["id"].n_unique() == 50


def test_generate_seed_reproducibility(minimal_schema):
    df1 = generate_dataset(minimal_schema, rows=10, seed=99)
    df2 = generate_dataset(minimal_schema, rows=10, seed=99)
    assert df1.equals(df2)


def test_generate_float_precision():
    """float `precision` rounds generated values to the requested decimals."""
    schema = _make_schema([ColumnSchema(name="f", col_type="float", min=1.0, max=200.0, precision=2)])
    df = generate_dataset(schema, rows=20, seed=1)
    for v in df["f"].to_list():
        assert v == round(v, 2)


def test_generate_float_precision_stays_in_range():
    """Rounding must not push values outside min/max (e.g. 9.996 -> 10.0 > 9.999)."""
    schema = _make_schema([ColumnSchema(name="f", col_type="float", min=9.99, max=9.999, precision=2)])
    df = generate_dataset(schema, rows=200, seed=1)
    assert df["f"].min() >= 9.99
    assert df["f"].max() <= 9.999


def test_generate_unique_coherent_presets():
    """unique is enforced on coherent presets (pointblank >= 1.1.0, posit-dev/pointblank#441)."""
    schema = _make_schema([ColumnSchema(name="name", col_type="string", preset="name", unique=True),
                           ColumnSchema(name="email", col_type="string", preset="email", unique=True)])
    df = generate_dataset(schema, rows=2000, seed=1)
    assert df["name"].n_unique() == 2000
    assert df["email"].n_unique() == 2000


def test_generate_float_precision_unique():
    """A unique float column stays unique after rounding."""
    schema = _make_schema([ColumnSchema(name="f", col_type="float", min=0.0, max=1.0,
                                        precision=1, unique=True)])
    df = generate_dataset(schema, rows=8, seed=1)
    assert df["f"].n_unique() == 8


def test_generate_float_precision_no_value_fits():
    """Clear error when no value with the given decimals fits in the range."""
    schema = _make_schema([ColumnSchema(name="f", col_type="float", min=1.001, max=1.009, precision=2)])
    with pytest.raises(ValueError, match="no value with 2 decimals"):
        generate_dataset(schema)


def test_generate_all_types():
    """Generate a dataset with all supported column types."""
    schema = _make_schema([
        ColumnSchema(name="i", col_type="int", min=0, max=100),
        ColumnSchema(name="f", col_type="float", min=0.0, max=1.0),
        ColumnSchema(name="s", col_type="string", preset="name"),
        ColumnSchema(name="b", col_type="bool"),
        ColumnSchema(name="d", col_type="date", min="2020-01-01", max="2024-12-31"),
        ColumnSchema(name="dt", col_type="datetime"),
    ])
    df = generate_dataset(schema, rows=5)
    assert df.height == 5
    assert set(["i", "f", "s", "b", "d", "dt"]) <= set(df.columns)


@pytest.mark.parametrize("col_type,values", [("int", [3, 7, 11]), ("float", [0.5, 1.25])])
def test_generate_numeric_values(col_type, values):
    """`values` on numeric columns restricts generation to that set (infer emits it)."""
    schema = _make_schema([ColumnSchema(name="n", col_type=col_type, values=values)])
    df = generate_dataset(schema, rows=200, seed=1)
    assert set(df["n"].to_list()) <= set(values)
