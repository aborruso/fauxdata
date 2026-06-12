# Impatto pointblank v0.25.0 su fauxdata

## Verdetto
Sì, impatto **forte**. La release introduce `schema_from_tbl()` / `Schema.from_table()`:
inferisce vincoli ricchi (min/max, unique, null rate, `allowed=`, preset come email/uuid)
da una tabella reale, pensati esplicitamente per la generazione sintetica.
È esattamente la premessa del progetto ("real fake datasets"): dato reale → schema → dato finto.

## BLOCCO — non installabile da PyPI
- v0.25.0 è **solo taggata su GitHub**, PyPI è fermo a 0.24.0.
- Non si può fare `pointblank>=0.25` + pubblicare fauxdata finché non esce su PyPI.
- API verificata sul tag git (non dal summary): firma confermata
  `schema_from_tbl(tbl, *, infer_constraints=True, categorical_threshold=20, detect_presets=True, sample_size=None)`.

## Fase A — nuovo comando `fauxdata infer` (la feature)
Flusso: tabella reale (CSV/Parquet via polars) → `schema_from_tbl` → YAML fauxdata → `generate`.
- Nuovo `commands/infer.py`: legge file, chiama `schema_from_tbl`, serializza in YAML fauxdata.
- Convertitore Field→ColumnSchema: mapping `dtype` (Int64/String/Float64/...) → `col_type`,
  `allowed`→`values`, `preset`, `min_val/max_val`→`min/max`, `unique`, `null_probability`.
- Flag da esporre: `--categorical-threshold`, `--no-detect-presets`, `--sample-size`, `--out schema.yml`.
- Mapping **lossy** da segnalare: `StringField.min_length/max_length` non hanno campo nel YAML fauxdata.
- Test di accettazione (vero criterio): infer da tabella campione → YAML → `generate` →
  output rispetta gli stessi vincoli (range, set, preset). NON basta "ritorna uno Schema".

## Fase B — verifiche di regressione (cambi di comportamento)
- `rows_distinct()`: in 0.25 le righe con null **non** sono più escluse. fauxdata lo usa nei
  `VALID_RULES` del validator → può cambiare pass/fail su schemi esistenti. Da testare.
- Lazy frame non più collezionati prematuramente: verificare che generator/validator non assuma DataFrame eager.

## Fuori scope (non rilevante per fauxdata)
- `Contract`/`Pipeline`, attachments multi-modali in `prompt()`, fix MCP server.

## Decisioni (prese 2026-06-12)
- **Timing**: solo piano. NON scrivere codice finché pointblank 0.25.0 non è su PyPI (ora è solo tag git, PyPI=0.24.0).
- **Validation**: `infer` genera sia `columns:` sia `validation:` (regole derivate dai vincoli — es. `col_vals_between` da min/max, `col_vals_in_set` da allowed, `col_vals_not_null`, `rows_distinct` per colonne unique).
- **Lunghezza stringhe**: aggiungere `min_length`/`max_length` a `ColumnSchema` per round-trip fedele
  → tocca `schema.py` (parse + dataclass), `generator.py` (`pb.string_field(min_length=, max_length=)`), test.

## Trigger di ripresa
Quando `pip index versions pointblank` (o PyPI) mostra 0.25.0:
1. Bump `pyproject.toml`: `pointblank>=0.25`, `uv sync`.
2. Fase B prima (regressioni rows_distinct / lazy frame) — sono rischi su codice esistente.
3. Poi Fase A (comando `infer` + estensione min_length/max_length).

## Review (completato 2026-06-12)
- **Fatto**: bump 0.25, comando `infer`, campi `min_length`/`max_length`, validation derivate, fix datetime CSV, errore chiaro unique+range. 102/102 test, coverage 83.2%.
- **Fase B esito**: nessuna modifica necessaria. Schemi inclusi tutti PASS; `rows_distinct`/lazy frame non impattano (fauxdata usa DataFrame eager).
- **Limiti noti documentati (README)**:
  1. Bassa cardinalità → valori reali congelati in `values:` (leak su colonne sensibili). Mitigazione: `--categorical-threshold` / editing manuale.
  2. `unique` + range int stretto non amplifica oltre la sorgente. Errore chiaro a runtime.
- **Non fatto (decisione utente)**: bump versione pacchetto (0.1.4 → 0.1.5) e publish PyPI — non richiesto, lasciato all'utente.
- **Possibili migliorie future** (docs/future-ideas.md candidate): opzione `infer` per non-categorizzare colonne testuali libere; flag per amplificazione (rilassa unique).
