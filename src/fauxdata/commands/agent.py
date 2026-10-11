"""fauxdata agent command - a Markdown guide for AI agents.

The lists of column types, presets and validation rules are built from the
constants in ``fauxdata.schema``, so the guide cannot drift from the code.
"""

from __future__ import annotations

import sys

from fauxdata import __version__
from fauxdata.schema import STRING_PRESETS, VALID_RULES, VALID_TYPES

TYPE_OPTIONS = {
    "int": "`min`, `max`, `unique`, `values`",
    "float": "`min`, `max`, `precision`, `unique`, `values`",
    "string": "`preset`, `values`, `pattern`, `unique`, `min_length`, `max_length`",
    "bool": "-",
    "date": "`min`, `max` (ISO date), `unique`",
    "datetime": "`min`, `max` (ISO datetime), `unique`",
}

RULE_PARAMS = {
    "col_vals_not_null": ("`columns`", "no nulls"),
    "col_vals_between": ("`column`, `min`, `max`", "value in range"),
    "col_vals_gt": ("`column`, `min`", "value > min"),
    "col_vals_lt": ("`column`, `max`", "value < max"),
    "col_vals_ge": ("`column`, `min`", "value >= min"),
    "col_vals_le": ("`column`, `max`", "value <= max"),
    "col_vals_regex": ("`column`, `pattern`", "value matches the regex"),
    "col_vals_in_set": ("`column`, `values`", "value in the allowed set"),
    "col_vals_str_len": ("`column`, `min` and/or `max`", "string length in range"),
    "rows_distinct": ("`columns`", "no duplicate keys (rows with a null key are skipped)"),
    "col_exists": ("`columns`", "column present"),
}

EXAMPLE = """\
name: people
rows: 1000
seed: 42
locale: IT
output:
  format: csv
  path: people.csv
columns:
  id:
    type: int
    unique: true
    min: 1
    max: 99999
  name:
    type: string
    preset: name
  email:
    type: string
    preset: email
  age:
    type: int
    min: 18
    max: 90
    null_probability: 0.05
  score:
    type: float
    min: 0
    max: 100
    precision: 1
  status:
    type: string
    values: [active, inactive, pending]
validation:
  - rule: col_vals_not_null
    columns: [id, name, email]
  - rule: col_vals_between
    column: age
    min: 18
    max: 90
  - rule: col_vals_in_set
    column: status
    values: [active, inactive, pending]
  - rule: rows_distinct
    columns: [id]
"""


def guide() -> str:
    types = "\n".join(f"| `{t}` | {TYPE_OPTIONS.get(t, '-')} |" for t in sorted(VALID_TYPES))
    rules = "\n".join(
        f"| `{r}` | {RULE_PARAMS.get(r, ('-', '-'))[0]} | {RULE_PARAMS.get(r, ('-', '-'))[1]} |"
        for r in sorted(VALID_RULES)
    )
    presets = ", ".join(f"`{p}`" for p in sorted(STRING_PRESETS))
    return f"""# fauxdata {__version__} - guide for AI agents

fauxdata generates realistic fake datasets from a YAML schema and validates datasets against the same schema.

## Workflow

1. Write a schema (see the example below), or infer one from a real table:
   `fauxdata infer real.csv --out schema.yml --json`
2. Generate data and validate it in one step:
   `fauxdata generate schema.yml --out data.csv --validate --json`
3. Validate any existing file against a schema:
   `fauxdata validate data.csv schema.yml --json`
4. Inspect a file (column stats and first rows):
   `fauxdata preview data.csv --json`

## Machine-readable output

- With `--json`, stdout contains exactly one JSON object and nothing else.
- On error: `{{"error": "..."}}` on stdout, exit code 1.
- `validate --json`: `{{"passed": bool, "rows": int, "results": [{{"step", "rule", "column", "passed", "failed", "total", "ok", "evaluated"}}]}}`
- `generate --json`: `{{"output_path", "format", "rows", "seed", "dry_run", "validation": null | {{"passed", "results"}}}}`
- `infer --json`: `{{"schema_path", "columns": [names], "validation_rules": int}}`
- `preview --json`: `{{"rows", "columns": [{{"name", "type", "nulls", "unique", "min", "max"}}], "head": [rows]}}`
- `evaluated: false` means the step could not run (e.g. its column is missing from the data); such a step has `ok: false`.
- `--json` cannot be combined with `--out -` (that mode writes data or YAML to stdout).

## Exit codes

- `0`: success, all validation rules passed
- `1`: error, or at least one validation rule failed

## Schema

Top-level keys: `name` (required), `columns` (required), `rows`, `seed`, `locale` (ISO country code, e.g. `US`, `IT`, `DE`, `JP`), `description`, `output.format` (`csv`, `parquet`, `json`, `jsonl`), `output.path`, `validation`.

Every column needs `type`. Any column also accepts `nullable` and `null_probability` (0-1).

| Type | Options |
|------|---------|
{types}

Notes:
- `precision` rounds floats; bounds with more decimals are moved inward so values never leave `min`/`max`.
- `values` restricts a column to a fixed set (strings, ints or floats).
- `pattern` generates strings matching a regex.

### String presets

{presets}

Presets are locale-aware and coherent within a row (the email matches the name, the city matches the country). Known limit: `unique: true` is not enforced on person and address presets such as `name`, `email`, `user_name`, `city` (pointblank issue #441). Validate with `rows_distinct` if uniqueness matters.

## Validation rules

| Rule | Parameters | Checks |
|------|------------|--------|
{rules}

Value rules ignore nulls: use `col_vals_not_null` to forbid them.

## Example schema

```yaml
{EXAMPLE}```
"""


def run():
    sys.stdout.write(guide())
