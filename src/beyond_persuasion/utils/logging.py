"""Logging helpers.

Later this can be extended to save:
- emotion predictions,
- ethical decisions,
- prompt variants,
- evaluation metadata.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a project logger with a simple default configuration."""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
