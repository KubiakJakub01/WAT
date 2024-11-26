import argparse
from pathlib import Path
from time import time

from .config import Config
from .trainer import GeneticTrainer
from .utils import log_info
from .tsp_dp import tsp_dynamic_programming


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genetic Algorithm for the Travelling Salesman Problem"
    )
    parser.add_argument(
        "--cities_fp",
        type=Path,
        default=Path("configs/cities.tsv"),
        help="Path to the TSV file containing the cities",
    )
    parser.add_argument(
        "--hparams_fp",
        type=Path,
        default=Path("configs/hparams.json"),
        help="Path to the JSON file containing the hyperparameters",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config.from_files(args.hparams_fp, args.cities_fp)

    log_info("Starting the genetic algorithm...")
    trainer = GeneticTrainer(config)
    start_time = time()
    outputs = trainer.fit()
    end_time = time()
    log_info("Best individual: %s", outputs["best_individual"])
    log_info("Minimum cost using genetic algorithm: %.2f", outputs["best_fitness"])
    log_info("Genetic algorithm time taken: %.2f seconds", end_time - start_time)

    log_info("Starting the dynamic programming algorithm...")
    start_time = time()
    min_cost = tsp_dynamic_programming(config.city_coords)
    end_time = time()
    log_info("Minimum cost using dynamic programming: %.2f", min_cost)
    log_info("Dynamic programming time taken: %.2f seconds", end_time - start_time)


if __name__ == "__main__":
    main()
