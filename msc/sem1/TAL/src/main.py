import argparse
import math
from pathlib import Path
from time import time

from memory_profiler import memory_usage

from .config import Config
from .trainer import GeneticTrainer
from .tsp_dp import tsp_dynamic_programming
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


def fn_with_memory_time_profiling(fn, *args, **kwargs):
    start_time = time()
    mem_usage, result = memory_usage((fn, args, kwargs), retval=True)
    end_time = time()
    return result, end_time - start_time, mem_usage


def main():
    args = parse_args()
    config = Config.from_files(args.hparams_fp, args.cities_fp)

    log_info("Number of cities: %d", len(config.cities))
    log_info("Starting the dynamic programming algorithm...")
    min_cost, run_time, mem_usage = fn_with_memory_time_profiling(
        tsp_dynamic_programming, config.city_coords
    )
    log_info("Minimum cost using dynamic programming: %.2f", min_cost)
    log_info("Dynamic programming time taken: %.2f seconds", run_time)
    log_info("Dynamic programming memory usage: %.6f MB", max(mem_usage) - min(mem_usage))

    log_info("Starting the genetic algorithm...")
    trainer = GeneticTrainer(config)
    outputs, run_time, mem_usage = fn_with_memory_time_profiling(
        trainer.fit, stop_threshold=math.ceil(min_cost)
    )
    log_info("Best individual: %s", outputs["best_individual"])
    log_info("Minimum cost using genetic algorithm: %.2f", outputs["best_fitness"])
    log_info("Genetic algorithm time taken: %.2f seconds", run_time)
    log_info("Genetic algorithm memory usage: %.6f MB", max(mem_usage) - min(mem_usage))


if __name__ == "__main__":
    main()
