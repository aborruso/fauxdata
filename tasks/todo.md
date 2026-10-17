# Upgrade to pointblank 1.0.1

Context: fauxdata is pinned to pointblank 0.25.0 (`uv.lock`). PyPI has 0.26.0, 0.27.0, 1.0.0 and 1.0.1 (7 October 2026). The release notes declare no breaking changes. From the new features we take three things: the dependency bump, `float_field(precision=)` (0.26) and `col_vals_str_len()` (1.0.0).

## Phase 1 - Dependency bump

- [x] `pyproject.toml`: `pointblank>=0.25` → `pointblank>=1.0.1`; `uv sync` → verify: `uv pip show pointblank` = 1.0.1
- [x] Full suite with no code changes → verify: `uv run pytest tests/ -q` all green (baseline 103 tests on 0.25, 103 passed on 1.0.1, coverage 83.28%)
- [x] Bundled schemas (people/orders/events): `generate` + `validate` → verify: all PASS as on 0.25
- [x] Same seed, same output: the three schemas generate byte-identical CSVs on 0.25.0 and 1.0.1
- [x] Nothing broke

Side effect: since 0.27.0 pointblank requires `anthropic[bedrock]>=0.68.0`, so installing fauxdata now also pulls in anthropic, boto3, botocore, pydantic, httpx2 and others (20 new packages in `uv.lock`). fauxdata does not use them. Unavoidable with `pointblank>=1.0.1`; worth a line in the release notes.

Why the minimum is 1.0.1 and not 1.0.0: with `polars>=1.0` a user can end up on Polars 2.x, and before 1.0.1 `col_vals_in_set` (which we use) fails when mixing ints and floats.

## Phase 2 - Native float precision

Today `generator.py` rounds after generation (`pl.col(...).round(precision)`), with the comment "pointblank has no float precision option".

- [x] Tests reproducing the two risks of post-generation rounding, before the change → both reproduced on the old code: `10.0` with `max: 9.999`; 6 distinct values out of 8 in a `unique` column
- [x] Checked the pointblank 1.0.1 source (`generate/generators.py`): it rounds each value inside generation and checks uniqueness after rounding (fixes `unique`), but still rounds past the bounds (does not fix range)
- [x] `_col_to_field`: pass `precision=col.precision` to `pb.float_field`; removed the `round_exprs` block → `unique` test green
- [x] Range fix (decided 2026-10-11): snap `min` up and `max` down to the precision grid before passing them to pointblank; clear `ValueError` when no value fits → range test and no-fit test green
- [x] README: new "Float precision" section, `precision` added to the `float` options (it was undocumented)
- [x] Full suite: 106 passed, coverage 83.50%; README example checked on 20,000 rows (all values within 1.0-199.99, all rounded to 2 decimals)

## Phase 3 - String length validation

`ColumnSchema` already has `min_length`/`max_length` and `infer` reads them, but there is no matching validation rule.

- [x] `schema.py`: `col_vals_str_len` added to `VALID_RULES` → parsing test green
- [x] `validator.py`: `col_vals_str_len` branch with `na_pass=True` (nulls are checked by `col_vals_not_null`) → tests on pass/fail counts, nulls ignored, max-only
- [x] `commands/infer.py` (`_build_validation`): rule emitted only for free-text strings → test with free-text, email preset and pattern columns
- [x] Round-trip infer → generate → validate (Python API, int threshold) → all PASS, including `col_vals_str_len`
- [x] README: `col_vals_str_len` in the rules table
- [x] Full suite: 111 passed, coverage 84.13%

### Pre-existing bugs found during phase 3 (present on 0.25.0 too)

1. [x] FIXED - `infer --categorical-threshold` from the CLI: typed `float`, so typer passed `20.0` even for the default; pointblank reads any float as a fraction of rows, so every non-preset string column became categorical with its real values copied into `values:`. Now whole numbers >= 1 are passed as int counts (`_threshold` in `infer.py`). CLI test added.
2. [x] FIXED - value rules (`between`, `gt/lt/ge/le`, `regex`, `in_set`) counted nulls as failures. Now `na_pass=True` (`in_set` has no `na_pass`: `None` is added to the allowed set). Tests for every rule.
3. [x] FIXED UPSTREAM (2026-10-17) - pointblank bug, not ours: `unique=True` is ignored for coherent presets (person, address, business, credit card: `email`, `name`, `city`, ...). `_generate_single_country()` routes them to `_generate_column_with_row_context()`, which never checks `field.unique` (still so on upstream `main` 4510729). Pure-pointblank reproducer: 2000 rows → `email` 1998 distinct, `city` 156, no error. Reported upstream: https://github.com/posit-dev/pointblank/issues/441 (2026-10-11). Fixed by posit-dev/pointblank#447, released in 1.1.0: fauxdata now requires `pointblank>=1.1.0`, test `test_generate_unique_coherent_presets` added, no fauxdata-side warning needed.
4. [x] FIXED - `infer` turned a low-cardinality int column into `values:`, but the generator ignored `values` for numeric columns (403/500 failures). Now `int`/`float` with `values` pass them as `allowed`. Tests: generator (int, float) + round-trip.
5. [x] FIXED - `rows_distinct` counted null keys as duplicates of each other (120/500 failures). Now rows with a null in the checked columns are excluded first (`pre=drop_nulls(subset)`, as in SQL UNIQUE); the reported total is the number of non-null rows. Test with nulls only (pass) and real duplicates (fail).
6. [ ] `unique` + `nullable` on a narrow int range: pointblank also needs unique values for the null rows, so even the source row count can't be generated (same on 0.25.0).

