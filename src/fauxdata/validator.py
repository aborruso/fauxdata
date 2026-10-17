"""Validation of datasets using pointblank."""

from __future__ import annotations

import pointblank as pb
import polars as pl

from fauxdata.schema import SchemaConfig, ValidationRule


def validate_dataset(df: pl.DataFrame, schema: SchemaConfig) -> tuple[bool, list[dict]]:
    """
    Run pointblank validation rules against df.
    Returns (all_passed, results_list).
    """
    if not schema.validation_rules:
        return True, []

    v = pb.Validate(
        data=df,
        tbl_name=schema.name,
        thresholds=pb.Thresholds(warning=1),
    )

    for rule in schema.validation_rules:
        _add_rule(v, rule)

    v.interrogate()

    all_passed = v.all_passed()
    results = _extract_results(v, schema.validation_rules)
    return all_passed, results


def _add_rule(v: pb.Validate, rule: ValidationRule) -> None:
    # Value rules ignore nulls (na_pass=True): nulls are checked by col_vals_not_null
    r = rule.rule

    if r == "col_vals_not_null":
        cols = rule.columns or ([rule.column] if rule.column else [])
        for col in cols:
            v.col_vals_not_null(columns=col)

    elif r == "col_vals_between":
        v.col_vals_between(columns=rule.column, left=rule.min, right=rule.max, na_pass=True)

    elif r == "col_vals_gt":
        v.col_vals_gt(columns=rule.column, value=rule.min, na_pass=True)

    elif r == "col_vals_lt":
        v.col_vals_lt(columns=rule.column, value=rule.max, na_pass=True)

    elif r == "col_vals_ge":
        v.col_vals_ge(columns=rule.column, value=rule.min, na_pass=True)

    elif r == "col_vals_le":
        v.col_vals_le(columns=rule.column, value=rule.max, na_pass=True)

    elif r == "col_vals_regex":
        v.col_vals_regex(columns=rule.column, pattern=rule.pattern, na_pass=True)

    elif r == "col_vals_in_set":
        # col_vals_in_set has no na_pass: allowing None has the same effect
        v.col_vals_in_set(columns=rule.column, set=[*rule.values, None])

    elif r == "col_vals_str_len":
        v.col_vals_str_len(columns=rule.column, min_val=rule.min, max_val=rule.max, na_pass=True)

    elif r == "rows_distinct":
        cols = rule.columns or ([rule.column] if rule.column else None)
        # rows with a null key are not duplicates of each other (as in SQL UNIQUE)
        pre = (lambda df: df.drop_nulls(subset=cols)) if cols else None
        v.rows_distinct(columns_subset=cols, pre=pre)

    elif r == "col_exists":
        cols = rule.columns or ([rule.column] if rule.column else [])
        for col in cols:
            v.col_exists(columns=col)


def _extract_results(v: pb.Validate, rules: list[ValidationRule]) -> list[dict]:
    """Extract per-step results as a list of dicts."""
    # validation_info carries active and eval_error, used to flag steps that could not run
    steps = {s.i: s for s in v.validation_info}
    results = []
    # Build a flat list of steps (one per column for multi-column rules)
    step = 1
    for rule in rules:
        if rule.rule in ("col_vals_not_null", "col_exists"):
            cols = rule.columns or ([rule.column] if rule.column else [])
            for col in cols:
                results.append(_get_step(steps, step, rule.rule, col))
                step += 1
        else:
            col = rule.column or (", ".join(rule.columns) if rule.columns else "-")
            results.append(_get_step(steps, step, rule.rule, col))
            step += 1
    return results


def _get_step(steps: dict, i: int, rule: str, column: str) -> dict:
    s = steps.get(i)
    # pointblank deactivates a step it cannot run (e.g. a missing column) and flags eval_error
    evaluated = s is not None and bool(s.active) and not s.eval_error
    passed = (s.n_passed if s else 0) or 0
    failed = (s.n_failed if s else 0) or 0
    total = passed + failed
    return {
        "step": i,
        "rule": rule,
        "column": column,
        "passed": passed,
        "failed": failed,
        "total": total,
        "ok": evaluated and failed == 0,
        "evaluated": evaluated,
    }
