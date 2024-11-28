import logging

import coloredlogs
import matplotlib.pyplot as plt
import numpy as np

from .config import Config

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


def fig_to_numpy(fig):
    """Convert matplotlib figure to numpy array

    Args:
        fig: Matplotlib figure

    Returns:
        Numpy array of the figure
    """
    fig.canvas.draw()
    data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data


def plot_route(
    config: Config, cities_names: list[str], distance: float, generation: int
):
    """Plotting the route

    Args:
        config: Config object
        route: Route to plot
    """
    citi_coords = config.city_coords
    x_shortest = [citi_coords[city_name][0] for city_name in cities_names]
    y_shortest = [citi_coords[city_name][1] for city_name in cities_names]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(
        x_shortest + [x_shortest[0]],
        y_shortest + [y_shortest[0]],
        "--go",
        label="Best Route",
        linewidth=2.5,
    )
    plt.legend()

    for i, citi_name in enumerate(cities_names, 1):
        x, y = citi_coords[citi_name]
        ax.plot(x, y, "ro")
        ax.annotate(f"{i}-{citi_name}", (x, y), fontsize=20)

    plt.title(label=f"Total Distance Travelled: {distance:.2f}", fontsize=20)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(color="k", linestyle="dotted")
    data = fig_to_numpy(fig)
    plt.close()
    return data
