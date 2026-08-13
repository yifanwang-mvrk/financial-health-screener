from __future__ import annotations

import atexit
import shutil
import sys
import tempfile
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
_TEMP_PROJECT: tempfile.TemporaryDirectory[str] | None = None


def project_root() -> Path:
    """Return a disposable project copy for rebuild-based integration tests."""
    global _TEMP_PROJECT
    if _TEMP_PROJECT is not None:
        return Path(_TEMP_PROJECT.name) / SOURCE_ROOT.name

    _TEMP_PROJECT = tempfile.TemporaryDirectory(
        prefix="financial-health-screener-tests-",
        ignore_cleanup_errors=True,
    )
    destination = Path(_TEMP_PROJECT.name) / SOURCE_ROOT.name
    shutil.copytree(
        SOURCE_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".DS_Store"),
    )
    atexit.register(_TEMP_PROJECT.cleanup)
    return destination
