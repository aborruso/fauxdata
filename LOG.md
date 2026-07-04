# Log

## 2026-07-04 — v0.1.6

- Release `0.1.6`: include il fix issue #2 (`precision` float). Build con `uv build`, tag `v0.1.6`.
- Deploy PyPI **manuale** (`uv publish`): nessun workflow di release automatico.

## 2026-07-04 — fix issue #2: `precision` float ignorato

- Bug: l'opzione `precision` dei float veniva letta nello schema ma mai applicata (`pb.float_field` non ha il parametro). Valori generati con precisione piena.
- Fix in `generator.py`: dopo `pb.generate_dataset`, arrotondo con `pl.col(...).round(precision)` le colonne `float` con `precision` impostato.
- Verifica: reproducer della issue → output atteso (`27.74, 169.64, …`). Test `test_generate_float_precision`. 103/103 pass.

## 2026-06-12 — pointblank 0.25 + comando `infer`

- Bump `pointblank>=0.25` (uscito su PyPI). Schemi inclusi (people/orders/events) verificati: tutti PASS.
- Fase B regressioni: `rows_distinct` ora include righe con null (correttezza migliorata), lazy frame ok. fauxdata passa sempre DataFrame eager → nessun impatto.
- Nuovo comando **`fauxdata infer DATASET`**: da tabella reale (csv/parquet/json/jsonl) genera schema YAML (`columns:` + `validation:`) via `pb.schema_from_tbl`. Flag: `--out/-o`, `--name/-n`, `--rows/-r`, `--format/-f`, `--categorical-threshold`, `--detect-presets/--no-detect-presets`, `--sample-size`.
- `ColumnSchema`: nuovi campi `min_length`/`max_length` per stringhe (round-trip fedele); passati a `pb.string_field`. Validazione parsing (negativi, min>max).
- infer CSV: `try_parse_dates=True` → date/datetime tipizzati invece che congelati come categorici.
- generate: errore chiaro su conflitto unique+range stretto ("too narrow a range") invece del traceback criptico di pointblank.
- Limite noto: colonne a bassa cardinalità congelate ai valori reali (possibile leak su colonne sensibili) — documentato nel README.
- Test: +14 (`tests/test_infer.py` + length in `test_new_fields.py`). 102/102 pass, coverage 83.2%.

- `init`: aggiunto `--description`, `--rows`, `--format`, `--yes`; questionary diventa fallback
- Tutti i comandi: `epilog` con esempi in `--help`
- `generate`: aggiunto `--dry-run` (mostra piano senza scrivere)
- `generate`: output su successo mostra `output_path`, `format`, `rows` come chiave: valore
- `init`: output su successo aggiunge `schema_path: <file>`
- Fix venv: ricreato con `uv venv --clear` (cartella rinominata da `real_fake_datasets`)

## 2026-03-06 — v0.1.3

- Add Python classifiers to pyproject.toml (3.11, 3.12, 3.13, MIT) — fixes pyversions badge
- Fix version tests to read `__version__` dynamically instead of hardcoded string

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
