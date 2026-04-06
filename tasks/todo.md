# Agent-friendly CLI improvements

## Obiettivo
Applicare i principi per CLI usabili dagli agenti AI.

## Fase 1 — Non-interactive `init`

- [ ] Aggiungere `--description`, `--rows`, `--format`, `--yes` come flag a `init_cmd` in `main.py`
- [ ] Aggiornare `run()` in `commands/init.py` per accettare questi parametri
- [ ] Rendere i prompt questionary fallback (solo quando il flag è None)
- [ ] `--yes` salta la conferma di sovrascrittura

## Fase 2 — Esempi in `--help`

- [ ] Aggiungere `epilog` con esempi a ogni comando in `main.py` (init, generate, validate, preview)

## Fase 3 — `--dry-run` per `generate`

- [ ] Aggiungere flag `--dry-run` a `generate_cmd` in `main.py`
- [ ] Implementare dry-run in `commands/generate.py`: mostra cosa farebbe senza scrivere file

## Fase 4 — Output strutturato su successo

- [ ] `generate`: output su successo mostra chiave=valore (output_path, format, rows)
- [ ] `init`: output su successo mostra schema_path

## Domande aperte

- Aggiungere anche `--quiet` / `--json` per output machine-readable?
- `validate` e `preview` hanno già flag, sufficienti?

## Review

- Tutte e 4 le fasi completate; 79/79 test passano, coverage 82%
- `init` ora fully non-interactive con `--name --description --rows --format --yes`
- `generate` ha `--dry-run` e output strutturato chiave: valore
- Ogni comando ha esempi nel `--help` via `epilog`
- Venv ricreato con `--clear` (cartella rinominata da `real_fake_datasets`)
