# fauxdata

**fauxdata** is a command-line tool for generating and validating realistic fake datasets from simple YAML schemas.

If you work with data — as an analyst, engineer, developer, or researcher — you constantly need test data: to prototype a pipeline, populate a demo dashboard, write unit tests, or show a colleague how a system should behave. Real data is often unavailable, sensitive, or too messy to share. fauxdata solves this by letting you describe your dataset structure once and generate as many rows as you need, on demand, with realistic values.

---

## Why fauxdata?

- **Schema-first**: define the shape of your data in a readable YAML file — column names, types, constraints, realistic presets
- **Locale-aware and coherent**: set `locale: IT` and get Italian names, cities, email domains, phone formats, IBANs — all consistent within each row. Set `locale: JP` and get Japanese names and addresses. The data is not just random strings: related fields are generated together so they make sense as a whole record
- **Validated by design**: the same schema that defines generation also drives validation; no surprises
- **Pipeline-friendly**: output to stdout with `--out -` for seamless piping and redirection
- **Multiple formats**: CSV, Parquet, JSON, JSONL / JSON Lines out of the box

---

## Install

### With uv (recommended)

[uv](https://docs.astral.sh/uv/) installs fauxdata as an isolated tool available globally, without polluting any existing Python environment:

```bash
git clone https://github.com/aborruso/fauxdata
cd fauxdata
uv tool install .
```

After installation, `fauxdata` is available from any directory.

To update after code changes:

```bash
uv tool install . --reinstall
```

### With pip

```bash
git clone https://github.com/aborruso/fauxdata
cd fauxdata
pip install .
```

---

## Quick start

```bash
# Generate 500 rows from a schema, with validation
fauxdata generate schemas/people.yml --rows 500 --validate

# Stream to stdout and pipe to other tools
fauxdata generate schemas/people.yml --rows 1000 --out - | head -5

# Validate an existing file against a schema
fauxdata validate my_data.csv schemas/people.yml

# Preview a dataset with column statistics
fauxdata preview my_data.csv --rows 10

# Create a new schema interactively
fauxdata init --name orders
```

---

## Schema format

A schema is a YAML file that describes the structure of your dataset. Here is a realistic example for a people dataset:

```yaml
name: people
description: "People dataset with personal info"
rows: 1000
seed: 42
locale: IT           # ISO country code — affects names, cities, emails, phone numbers, etc.

output:
  format: csv        # csv | parquet | json | jsonl | jsonlines
  path: tmp/people.csv

columns:
  id:
    type: int
    unique: true
    min: 1
    max: 99999

  name:
    type: string
    preset: name     # generates realistic full names for the given locale

  email:
    type: string
    preset: email

  age:
    type: int
    min: 18
    max: 90

  city:
    type: string
    preset: city

  country_code:
    type: string
    preset: country_code_2   # ISO 3166-1 alpha-2, e.g. "IT"

  active:
    type: bool

  signup_date:
    type: date
    min: "2020-01-01"
    max: "2024-12-31"

  score:
    type: float
    min: 0.0
    max: 100.0

  status:
    type: string
    values: [active, inactive, pending]   # enum: pick from a fixed list

validation:
  - rule: col_vals_not_null
    columns: [id, name, email]
  - rule: col_vals_between
    column: age
    min: 18
    max: 90
  - rule: col_vals_regex
    column: email
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
  - rule: rows_distinct
    columns: [id]
```

### Column types

| Type | Description | Options |
|------|-------------|---------|
| `int` | Integer | `min`, `max`, `unique` |
| `float` | Floating point | `min`, `max` |
| `string` | Text | `preset`, `values`, `unique` |
| `bool` | Boolean | — |
| `date` | Date | `min`, `max` (ISO format) |
| `datetime` | Datetime | `min`, `max` (ISO format) |

### String presets

Presets generate realistic, locale-aware values. Set `locale` at the schema level to control the country.

| Category | Presets |
|----------|---------|
| Personal | `name`, `name_full`, `first_name`, `last_name`, `email`, `phone_number` |
| Location | `address`, `city`, `state`, `country`, `country_code_2`, `country_code_3`, `postcode`, `latitude`, `longitude` |
| Business | `company`, `job`, `catch_phrase` |
| Internet | `url`, `domain_name`, `ipv4`, `ipv6`, `user_name`, `password` |
| Text | `text`, `sentence`, `paragraph`, `word` |
| Financial | `iban`, `currency_code`, `credit_card_number` |
| Identifiers | `uuid4`, `md5`, `sha1`, `ssn`, `license_plate` |

### Locale-aware generation

Setting `locale` in the schema is more than a language switch — it makes the entire dataset culturally coherent.

With `locale: IT`:

```
id     name                 email                        city       country_code
83811  Giovanni Gentile     giovanni.gentile@tin.it      Bari       IT
14593  Bruno Mancini        bruno.mancini16@virgilio.it  Taranto    IT
3279   Giada Santini        gsantini38@fastwebnet.it     Milano     IT
```

With `locale: DE`:

```
id     name                 email                        city       country_code
12044  Hans Müller          h.mueller@web.de             Berlin     DE
57892  Lena Schmidt         lena.schmidt@gmx.de          München    DE
```

With `locale: JP`:

```
id     name                 email                        city       country_code
9341   Yuki Tanaka          y.tanaka@docomo.ne.jp        Tokyo      JP
```

The magic is that **related presets are generated together**: the email is derived from the name, the city belongs to the country, the phone number uses the right country prefix, and IBANs use the correct country code. A single `locale` field in your schema is all it takes.

Supported locales include: `US`, `IT`, `DE`, `FR`, `ES`, `JP`, `BR`, `PL`, `NL`, `SE`, `DK`, `TR`, `RU`, `CN`, `KR`, and [many more](https://github.com/posit-dev/pointblank).

### Validation rules

| Rule | Description | Parameters |
|------|-------------|------------|
| `col_vals_not_null` | No nulls | `columns` |
| `col_vals_between` | Value in range | `column`, `min`, `max` |
| `col_vals_regex` | Matches pattern | `column`, `pattern` |
| `col_vals_in_set` | Value in allowed set | `column`, `values` |
| `col_vals_gt` / `col_vals_lt` | Greater / less than | `column`, `min` / `max` |
| `col_vals_ge` / `col_vals_le` | Greater / less or equal | `column`, `min` / `max` |
| `rows_distinct` | Unique rows | `columns` |
| `col_exists` | Column present | `columns` |

---

## Commands

### `fauxdata generate SCHEMA`

```
fauxdata generate schemas/people.yml
fauxdata generate schemas/people.yml --rows 500 --seed 42 --validate
fauxdata generate schemas/people.yml --format parquet --out tmp/people.parquet
fauxdata generate schemas/people.yml --rows 1000 --out -         # stdout
fauxdata generate schemas/people.yml --out - --format jsonl | wc -l
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--rows` | `-r` | from schema | Number of rows to generate |
| `--out` | `-o` | from schema | Output path — use `-` for stdout |
| `--format` | `-f` | from schema | Output format: `csv`, `parquet`, `json`, `jsonl`, `jsonlines` |
| `--seed` | `-s` | from schema | Random seed for reproducibility |
| `--validate` | `-v` | off | Run validation rules after generating |

When `--out -` is used, all output messages are suppressed and only data is written to stdout.

### `fauxdata validate DATASET SCHEMA`

```
fauxdata validate tmp/people.csv schemas/people.yml
```

Validates an existing file against a schema. Exits with code `1` if any rule fails — useful in CI pipelines.

### `fauxdata preview DATASET`

```
fauxdata preview tmp/people.csv --rows 10
```

Shows the first N rows and a column statistics table (type, nulls, unique count, min/max).

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--rows` | `-r` | 10 | Number of rows to display |

### `fauxdata init`

```
fauxdata init
fauxdata init --name orders
```

Interactive wizard to create a new schema template. Asks for name, description, row count, and default format.

| Option | Short | Description |
|--------|-------|-------------|
| `--name` | `-n` | Schema name (skips the interactive prompt) |

---

## Example schemas

Three ready-to-use schemas are included in `schemas/`:

| Schema | Domain | Columns |
|--------|--------|---------|
| `people.yml` | Personal data | id, name, email, age, city, country_code, active, signup_date, score |
| `orders.yml` | E-commerce | order_id, customer_id, product, amount, status, created_at |
| `events.yml` | Analytics | event_id, user_id, event_type, timestamp, ip, user_agent, session_duration |

---

## Acknowledgements

A heartfelt thank you to **[Rich Iannone](https://github.com/rich-iannone)** and the entire [pointblank](https://github.com/posit-dev/pointblank) team at [Posit](https://posit.co/) for building an exceptional data quality library — and for inspiring this project with their article:

> **[Building realistic fake datasets with pointblank](https://posit.co/blog/building-realistic-fake-datasets-with-pointblank/)**

Without their work, fauxdata would not exist. If you find pointblank useful, please give it a ⭐ on GitHub.
