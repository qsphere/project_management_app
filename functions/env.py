from __future__ import annotations

import os
import tomllib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = SCRIPT_DIR / ".streamlit" / "secrets.toml"


def _flatten_secret_leaves(data: dict) -> dict[str, str]:
    """Collect leaf keys from nested TOML tables into a flat map."""
    out: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out.update(_flatten_secret_leaves(value))
        else:
            out[key] = value.strip() if isinstance(value, str) else str(value)
    return out


def load_secrets(path: Path | None = None) -> Path | None:
    """Load secret leaf keys from ``secrets.toml`` into ``os.environ``.

    Supports root-level keys and nested TOML tables (e.g. ``[database]``): leaf
    names like ``DATABASE_URL`` are flattened into the environment. Does not
    overwrite existing environment variables. Used by the UI and CLI so both
    share one secrets file without importing Streamlit here.
    """
    secrets_file = path or SECRETS_PATH
    if not secrets_file.is_file():
        return None
    with secrets_file.open("rb") as fh:
        data = tomllib.load(fh)
    for key, value in _flatten_secret_leaves(data).items():
        if key in os.environ:
            continue
        os.environ[key] = value
    return secrets_file


def env(name: str) -> str:
    return (os.getenv(name) or "").strip()
