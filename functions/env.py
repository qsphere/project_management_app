from __future__ import annotations

import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent


def env(name: str) -> str:
    return (os.getenv(name) or "").strip()
