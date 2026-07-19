from __future__ import annotations

import os
import tomllib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = SCRIPT_DIR / ".streamlit" / "secrets.toml"


def load_secrets(path: Path | None = None) -> Path | None:
    """Load root-level keys from ``secrets.toml`` into ``os.environ``.

    Does not overwrite existing environment variables. Nested TOML tables are
    skipped (Streamlit exposes those via ``st.secrets`` only). Used by the UI
    and CLI so both share one secrets file without importing Streamlit here.
    """
    secrets_file = path or SECRETS_PATH
    if not secrets_file.is_file():
        return None
    with secrets_file.open("rb") as fh:
        data = tomllib.load(fh)
    for key, value in data.items():
        if isinstance(value, dict) or key in os.environ:
            continue
        os.environ[key] = value.strip() if isinstance(value, str) else str(value)
    return secrets_file


def env(name: str) -> str:
    return (os.getenv(name) or "").strip()
