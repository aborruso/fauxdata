"""Tests for the infer command and schema inference (pointblank >=0.25)."""

import polars as pl
import pytest
import yaml

from fauxdata.commands.infer import (
    _col_type_from_dtype,
    _field_to_spec,
    _build_validation,
)
from fauxdata.commands import infer as infer_mod
from fauxdata.schema import load_schema
from fauxdata.generator import generate_dataset
from fauxdata.validator import validate_dataset


# --- dtype mapping ---

@pytest.mark.parametrize("dtype,expected", [
    ("Int64", "int"),
    ("UInt32", "int"),
    ("Float64", "float"),
    ("String", "string"),
    ("Utf8", "string"),
    ("Boolean", "bool"),
    ("Date", "date"),
    ("Datetime(time_unit='us')", "datetime"),
    ("SomethingWeird", "string"),  # fallback
])
def test_col_type_from_dtype(dtype, expected):
    assert _col_type_from_dtype(dtype) == expected


# --- field -> spec ---

def _spec_of(df, col):
    import pointblank as pb
    s = pb.schema_from_tbl(df)
    fields = dict(s.columns)
    return _field_to_spec(fields[col])


def test_field_to_spec_int_range_unique():
    df = pl.DataFrame({"id": [1, 2, 3, 4, 5]})
    spec = _spec_of(df, "id")
    assert spec["type"] == "int"
    assert spec["min"] == 1
    assert spec["max"] == 5
    assert spec["unique"] is True


def test_field_to_spec_email_preset():
    df = pl.DataFrame({"email": [f"u{i}@ex.com" for i in range(6)]})
    spec = _spec_of(df, "email")
    assert spec["type"] == "string"
    assert spec.get("preset") == "email"


def test_field_to_spec_categorical_values():
    df = pl.DataFrame({"status": ["a", "b", "a", "b", "a", "b"]})
    spec = _spec_of(df, "status")
    assert spec["type"] == "string"
    assert sorted(spec["values"]) == ["a", "b"]


# --- validation derivation ---

def test_build_validation_rules():
    columns = [
        ("id", {"type": "int", "unique": True, "min": 1, "max": 9}),
        ("status", {"type": "string", "values": ["a", "b"]}),
        ("note", {"type": "string", "nullable": True}),
    ]
    rules = _build_validation(columns)
    kinds = [r["rule"] for r in rules]
    assert "col_vals_not_null" in kinds
    assert "col_vals_between" in kinds
    assert "col_vals_in_set" in kinds
    assert "rows_distinct" in kinds
    # nullable column excluded from not_null
    nn = next(r for r in rules if r["rule"] == "col_vals_not_null")
    assert "note" not in nn["columns"]
    assert "id" in nn["columns"]


def test_build_validation_in_set_is_copy():
    """values in the rule must not alias the column spec list (no YAML anchor)."""
    vals = ["a", "b"]
    columns = [("status", {"type": "string", "values": vals})]
    rules = _build_validation(columns)
    rule_vals = next(r for r in rules if r["rule"] == "col_vals_in_set")["values"]
    assert rule_vals == vals
    assert rule_vals is not vals


# --- end-to-end round trip ---

def test_infer_roundtrip(tmp_path):
    real = pl.DataFrame({
        "id": list(range(1, 9)),
        "email": [f"u{i}@ex.com" for i in range(8)],
        "age": [20, 35, 40, 55, 60, 25, 33, 48],
        "status": ["active", "inactive"] * 4,
        "price": [1.5, 2.0, 3.25, 4.0, 5.5, 2.2, 3.3, 4.4],
    })
    src = tmp_path / "real.csv"
    real.write_csv(src)

    out = tmp_path / "inferred.yml"
    infer_mod.run(dataset_path=str(src), out=str(out))

    assert out.exists()
    data = yaml.safe_load(out.read_text())
    assert set(data["columns"]) == {"id", "email", "age", "status", "price"}
    assert data["columns"]["email"]["preset"] == "email"
    assert data["rows"] == 8

    # the inferred schema generates valid data that passes its own rules.
    # Use the schema's own row count (calibrated to the source size): inferred
    # unique columns over a narrow integer range cannot yield many more rows.
    schema = load_schema(out)
    df = generate_dataset(schema)
    all_passed, _ = validate_dataset(df, schema)
    assert all_passed


def test_infer_datetime_from_csv_typed(tmp_path):
    """date/datetime CSV columns are inferred as typed, not frozen as categorical strings."""
    import datetime
    real = pl.DataFrame({
        "ts": [datetime.datetime(2020, 1, 1, 8, 30) + datetime.timedelta(days=i * 40) for i in range(8)],
    })
    src = tmp_path / "dt.csv"
    real.write_csv(src)
    out = tmp_path / "dt.yml"
    infer_mod.run(dataset_path=str(src), out=str(out))
    data = yaml.safe_load(out.read_text())
    assert data["columns"]["ts"]["type"] == "datetime"
    # round-trips through generation
    schema = load_schema(out)
    assert len(generate_dataset(schema)) == schema.rows


def test_generate_unique_range_too_narrow_clear_error():
    """Amplifying a unique column beyond its range raises a clear, named error."""
    from fauxdata.schema import SchemaConfig, ColumnSchema
    schema = SchemaConfig(
        name="x", rows=5, seed=1,
        columns=[ColumnSchema(name="id", col_type="int", min=1, max=5, unique=True)],
    )
    with pytest.raises(ValueError, match="too narrow a range"):
        generate_dataset(schema, rows=100)


def test_infer_unsupported_format(tmp_path):
    import typer
    bad = tmp_path / "data.xyz"
    bad.write_text("nope")
    with pytest.raises(typer.Exit):
        infer_mod.run(dataset_path=str(bad))


def test_infer_stdout(tmp_path, capsys):
    real = pl.DataFrame({"id": [1, 2, 3]})
    src = tmp_path / "r.csv"
    real.write_csv(src)
    infer_mod.run(dataset_path=str(src), out="-")
    captured = capsys.readouterr()
    assert "columns:" in captured.out
    assert "name: r" in captured.out
