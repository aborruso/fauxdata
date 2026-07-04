# Releasing

Procedura per pubblicare una nuova release di `fauxdata` su PyPI.
Il deploy **non è automatico**: nessun workflow GitHub Actions. Ogni step è manuale.

## Versioning

`MAJOR.MINOR.PATCH` (SemVer).

- **subrelease / patch** (`0.1.5` → `0.1.6`): bugfix, nessuna modifica di API.
- **minor** (`0.1.x` → `0.2.0`): nuove feature retrocompatibili.
- **major** (`0.x` → `1.0.0`): breaking change.

## Step

1. **Aggiorna la versione** nei due file (devono restare allineati):
   - `pyproject.toml` → `version = "X.Y.Z"`
   - `src/fauxdata/__init__.py` → `__version__ = "X.Y.Z"`

2. **Aggiorna `LOG.md`**: nuova sezione in cima con data `YYYY-MM-DD` e le modifiche.

3. **Test**: devono passare tutti.

   ```bash
   uv run pytest tests/ -q
   uv run fauxdata --version   # deve stampare la nuova versione
   ```

4. **Build**:

   ```bash
   rm -rf dist/
   uv build
   ls dist/   # fauxdata_cli-X.Y.Z-py3-none-any.whl + .tar.gz
   ```

5. **Aggiorna la CLI installata localmente** (`fauxdata` è installato come `uv tool`):

   ```bash
   uv tool install --reinstall .   # reinstalla dalla working copy
   fauxdata --version              # deve stampare la nuova versione
   ```

6. **Commit + tag + push**:

   ```bash
   git add pyproject.toml src/fauxdata/__init__.py LOG.md
   git commit -m "chore: vX.Y.Z — <sintesi>"
   git tag -a vX.Y.Z -m "vX.Y.Z — <sintesi>"
   git push origin main
   git push origin vX.Y.Z
   ```

7. **Pubblica su PyPI** (richiede token PyPI — step da eseguire a mano):

   ```bash
   uv publish              # oppure: twine upload dist/*
   ```

   Il token si passa via `UV_PUBLISH_TOKEN` o `--token`. Non committare mai il token.

8. **Verifica / aggiorna da PyPI** (il pacchetto su PyPI è `fauxdata-cli`):

   ```bash
   uvx fauxdata@X.Y.Z --version          # verifica al volo la versione pubblicata

   pip install --upgrade fauxdata-cli     # aggiorna un'installazione pip esistente
   # oppure, se installato come uv tool:
   uv tool upgrade fauxdata-cli
   ```

9. **(Opzionale) GitHub Release**: dal tag già pushato.

   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes "<changelog dal LOG.md>"
   ```

## Note

- Se una release chiude una issue, referenziarla nel commit/tag (`#N`) e chiudere la issue con un commento che linka al commit.
- La versione è testata dinamicamente (`test_cli_version` legge `__version__`), quindi il bump non rompe i test.
