import argparse
import csv
import random

import geonamescache

from .utils import log_info


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate cities with random coordinates"
    )
    parser.add_argument("--output_fp", type=str, help="Path to the output TSV file")
    parser.add_argument(
        "--n_cities", type=int, default=10, help="Number of cities to generate"
    )
    parser.add_argument(
        "--min_coord", type=float, default=0, help="Minimum coordinate value"
    )
    parser.add_argument(
        "--max_coord", type=float, default=100, help="Maximum coordinate value"
    )
    return parser.parse_args()


def generate_cities(n_cities, min_coord, max_coord):
    """Generate cities with random coordinates

    Args:
        n_cities: Number of cities to generate
        min_coord: Minimum coordinate value
        max_coord: Maximum coordinate value

    Returns:
        List of cities with random coordinates
    """
    cities = []
    gc = geonamescache.GeonamesCache()
    city_names = [x["name"] for x in gc.get_cities().values()]
    city_names = random.sample(city_names, n_cities)
    for city_name in city_names:
        city = {
            "name": city_name,
            "x": random.uniform(min_coord, max_coord),
            "y": random.uniform(min_coord, max_coord),
        }
        cities.append(city)
    return cities


def save_cities(cities, file_path):
    """Save cities to a TSV file

    Args:
        cities: List of cities
        file_path: Path to the TSV file
    """
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "x", "y"], delimiter="\t")
        writer.writeheader()
        writer.writerows(cities)


def main():
    args = parse_args()
    log_info("Generating %d cities...", args.n_cities)
    cities = generate_cities(args.n_cities, args.min_coord, args.max_coord)
    log_info("Saving cities to %s", args.output_fp)
    save_cities(cities, args.output_fp)


if __name__ == "__main__":
    main()
