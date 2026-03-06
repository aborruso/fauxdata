# Log

## 2026-03-06 — v0.1.2

- Bump to 0.1.2 and publish to PyPI

## 2026-03-06 (feature)

- `--version` / `-V` flag nel CLI (`fauxdata --version` → `fauxdata 0.1.1`)
- Coverage threshold 80% in pytest config (`--cov-fail-under=80`); attuale: 83.76%
- Nuovo campo `pattern` in ColumnSchema: genera stringhe che matchano un regex via pointblank
- Nuovo campo `null_probability` in ColumnSchema: controllo granulare dei null (0.0–1.0), con validazione in parsing
- Rimossa dipendenza `faker` (non usata, pointblank gestisce tutto)
- Fix generator: `null_probability=None` non passato a pointblank (causa TypeError)
- Test aggiornati: 79/79 pass

## 2026-03-06 (tests)

- Add pytest test suite: 65 tests, 100% pass, 0.44s
- `tests/test_schema.py`: unit tests for YAML schema parsing (valid/invalid cases)
- `tests/test_output.py`: unit tests for export functions (all formats, stdout, errors)
- `tests/test_generator.py`: integration tests for generation (types, seed, unique, presets)
- `tests/test_validator.py`: integration tests for validation rules (pass/fail scenarios)
- `tests/test_cli.py`: CLI smoke tests via `typer.testing.CliRunner`
- Add `[dependency-groups] dev` in `pyproject.toml` (pytest, pytest-cov); config via `[tool.pytest.ini_options]`

## 2026-03-06

- Initial implementation of `fauxdata` CLI
- Stack: pointblank 0.22 (native generation + validation), polars, typer, rich, pyfiglet, questionary
- Commands: `init`, `generate`, `validate`, `preview`
- Example schemas: `people.yml`, `orders.yml`, `events.yml`
- All schemas generate and validate cleanly (all rules PASS)
- `locale` field at schema level maps to pointblank `country=` param
