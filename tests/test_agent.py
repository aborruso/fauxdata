"""Tests for the agent guide and --json output."""

import json
import re

import polars as pl
import pytest
import yaml
from typer.testing import CliRunner

from fauxdata.commands.agent import EXAMPLE, RULE_PARAMS, TYPE_OPTIONS, guide
from fauxdata.generator import generate_dataset
from fauxdata.main import app
from fauxdata.schema import STRING_PRESETS, VALID_RULES, VALID_TYPES, _parse_schema
from fauxdata.validator import validate_dataset

runner = CliRunner()


def _json(result):
    """stdout must be exactly one JSON object."""
    return json.loads(result.stdout)


# --- agent guide ---

def test_agent_command_prints_guide():
    result = runner.invoke(app, ["agent"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# fauxdata")


def test_guide_covers_every_type_rule_and_preset():
    text = guide()
    for name in VALID_TYPES | VALID_RULES | STRING_PRESETS:
        assert f"`{name}`" in text, name


def test_guide_tables_documented_for_every_type_and_rule():
    """Adding a type or rule to schema.py must come with its guide entry."""
    assert set(TYPE_OPTIONS) == VALID_TYPES
    assert set(RULE_PARAMS) == VALID_RULES


def test_guide_example_schema_generates_valid_data():
    schema = _parse_schema(yaml.safe_load(EXAMPLE))
    df = generate_dataset(schema, rows=200)
    passed, results = validate_dataset(df, schema)
    assert passed, results


def test_main_help_mentions_agent():
    result = runner.invoke(app, ["--help"])
    assert "fauxdata agent" in re.sub(r"\s+", " ", result.stdout)


# --- validate --json ---

def test_validate_json_pass(tmp_path, people_schema_path):
    data = tmp_path / "people.csv"
    runner.invoke(app, ["generate", str(people_schema_path), "-o", str(data)])
    result = runner.invoke(app, ["validate", str(data), str(people_schema_path), "--json"])
    assert result.exit_code == 0
    out = _json(result)
    assert out["passed"] is True
    assert out["rows"] > 0
    assert {"step", "rule", "column", "passed", "failed", "total", "ok"} <= set(out["results"][0])


def test_validate_json_fail(tmp_path):
    schema = tmp_path / "s.yml"
    schema.write_text("name: s\ncolumns:\n  n:\n    type: int\nvalidation:\n"
                      "  - rule: col_vals_between\n    column: n\n    min: 1\n    max: 5\n")
    data = tmp_path / "d.csv"
    pl.DataFrame({"n": [1, 9]}).write_csv(data)
    result = runner.invoke(app, ["validate", str(data), str(schema), "--json"])
    assert result.exit_code == 1
    out = _json(result)
    assert out["passed"] is False
    assert out["results"][0]["failed"] == 1


@pytest.mark.parametrize("args", [
    ["validate", "missing.csv", "missing.yml", "--json"],
    ["validate", "data.txt", "schemas/people.yml", "--json"],
    ["preview", "missing.csv", "--json"],
    ["infer", "missing.csv", "--json"],
    ["generate", "missing.yml", "--json"],
])
def test_json_errors(args):
    result = runner.invoke(app, args)
    assert result.exit_code == 1
    assert "error" in _json(result)


# --- preview --json ---

def test_preview_json(tmp_path):
    data = tmp_path / "d.csv"
    pl.DataFrame({"n": [1, 2, None], "s": ["a", "b", "c"]}).write_csv(data)
    result = runner.invoke(app, ["preview", str(data), "--rows", "2", "--json"])
    assert result.exit_code == 0
    out = _json(result)
    assert out["rows"] == 3
    n = out["columns"][0]
    assert (n["name"], n["nulls"], n["min"], n["max"]) == ("n", 1, 1, 2)
    assert out["columns"][1]["min"] is None
    assert len(out["head"]) == 2


# --- infer --json ---

def test_infer_json(tmp_path):
    data = tmp_path / "real.csv"
    pl.DataFrame({"id": list(range(30)), "s": ["a", "b"] * 15}).write_csv(data)
    out_yml = tmp_path / "inferred.yml"
    result = runner.invoke(app, ["infer", str(data), "-o", str(out_yml), "--json"])
    assert result.exit_code == 0
    out = _json(result)
    assert out["schema_path"] == str(out_yml)
    assert out["columns"] == ["id", "s"]
    assert out["validation_rules"] > 0
    assert out_yml.exists()


def test_infer_json_refuses_stdout(tmp_path):
    data = tmp_path / "real.csv"
    pl.DataFrame({"id": [1, 2]}).write_csv(data)
    result = runner.invoke(app, ["infer", str(data), "-o", "-", "--json"])
    assert result.exit_code == 1
    assert "error" in _json(result)


# --- generate --json ---

@pytest.mark.parametrize("validate", [False, True])
def test_generate_json(tmp_path, people_schema_path, validate):
    data = tmp_path / "out.csv"
    args = ["generate", str(people_schema_path), "-o", str(data), "--rows", "50", "--json"]
    result = runner.invoke(app, args + (["--validate"] if validate else []))
    assert result.exit_code == 0
    out = _json(result)
    assert out["output_path"] == str(data)
    assert out["rows"] == 50
    assert data.exists()
    if validate:
        assert out["validation"]["passed"] is True
    else:
        assert out["validation"] is None


def test_generate_json_dry_run(tmp_path, people_schema_path):
    data = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", str(people_schema_path), "-o", str(data), "--dry-run", "--json"])
    assert result.exit_code == 0
    assert _json(result)["dry_run"] is True
    assert not data.exists()


def test_generate_json_refuses_stdout(people_schema_path):
    result = runner.invoke(app, ["generate", str(people_schema_path), "-o", "-", "--json"])
    assert result.exit_code == 1
    assert "error" in _json(result)
