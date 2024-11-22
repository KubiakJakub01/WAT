import logging

import coloredlogs

# Set up logging
_LOGGER = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_LOGGER.addHandler(_handler)
coloredlogs.install(
    level="INFO", logger=_LOGGER, fmt="%(asctime)s %(levelname)s %(message)s"
)


def log_debug(*args, **kwargs):
    """Log an debug message."""
    _LOGGER.debug(*args, **kwargs)


def log_info(*args, **kwargs):
    """Log an info message."""
    _LOGGER.info(*args, **kwargs)


def log_warning(*args, **kwargs):
    """Log a warning message."""
    _LOGGER.warning(*args, **kwargs)


def log_error(*args, **kwargs):
    """Log an error message."""
    _LOGGER.error(*args, **kwargs)
