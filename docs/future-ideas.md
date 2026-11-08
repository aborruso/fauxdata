# Future ideas

Ideas from the pointblank 0.26-1.1.1 releases, not yet planned (first list 2026-10-11, updated 2026-10-17).

- Related tables: generate linked datasets (e.g. people and orders) and check foreign keys with `col_vals_in_table()` (pointblank 0.27); since 1.1.0 `ref_table` can be a file path or a connection string, so a schema could point to a reference file such as an official code list.
- Coded missing values: a schema field for sentinel values like `-99` or `N/A`, generated and validated via `MissingSpec` and `col_pct_missing()` (pointblank 0.26).
- Schema export: let `infer` also write JSON Schema, Frictionless, dbt or ODCS via `export_contract()` (pointblank 0.26/0.27).
- Fidelity report: compare the real dataset with the synthetic one using `DataScan.compare()` (PSI, Kolmogorov-Smirnov) to show how close the shapes are (pointblank 0.27).
- Quality score in `validate`: report pointblank's data quality dimensions (completeness, validity, uniqueness, ...) and the overall health score from `get_dimension_scores()` / `get_health_score()`, in the table and in `--json` (pointblank 0.26).
- Schema import: build a fauxdata schema from an existing Frictionless Table Schema, CSVW or JSON Schema via `import_contract()` / `import_metadata()`, the inverse of the schema export idea above (pointblank 0.26/0.27).
- Reproducibility check: `pb.compare()` (or the `pb compare` CLI) between two generated files, to verify that the same schema and seed give the same data across fauxdata or pointblank upgrades. Today this check is done by hand. Not suited to real vs synthetic data: it compares rows, and synthetic rows differ by design (pointblank 1.1.0).

## Ideas from SDV

Reviewed 2026-11-08 against SDV 2.2.0. SDV is BUSL-1.1 (not open source) and a CPU-only install takes 1.2 GB, so it should not become a core dependency. Test: 3000 correlated rows, `infer --no-detect-presets` + `generate`, compared with SDV GaussianCopula.

- Cross-column rules: a schema-level `constraints:` block, starting with inequality (`end_date > start_date`). Generated data had `end > start` in 53% of rows; the source had 100%. Generate first, then repair, and keep the rule in validation. SDV's equivalents are `Inequality`, `FixedCombinations` and `Range` in `sdv.cag`.
- Category frequencies: let `infer` record the weight of each entry in `values:`. A column with 50% `nord` came out with 34%.
- Pairwise fidelity: add correlation between column pairs to the fidelity report idea above. `DataScan.compare()` reports per-column differences only. SDV's quality report scored Column Pair Trends 0.39 for fauxdata and 0.71 for GaussianCopula. SDMetrics is MIT but depends on `copulas` (BUSL-1.1), so reimplementing the pair metric is cleaner than depending on it.
- Privacy check for `infer`: flag synthetic rows identical or too close to real ones, in the spirit of SDMetrics `NewRowSynthesis` and `DCROverfittingProtection`.
- Optional `fauxdata-cli[sdv]` extra to learn from real data with GaussianCopula. Lowest priority: heavy, licence to review, and it breaks the schema-first model because the output depends on a fitted model rather than on the YAML.