## Wrap-up

- [x] `LOG.md`: dated entry
- [x] Coverage not below 83.2%: now 85.14%, 119 passed
- [x] Package version → 0.2.0 (`pyproject.toml`, `__init__.py`, `uv.lock`); release only on request (see `RELEASING.md`)
- [x] Single commit (on user's ok) - `56cfe93`, released as 0.2.0

## Decisions (2026-10-11)

- Version: 0.2.0.
- Rule name: `col_vals_str_len`, as in pointblank.
- `infer` emits `col_vals_str_len` only for free-text strings. pointblank 0.25 returns lengths even for preset columns (email: `min_length=6, max_length=7` on a 5-row sample), but the generator applies `min_length`/`max_length` only to free-text strings: on preset/pattern columns the rule would fail on our own synthetic data. pointblank always gives both bounds or neither; the one-bound case only comes from hand-written YAML, and the validator handles it by passing `None`.
- "Later" ideas saved in `docs/future-ideas.md`.

## Open questions

- None.

## Phase 4 - Agent-friendly CLI (in 0.2.0, decided 2026-10-11)

Goal: a general-purpose agent can learn and drive fauxdata without reading the README and can parse every result.

- [x] `fauxdata agent` (`commands/agent.py`): Markdown guide on stdout (workflow, JSON output, exit codes, schema, types, presets, rules, example). Types, presets and rules come from `schema.py` constants → tests: every type/rule/preset appears; `TYPE_OPTIONS`/`RULE_PARAMS` keys must equal `VALID_TYPES`/`VALID_RULES`; the example schema generates data that passes its own rules
- [x] `--json` on `validate`, `preview`, `infer`, `generate` (`jsonmode.py`: `emit`, `fail`); no Rich output in JSON mode; exit codes unchanged → CliRunner tests parse stdout with `json.loads` (pass/fail, dry run, with/without `--validate`)
- [x] Errors in JSON mode: `{"error": ...}` + exit 1, also for missing files and schema errors (`_run` wrapper in `main.py`) → parametrized test on 5 commands
- [x] `--json` with `--out -` refused on `generate` and `infer` → tests
- [x] README: section "Using fauxdata with AI agents" + `--json` row in the `generate` options
- [x] Main `--help` mentions `fauxdata agent` → test
- [x] Full suite: 142 passed, coverage 87.34%

- [x] FIXED (pre-existing): steps on columns missing from the dataset were reported `ok: true` with 0/0 rows. Now read from `validation_info` (`active`, `eval_error`): new field `evaluated`, `ok: false`, table shows `NOT RUN`. `get_dataframe_report()` (suggested in fauxdata issue #1) can't be used: it raises on `rows_distinct`/`rows_complete` with `columns_subset` (0.24.0-1.0.1, upstream `main` 4510729); reported as https://github.com/posit-dev/pointblank/issues/442.
- [x] Website `docs/index.html`: badge pointblank 1.0+, "six commands", rows for `infer` and `agent`, `--json` on generate/validate.

Decided 2026-10-11: command name `agent`; `--json` on `generate` too; JSON shape above OK.

## Review (2026-10-11)

- Shipped in 0.2.0 (not committed yet): pointblank `>=1.0.1`; native float `precision` with bounds snapped inward; `col_vals_str_len`; fixes for `--categorical-threshold` from the CLI, nulls in value rules, numeric `values` ignored by the generator, `rows_distinct` on null keys; `fauxdata agent` and `--json` on generate/validate/infer/preview.
- 143 tests, coverage 87.05% (from 103 and 83.2%). Bundled schemas: same seed, byte-identical output to 0.1.6.
- Also fixed: steps on missing columns (`evaluated` field, `NOT RUN`). Website updated. Closes fauxdata issue #1 (`--json`).
- Found, not fixed: `unique` ignored on coherent presets (posit-dev/pointblank#441); `get_dataframe_report()` fails with `columns_subset` (posit-dev/pointblank#442); `unique` + `nullable` on a narrow int range not generable.
- Behavior changes for the release notes: value rules ignore nulls; `rows_distinct` totals count non-null rows only; `--categorical-threshold N` is a count (`1` = one value); `precision` bounds snap inward; 20 extra transitive packages via `anthropic[bedrock]`.
- Release only on request (`RELEASING.md`).

## Phase 5 - pointblank 1.1.0 (2026-10-17)

Both upstream issues closed on 2026-10-12, fixes released in pointblank 1.1.0 (2026-10-15).

- [x] `pyproject.toml`: `pointblank>=1.1.0`; `uv lock --upgrade-package pointblank` → 1.1.1; `anthropic[bedrock]` and its 20 transitive packages gone from `uv.lock`
- [x] #441: test `test_generate_unique_coherent_presets` → passes on 1.1.1, fails on 1.0.1 (1959/2000); "Known limit" removed from `fauxdata agent`
- [x] #442: `get_dataframe_report()` works again, but the validator stays on `validation_info` (it needs `active`/`eval_error` for `evaluated`); outdated comment fixed
- [x] Website badge `pointblank 1.1+`; LOG entry
- [x] Full suite: 144 passed, coverage 87.05%
- [ ] Commit (on user's ok)

Still open: item 6 above (`unique` + `nullable` on a narrow int range), not related to these issues.
