"""Configuration utilities.

This file is a good place for:
- loading YAML configuration files,
- validating required keys,
- exposing typed configuration objects later.
"""

from pathlib import Path
from typing import Any, Dict, Optional


def get_default_config_path() -> Path:
    """Return the default project config path."""
    return Path("configs/base.yaml")


def load_yaml_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the project YAML configuration file."""
    try:
        import yaml
    except Exception as exc:
        raise RuntimeError(
            "PyYAML is required to load configuration files. "
            "Install project dependencies before using from_config_file()."
        ) from exc

    config_path = path or get_default_config_path()

    with config_path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    if not isinstance(data, dict):
        raise ValueError("The configuration file must contain a dictionary at the top level.")

    return data
