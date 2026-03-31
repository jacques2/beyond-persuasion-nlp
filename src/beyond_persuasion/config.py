"""Configuration utilities.

This file is a good place for:
- loading YAML configuration files,
- validating required keys,
- exposing typed configuration objects later.
"""

from pathlib import Path


def get_default_config_path() -> Path:
    """Return the default project config path."""
    return Path("configs/base.yaml")
