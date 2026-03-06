"""Tests for pattern, null_probability, and --version."""

import textwrap
import pytest
from typer.testing import CliRunner

from fauxdata.main import app
from fauxdata.schema import _parse_schema
from fauxdata.generator import generate_dataset
from fauxdata.schema import SchemaConfig, ColumnSchema

runner = CliRunner()


# --- null_probability in schema parsing ---

def test_null_probability_valid():
    schema = _parse_schema({
        "name": "x",
        "columns": {"score": {"type": "float", "null_probability": 0.2}},
    })
    assert schema.columns[0].null_probability == pytest.approx(0.2)


def test_null_probability_zero():
    schema = _parse_schema({
        "name": "x",
        "columns": {"score": {"type": "float", "null_probability": 0.0}},
    })
    assert schema.columns[0].null_probability == 0.0


def test_null_probability_one():
    schema = _parse_schema({
        "name": "x",
        "columns": {"score": {"type": "float", "null_probability": 1.0}},
    })
    assert schema.columns[0].null_probability == 1.0


def test_null_probability_invalid():
    with pytest.raises(ValueError, match="null_probability"):
        _parse_schema({
            "name": "x",
            "columns": {"score": {"type": "float", "null_probability": 1.5}},
        })


def test_null_probability_negative():
    with pytest.raises(ValueError, match="null_probability"):
        _parse_schema({
            "name": "x",
            "columns": {"score": {"type": "float", "null_probability": -0.1}},
        })


# --- pattern in schema parsing ---

def test_pattern_parsed():
    schema = _parse_schema({
        "name": "x",
        "columns": {"code": {"type": "string", "pattern": r"[A-Z]{3}-\d{4}"}},
    })
    assert schema.columns[0].pattern == r"[A-Z]{3}-\d{4}"


def test_pattern_default_none():
    schema = _parse_schema({
        "name": "x",
        "columns": {"name": {"type": "string", "preset": "name"}},
    })
    assert schema.columns[0].pattern is None


# --- generation with null_probability ---

def _make_schema(columns, rows=50, seed=42):
    return SchemaConfig(name="test", rows=rows, seed=seed, locale="US",
                        output_format="csv", columns=columns)


def test_generate_null_probability_produces_nulls():
    schema = _make_schema([
        ColumnSchema(name="val", col_type="int", min=1, max=100, null_probability=0.5)
    ], rows=200)
    df = generate_dataset(schema)
    null_count = df["val"].null_count()
    assert null_count > 0


def test_generate_zero_null_probability_no_nulls():
    schema = _make_schema([
        ColumnSchema(name="val", col_type="int", min=1, max=100, null_probability=0.0)
    ], rows=50)
    df = generate_dataset(schema)
    assert df["val"].null_count() == 0


# --- generation with pattern ---

def test_generate_string_pattern():
    schema = _make_schema([
        ColumnSchema(name="code", col_type="string", pattern=r"[A-Z]{2}\d{3}")
    ], rows=20)
    df = generate_dataset(schema)
    assert df["code"].dtype.is_(type(df["code"].dtype))
    assert df["code"].null_count() == 0


# --- CLI --version ---

def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.1" in result.output


def test_cli_version_short():
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert "0.1.1" in result.output


# --- CLI generate with new fields via YAML ---

def test_cli_generate_with_null_probability(tmp_path):
    schema_yaml = textwrap.dedent("""\
        name: nullable_test
        rows: 100
        seed: 1
        columns:
          id:
            type: int
            min: 1
            max: 999
          score:
            type: float
            min: 0.0
            max: 100.0
            null_probability: 0.3
    """)
    schema_path = tmp_path / "nullable.yml"
    schema_path.write_text(schema_yaml)
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", str(schema_path),
                                  "--out", str(out), "--format", "csv"])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_cli_generate_with_pattern(tmp_path):
    schema_yaml = textwrap.dedent(r"""
name: pattern_test
rows: 20
seed: 1
columns:
  code:
    type: string
    pattern: "[A-Z]{2}[0-9]{4}"
""")
    schema_path = tmp_path / "pattern.yml"
    schema_path.write_text(schema_yaml)
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", str(schema_path),
                                  "--out", str(out), "--format", "csv"])
    assert result.exit_code == 0, result.output
    assert out.exists()
