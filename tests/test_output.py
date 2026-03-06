"""Unit tests for output/export functions."""

import io
import sys
import pytest
import polars as pl

from fauxdata.output import normalize_fmt, default_output_path, export_dataset, write_stdout


# --- normalize_fmt ---

def test_normalize_fmt_passthrough():
    assert normalize_fmt("csv") == "csv"
    assert normalize_fmt("parquet") == "parquet"
    assert normalize_fmt("json") == "json"
    assert normalize_fmt("jsonl") == "jsonl"


def test_normalize_fmt_jsonlines_alias():
    assert normalize_fmt("jsonlines") == "jsonl"


# --- default_output_path ---

def test_default_output_path():
    assert default_output_path("people", "csv") == "people.csv"
    assert default_output_path("orders", "parquet") == "orders.parquet"
    assert default_output_path("events", "jsonlines") == "events.jsonl"


# --- export_dataset ---

@pytest.fixture
def sample_df():
    return pl.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})


def test_export_csv(tmp_path, sample_df):
    out = tmp_path / "out.csv"
    result = export_dataset(sample_df, out, "csv")
    assert result == out
    assert out.exists()
    loaded = pl.read_csv(out)
    assert loaded.shape == (2, 2)


def test_export_parquet(tmp_path, sample_df):
    out = tmp_path / "out.parquet"
    export_dataset(sample_df, out, "parquet")
    loaded = pl.read_parquet(out)
    assert loaded.shape == (2, 2)


def test_export_json(tmp_path, sample_df):
    out = tmp_path / "out.json"
    export_dataset(sample_df, out, "json")
    assert out.exists()


def test_export_jsonl(tmp_path, sample_df):
    out = tmp_path / "out.jsonl"
    export_dataset(sample_df, out, "jsonl")
    assert out.exists()


def test_export_jsonlines_alias(tmp_path, sample_df):
    out = tmp_path / "out.jsonl"
    export_dataset(sample_df, out, "jsonlines")
    assert out.exists()


def test_export_creates_parent_dirs(tmp_path, sample_df):
    out = tmp_path / "nested" / "deep" / "out.csv"
    export_dataset(sample_df, out, "csv")
    assert out.exists()


def test_export_unsupported_format(tmp_path, sample_df):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_dataset(sample_df, tmp_path / "out.xlsx", "xlsx")


# --- write_stdout ---

def test_write_stdout_csv(sample_df, capsys):
    write_stdout(sample_df, "csv")
    captured = capsys.readouterr()
    assert "id" in captured.out
    assert "Alice" in captured.out


def test_write_stdout_json(sample_df, capsys):
    write_stdout(sample_df, "json")
    captured = capsys.readouterr()
    assert "Alice" in captured.out


def test_write_stdout_jsonl(sample_df, capsys):
    write_stdout(sample_df, "jsonl")
    captured = capsys.readouterr()
    assert "Alice" in captured.out


def test_write_stdout_unsupported(sample_df):
    with pytest.raises(ValueError, match="Unsupported format"):
        write_stdout(sample_df, "xlsx")
