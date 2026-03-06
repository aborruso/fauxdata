"""Integration tests for dataset validation."""

import pytest
import polars as pl

from fauxdata.schema import SchemaConfig, ColumnSchema, ValidationRule
from fauxdata.validator import validate_dataset


def _schema_with_rules(rules):
    return SchemaConfig(
        name="test",
        rows=3,
        seed=42,
        locale="US",
        output_format="csv",
        columns=[ColumnSchema(name="id", col_type="int")],
        validation_rules=rules,
    )


def test_validate_no_rules(simple_df):
    schema = _schema_with_rules([])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is True
    assert results == []


def test_validate_not_null_pass(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_not_null", columns=["id", "age"])
    ])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is True
    assert all(r["ok"] for r in results)


def test_validate_not_null_fail():
    df = pl.DataFrame({"id": [1, None, 3]})
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_not_null", column="id")
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is False
    assert results[0]["failed"] == 1


def test_validate_between_pass(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_between", column="age", min=0, max=100)
    ])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is True


def test_validate_between_fail(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_between", column="age", min=0, max=30)
    ])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is False


def test_validate_regex_pass(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_regex", column="email", pattern=r"^[^@]+@[^@]+\.[^@]+$")
    ])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is True


def test_validate_regex_fail():
    df = pl.DataFrame({"email": ["valid@x.com", "not-an-email"]})
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_regex", column="email", pattern=r"^[^@]+@[^@]+\.[^@]+$")
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is False


def test_validate_in_set_pass():
    df = pl.DataFrame({"status": ["open", "closed", "open"]})
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_in_set", column="status", values=["open", "closed"])
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is True


def test_validate_in_set_fail():
    df = pl.DataFrame({"status": ["open", "pending"]})
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_in_set", column="status", values=["open", "closed"])
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is False


def test_validate_rows_distinct_pass(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="rows_distinct", columns=["id"])
    ])
    passed, results = validate_dataset(simple_df, schema)
    assert passed is True


def test_validate_rows_distinct_fail():
    df = pl.DataFrame({"id": [1, 1, 2]})
    schema = _schema_with_rules([
        ValidationRule(rule="rows_distinct", columns=["id"])
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is False


def test_validate_results_structure(simple_df):
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_not_null", column="id")
    ])
    _, results = validate_dataset(simple_df, schema)
    assert len(results) == 1
    r = results[0]
    assert set(r.keys()) == {"step", "rule", "column", "passed", "failed", "total", "ok"}
