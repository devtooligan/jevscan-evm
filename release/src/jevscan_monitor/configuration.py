"""Explicit environment configuration; importing never reads a local .env file."""

import os
from pathlib import Path


def data_directory() -> Path:
    value = os.environ.get("JEVSCAN_DATA_DIR")
    return Path(value).expanduser().resolve() if value else Path.home() / ".local/share/jevscan-monitor"


def load_dotenv() -> None:
    """Compatibility hook: credentials come only from the process environment.

    The release intentionally does not discover or execute configuration files
    from the working directory, scanned input, or installed package directory.
    """
