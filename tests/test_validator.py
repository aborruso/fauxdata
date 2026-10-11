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
    assert set(r.keys()) == {"step", "rule", "column", "passed", "failed", "total", "ok", "evaluated"}


def test_validate_str_len_counts():
    """Lengths outside min/max fail; nulls are ignored (checked by col_vals_not_null)."""
    df = pl.DataFrame({"s": ["a", "ab", "abcd", "abcdefgh", None]})
    schema = _schema_with_rules([ValidationRule(rule="col_vals_str_len", column="s", min=2, max=5)])
    passed, results = validate_dataset(df, schema)
    assert passed is False
    assert results[0]["failed"] == 2  # "a" and "abcdefgh"
    assert results[0]["passed"] == 3  # "ab", "abcd", null


def test_validate_str_len_max_only():
    df = pl.DataFrame({"s": ["a", "abc", "abcdef"]})
    schema = _schema_with_rules([ValidationRule(rule="col_vals_str_len", column="s", max=3)])
    passed, results = validate_dataset(df, schema)
    assert passed is False
    assert results[0]["failed"] == 1


@pytest.mark.parametrize("rule", [
    ValidationRule(rule="col_vals_between", column="v", min=1, max=10),
    ValidationRule(rule="col_vals_gt", column="v", min=0),
    ValidationRule(rule="col_vals_lt", column="v", max=11),
    ValidationRule(rule="col_vals_ge", column="v", min=1),
    ValidationRule(rule="col_vals_le", column="v", max=10),
    ValidationRule(rule="col_vals_in_set", column="v", values=[1, 5, 10]),
])
def test_validate_value_rules_ignore_nulls(rule):
    """Nulls are checked by col_vals_not_null, not by value rules."""
    df = pl.DataFrame({"v": [1, None, 5, None, 10]})
    passed, results = validate_dataset(df, _schema_with_rules([rule]))
    assert passed is True, results


def test_validate_regex_ignores_nulls():
    df = pl.DataFrame({"v": ["ab", None, "cd"]})
    rule = ValidationRule(rule="col_vals_regex", column="v", pattern="^[a-z]+$")
    passed, results = validate_dataset(df, _schema_with_rules([rule]))
    assert passed is True, results


def test_validate_rows_distinct_ignores_nulls():
    """Null keys are not duplicates of each other; real duplicates still fail."""
    ok = pl.DataFrame({"k": ["a", None, "b", None]})
    rule = ValidationRule(rule="rows_distinct", columns=["k"])
    passed, results = validate_dataset(ok, _schema_with_rules([rule]))
    assert passed is True, results

    dup = pl.DataFrame({"k": ["a", None, "a", None]})
    passed, results = validate_dataset(dup, _schema_with_rules([rule]))
    assert passed is False
    assert results[0]["failed"] == 2


def test_validate_missing_column_step_not_ok():
    """A step on a column missing from the data is reported as not evaluated, not as passed."""
    df = pl.DataFrame({"id": [1, 2, 3]})
    schema = _schema_with_rules([
        ValidationRule(rule="col_vals_not_null", columns=["id"]),
        ValidationRule(rule="col_vals_between", column="missing", min=1, max=2),
    ])
    passed, results = validate_dataset(df, schema)
    assert passed is False
    assert results[0]["ok"] is True and results[0]["evaluated"] is True
    assert results[1]["ok"] is False and results[1]["evaluated"] is False
