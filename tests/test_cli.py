"""Smoke tests for the fauxdata CLI using typer's CliRunner."""

import textwrap
import pytest
from typer.testing import CliRunner

from fauxdata.main import app

runner = CliRunner()


def test_cli_no_args():
    """Running fauxdata with no args should show help."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "fauxdata" in result.output.lower() or "generate" in result.output.lower()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output


def test_cli_generate_help():
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--rows" in result.output
    assert "--format" in result.output


def test_cli_generate_csv(tmp_path, people_schema_path):
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", people_schema_path, "--rows", "5",
                                  "--out", str(out), "--format", "csv", "--seed", "1"])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_cli_generate_json(tmp_path, people_schema_path):
    out = tmp_path / "out.json"
    result = runner.invoke(app, ["generate", people_schema_path, "--rows", "5",
                                  "--out", str(out), "--format", "json", "--seed", "1"])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_cli_generate_parquet(tmp_path, people_schema_path):
    out = tmp_path / "out.parquet"
    result = runner.invoke(app, ["generate", people_schema_path, "--rows", "5",
                                  "--out", str(out), "--format", "parquet", "--seed", "1"])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_cli_generate_stdout(people_schema_path, capsys):
    result = runner.invoke(app, ["generate", people_schema_path, "--rows", "3",
                                  "--out", "-", "--format", "csv", "--seed", "1"])
    assert result.exit_code == 0, result.output


def test_cli_generate_with_validate(tmp_path, people_schema_path):
    out = tmp_path / "out.csv"
    result = runner.invoke(app, ["generate", people_schema_path, "--rows", "10",
                                  "--out", str(out), "--format", "csv",
                                  "--seed", "42", "--validate"])
    assert result.exit_code == 0, result.output


def test_cli_generate_missing_schema(tmp_path):
    result = runner.invoke(app, ["generate", "/nonexistent/schema.yml"])
    assert result.exit_code != 0


def test_cli_validate(tmp_path, people_schema_path):
    """Generate a file then validate it."""
    out = tmp_path / "people.csv"
    runner.invoke(app, ["generate", people_schema_path, "--rows", "10",
                         "--out", str(out), "--format", "csv", "--seed", "42"])
    result = runner.invoke(app, ["validate", str(out), people_schema_path])
    assert result.exit_code == 0, result.output


def test_cli_preview(tmp_path, people_schema_path):
    out = tmp_path / "people.csv"
    runner.invoke(app, ["generate", people_schema_path, "--rows", "20",
                         "--out", str(out), "--format", "csv", "--seed", "42"])
    result = runner.invoke(app, ["preview", str(out), "--rows", "5"])
    assert result.exit_code == 0, result.output


def test_cli_generate_inline_schema(tmp_path):
    """Test with a minimal inline schema written to a tmp file."""
    schema_yaml = textwrap.dedent("""\
        name: mini
        rows: 5
        columns:
          id:
            type: int
            min: 1
            max: 100
          label:
            type: string
            values: ["a", "b"]
    """)
    schema_path = tmp_path / "mini.yml"
    schema_path.write_text(schema_yaml)
    out = tmp_path / "mini.csv"
    result = runner.invoke(app, ["generate", str(schema_path),
                                  "--out", str(out), "--format", "csv", "--seed", "1"])
    assert result.exit_code == 0, result.output
    assert out.exists()
