# Log

## 2026-10-17 — 0.2.1: pointblank 1.1.0

- Versione `0.2.1` (patch): porta su PyPI il nuovo minimo `pointblank>=1.1.0` e `unique` rispettato sui preset coerenti (vedi voce sotto). Link agli schemi d'esempio nel README.
- sdist a whitelist (`only-include`: `src`, `tests`, `schemas`, README, LICENSE, `pyproject.toml`): i file non tracciati (`share.png`, `.claude/settings.local.json`) non finiscono più nel pacchetto, niente più build da clone pulito. Verificato: build dalla working copy pulita, 144/144 test dallo sdist estratto.

## 2026-10-17 — pointblank 1.1.0: chiuse le issue #441 e #442

- Bump `pointblank>=1.1.0` (da 1.0.1; installata 1.1.1). Le due issue segnalate l'11 ottobre sono state chiuse il 12 e le correzioni sono uscite in v1.1.0 (15 ottobre): #441 con la PR posit-dev/pointblank#447 (`unique` sui preset coerenti), #442 con la PR posit-dev/pointblank#444 (`get_dataframe_report()` con `columns_subset`).
- `unique` sui preset coerenti ora rispettato: test `test_generate_unique_coherent_presets` (2000 righe, `name` ed `email` tutti distinti); con pointblank 1.0.1 fallisce (1959 su 2000). Tolto il "Known limit" dalla guida di `fauxdata agent`.
- Validator: resta su `validation_info` (serve per `active`/`eval_error`, cioè `evaluated`/`NOT RUN`); aggiornato solo il commento, che citava il bug ormai corretto.
- Effetto collaterale positivo: pointblank 1.1.x non richiede più `anthropic[bedrock]`, 20 pacchetti transitivi in meno in `uv.lock`.
- Sito: badge `pointblank 1.1+`. 144/144 test, coverage 87.05%. Versione del pacchetto invariata (0.2.0), nessuna release.

## 2026-10-11 — 0.2.0: pointblank 1.0.1, `precision` nativa, `col_vals_str_len`, fix, comando `agent` e `--json`

- Rilasciata: tag `v0.2.0`, PyPI (`fauxdata-cli` 0.2.0), GitHub Release. Build da clone pulito: l'sdist della 0.1.6 conteneva anche `.claude/settings.local.json` e `share.png` non tracciati.
- `carousel/`: 6 cartoline LinkedIn per l'annuncio (Typst, stile del sito; font VT323 e IBM Plex Mono inclusi con licenza OFL). Build: `typst compile --font-path fonts slides.typ output/deck.pdf`.
- Bump `pointblank>=1.0.1` (da 0.25.0). 103/103 test invariati; schemi inclusi PASS; stesso seed → CSV identici byte per byte tra 0.25 e 1.0.1. Effetto collaterale: da 0.27 pointblank richiede `anthropic[bedrock]` → 20 pacchetti in più installati (anthropic, boto3, pydantic, …), non usati da fauxdata.
- `precision` float: ora nativa (`pb.float_field(precision=)`), unicità garantita dopo l'arrotondamento. Limiti stretti verso l'interno sulla griglia dei decimali (`max: 9.999`, `precision: 2` → `9.99`) perché l'arrotondamento non sfori il range; errore chiaro se nessun valore ci sta. Documentata nel README (prima non lo era).
- Nuova regola `col_vals_str_len` (`column`, `min`/`max`, null ignorati). `infer` la emette solo per stringhe libere: su preset/pattern/values il generatore ignora le lunghezze.
- Fix: le regole sui valori (`between`, `gt/lt/ge/le`, `regex`, `in_set`) ignorano i null (`na_pass=True`; `in_set` via `None` nel set). Prima una colonna col 20% di null falliva 195/1000 righe.
- Fix: `infer --categorical-threshold` da CLI arrivava come float (anche il default) e pointblank lo leggeva come frazione → ogni colonna stringa senza preset diventava categorica con i valori reali copiati in `values:`. Ora gli interi ≥ 1 passano come conteggio.
- Fix: `values` sulle colonne `int`/`float` ora rispettato in generazione (passato come `allowed`); prima `infer` lo emetteva per gli int a bassa cardinalità e il generatore lo ignorava (403/500 fallimenti in round-trip).
- Fix: `rows_distinct` esclude le righe con null nelle colonne controllate (come SQL UNIQUE); prima i null contavano come duplicati tra loro.
- Bug di pointblank (non nostro): `unique=True` ignorato sui preset coerenti (`email`, `name`, `city`, …); segnalato in https://github.com/posit-dev/pointblank/issues/441. Non corretto: `unique` + `nullable` su range stretto non generabile.
- Nuovo comando `fauxdata agent`: guida Markdown per agenti AI (flusso, output JSON, exit code, schema, tipi, preset, regole, esempio); liste generate dalle costanti di `schema.py`.
- Nuovo flag `--json` su `generate`, `validate`, `infer`, `preview`: stdout contiene solo un oggetto JSON; errori come `{"error": ...}` con exit 1. Sezione README "Using fauxdata with AI agents".
- Fix: un passo su una colonna assente dal dataset risultava `ok: true` con 0/0 righe; ora campo `evaluated` (da `validation_info`), `ok: false`, `NOT RUN` in tabella. `get_dataframe_report()` non usabile: fallisce con `rows_distinct`/`rows_complete` + `columns_subset` (segnalato in https://github.com/posit-dev/pointblank/issues/442). Chiude la issue #1 di fauxdata (output strutturato → `--json`).
- Sito `docs/index.html`: badge pointblank 1.0+, "six commands", righe `infer` e `agent`, `--json`.
- 143/143 test, coverage 87.05%.

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
