import argparse
import json
from pathlib import Path

import numpy as np

from .config import Config
from .trainer import GeneticTrainer
from .utils import log_info


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
    log_info("Loaded config:\n%s", json.dumps(config.model_dump(), indent=2))

    trainer = GeneticTrainer(config)
    outputs = trainer.fit()
    log_info("Best individual: %s", outputs["best_individual"])
    log_info("Best fitness: %.2f", outputs["best_fitness"])


if __name__ == "__main__":
    main()
