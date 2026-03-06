"""Unit tests for schema parsing."""

import pytest
import textwrap
from pathlib import Path

from fauxdata.schema import load_schema, _parse_schema, SchemaConfig, ColumnSchema


# --- _parse_schema ---

def test_parse_schema_minimal():
    data = {"name": "test", "columns": {"id": {"type": "int"}}}
    schema = _parse_schema(data)
    assert schema.name == "test"
    assert schema.rows == 100  # default
    assert len(schema.columns) == 1
    assert schema.columns[0].name == "id"


def test_parse_schema_missing_name():
    with pytest.raises(ValueError, match="name"):
        _parse_schema({"columns": {"id": {"type": "int"}}})


def test_parse_schema_missing_columns():
    with pytest.raises(ValueError, match="columns"):
        _parse_schema({"name": "test"})


def test_parse_schema_defaults():
    schema = _parse_schema({"name": "x", "columns": {"v": {"type": "bool"}}})
    assert schema.locale == "US"
    assert schema.output_format == "csv"
    assert schema.seed is None
    assert schema.output_path is None


def test_parse_schema_custom_values():
    data = {
        "name": "orders",
        "rows": 500,
        "seed": 7,
        "locale": "IT",
        "output": {"format": "parquet", "path": "out/orders.parquet"},
        "columns": {"status": {"type": "string", "values": ["open", "closed"]}},
    }
    schema = _parse_schema(data)
    assert schema.rows == 500
    assert schema.seed == 7
    assert schema.locale == "IT"
    assert schema.output_format == "parquet"
    assert schema.output_path == "out/orders.parquet"
    assert schema.columns[0].values == ["open", "closed"]


# --- column parsing ---

def test_parse_column_invalid_type():
    with pytest.raises(ValueError, match="invalid type"):
        _parse_schema({"name": "x", "columns": {"v": {"type": "unknown"}}})


def test_parse_column_missing_type():
    with pytest.raises(ValueError, match="type"):
        _parse_schema({"name": "x", "columns": {"v": {}}})


def test_parse_column_invalid_preset():
    with pytest.raises(ValueError, match="unknown preset"):
        _parse_schema({"name": "x", "columns": {"v": {"type": "string", "preset": "not_a_preset"}}})


def test_parse_column_valid_preset():
    schema = _parse_schema({"name": "x", "columns": {"email": {"type": "string", "preset": "email"}}})
    assert schema.columns[0].preset == "email"


def test_parse_column_unique_nullable():
    schema = _parse_schema({
        "name": "x",
        "columns": {"id": {"type": "int", "unique": True, "nullable": False}},
    })
    col = schema.columns[0]
    assert col.unique is True
    assert col.nullable is False


# --- validation rules ---

def test_parse_validation_rules():
    data = {
        "name": "x",
        "columns": {"age": {"type": "int"}},
        "validation": [
            {"rule": "col_vals_between", "column": "age", "min": 0, "max": 120},
        ],
    }
    schema = _parse_schema(data)
    assert len(schema.validation_rules) == 1
    rule = schema.validation_rules[0]
    assert rule.rule == "col_vals_between"
    assert rule.min == 0
    assert rule.max == 120


def test_parse_invalid_rule():
    data = {
        "name": "x",
        "columns": {"v": {"type": "int"}},
        "validation": [{"rule": "not_a_rule"}],
    }
    with pytest.raises(ValueError, match="Unknown validation rule"):
        _parse_schema(data)


# --- load_schema (file I/O) ---

def test_load_schema_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_schema("/nonexistent/path/schema.yml")


def test_load_schema_from_file(tmp_path, people_schema_path):
    schema = load_schema(people_schema_path)
    assert schema.name == "people"
    assert schema.rows == 1000
    assert schema.seed == 42
    assert schema.locale == "IT"
    assert any(c.name == "email" for c in schema.columns)


def test_load_schema_tmp_file(tmp_path):
    yaml_content = textwrap.dedent("""\
        name: tmp_test
        rows: 5
        columns:
          score:
            type: float
            min: 0.0
            max: 1.0
    """)
    p = tmp_path / "schema.yml"
    p.write_text(yaml_content)
    schema = load_schema(str(p))
    assert schema.name == "tmp_test"
    assert schema.columns[0].col_type == "float"
