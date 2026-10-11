"""JSON output for agents: with --json, stdout carries exactly one JSON document."""

from __future__ import annotations

import json
import sys

import typer


def emit(obj) -> None:
    """Write obj to stdout as a single JSON line (dates and other values via str)."""
    sys.stdout.write(json.dumps(obj, default=str, ensure_ascii=False) + "\n")


def fail(message: str):
    """Report an error as {"error": ...} and exit with code 1."""
    emit({"error": message})
    raise typer.Exit(code=1)
