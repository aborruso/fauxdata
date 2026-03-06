"""Schema parsing and validation for fauxdata YAML schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


VALID_TYPES = {"int", "float", "string", "bool", "date", "datetime"}

STRING_PRESETS = {
    # Personal
    "name", "name_full", "first_name", "last_name",
    "email", "phone_number",
    "address", "city", "state", "country", "country_code_2", "country_code_3", "postcode",
    "latitude", "longitude",
    # Business
    "company", "job", "catch_phrase",
    # Internet
    "url", "domain_name", "ipv4", "ipv6", "user_name", "password",
    # Text
    "text", "sentence", "paragraph", "word",
    # Financial
    "credit_card_number", "iban", "currency_code",
    # Identifiers
    "uuid4", "md5", "sha1",
    # Misc
    "license_plate", "ssn",
}

VALID_RULES = {
    "col_vals_not_null",
    "col_vals_between",
    "col_vals_regex",
    "col_vals_in_set",
    "col_vals_gt",
    "col_vals_lt",
    "col_vals_ge",
    "col_vals_le",
    "rows_distinct",
    "col_exists",
}


@dataclass
class ColumnSchema:
    name: str
    col_type: str
    unique: bool = False
    nullable: bool = False
    min: Any = None
    max: Any = None
    preset: str | None = None
    locale: str | None = None
    precision: int | None = None
    values: list | None = None  # for in_set
    pattern: str | None = None  # regex pattern for string generation
    null_probability: float | None = None  # e.g. 0.1 = 10% nulls


@dataclass
class ValidationRule:
    rule: str
    columns: list[str] | None = None
    column: str | None = None
    min: Any = None
    max: Any = None
    pattern: str | None = None
    values: list | None = None


@dataclass
class SchemaConfig:
    name: str
    rows: int
    columns: list[ColumnSchema]
    description: str = ""
    seed: int | None = None
    locale: str = "US"
    output_format: str = "csv"
    output_path: str | None = None
    validation_rules: list[ValidationRule] = field(default_factory=list)


def load_schema(path: str | Path) -> SchemaConfig:
    """Load and parse a YAML schema file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return _parse_schema(data)


def _parse_schema(data: dict) -> SchemaConfig:
    if "name" not in data:
        raise ValueError("Schema must have a 'name' field")
    if "columns" not in data:
        raise ValueError("Schema must have a 'columns' field")

    rows = data.get("rows", 100)
    seed = data.get("seed", None)
    description = data.get("description", "")

    output = data.get("output", {})
    output_format = output.get("format", "csv")
    output_path = output.get("path", None)

    columns = []
    for col_name, col_data in data["columns"].items():
        col = _parse_column(col_name, col_data)
        columns.append(col)

    validation_rules = []
    for rule_data in data.get("validation", []):
        validation_rules.append(_parse_rule(rule_data))

    return SchemaConfig(
        name=data["name"],
        rows=rows,
        seed=seed,
        description=description,
        locale=data.get("locale", "US"),
        output_format=output_format,
        output_path=output_path,
        columns=columns,
        validation_rules=validation_rules,
    )


def _parse_column(name: str, data: dict) -> ColumnSchema:
    if "type" not in data:
        raise ValueError(f"Column '{name}' must have a 'type' field")
    col_type = data["type"]
    if col_type not in VALID_TYPES:
        raise ValueError(f"Column '{name}': invalid type '{col_type}'. Valid: {VALID_TYPES}")

    preset = data.get("preset", None)
    if preset and preset not in STRING_PRESETS:
        raise ValueError(f"Column '{name}': unknown preset '{preset}'. Valid: {STRING_PRESETS}")

    null_probability = data.get("null_probability", None)
    if null_probability is not None and not (0.0 <= float(null_probability) <= 1.0):
        raise ValueError(f"Column '{name}': null_probability must be between 0.0 and 1.0")

    return ColumnSchema(
        name=name,
        col_type=col_type,
        unique=data.get("unique", False),
        nullable=data.get("nullable", False),
        min=data.get("min", None),
        max=data.get("max", None),
        preset=preset,
        locale=data.get("locale", None),
        precision=data.get("precision", None),
        values=data.get("values", None),
        pattern=data.get("pattern", None),
        null_probability=float(null_probability) if null_probability is not None else None,
    )


def _parse_rule(data: dict) -> ValidationRule:
    if "rule" not in data:
        raise ValueError("Validation rule must have a 'rule' field")
    rule = data["rule"]
    if rule not in VALID_RULES:
        raise ValueError(f"Unknown validation rule '{rule}'. Valid: {VALID_RULES}")

    return ValidationRule(
        rule=rule,
        columns=data.get("columns", None),
        column=data.get("column", None),
        min=data.get("min", None),
        max=data.get("max", None),
        pattern=data.get("pattern", None),
        values=data.get("values", None),
    )
