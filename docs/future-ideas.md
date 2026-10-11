# Future ideas

Ideas from the pointblank 0.26-1.0.1 releases, not yet planned (2026-10-11).

- Related tables: generate linked datasets (e.g. people and orders) and check foreign keys with `col_vals_in_table()` (pointblank 0.27).
- Coded missing values: a schema field for sentinel values like `-99` or `N/A`, generated and validated via `MissingSpec` and `col_pct_missing()` (pointblank 0.26).
- Schema export: let `infer` also write JSON Schema, Frictionless, dbt or ODCS via `export_contract()` (pointblank 0.26/0.27).
- Fidelity report: compare the real dataset with the synthetic one using `DataScan.compare()` (PSI, Kolmogorov-Smirnov) to show how close the shapes are (pointblank 0.27).
