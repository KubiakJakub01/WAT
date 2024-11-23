import logging

import coloredlogs
import numpy as np

# Set up logging
_LOGGER = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler()
_HANDLER.setLevel(logging.INFO)
_LOGGER.addHandler(_HANDLER)
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


def euclidean_distance(cord_1, cord_2):
    """Calculating the distance between two cities

    Args:
        cord_1: City one coordinates
        cord_2: City two coordinates

    Returns:
        Calculated Euclidean distance between two cities
    """
    return np.sqrt(np.sum((np.array(cord_1) - np.array(cord_2)) ** 2))
