#!/usr/bin/env python3
"""Fail if any non-empty module under ui/ does not use Streamlit."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "ui"
STREAMLIT_RE = re.compile(
    r"(^|\n)\s*(import streamlit\b|from streamlit\b)",
    re.MULTILINE,
)


def main() -> int:
    violations: list[Path] = []
    for path in sorted(APP.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            continue  # empty __init__.py package markers allowed
        if not STREAMLIT_RE.search(text):
            violations.append(path.relative_to(ROOT))

    if violations:
        print("ui/ must be Streamlit-only. These modules lack a Streamlit import:")
        for path in violations:
            print(f"  - {path}")
        print("Move non-UI code to constants/, functions/, services/, or clients/.")
        return 1

    print("OK: all non-empty modules under ui/ use Streamlit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
