import argparse
import json
import random
from itertools import permutations
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


def initial_population(config: Config):
    """Generating initial population of cities randomly \
        selected from the all possible permutations of the given cities. 

    Args:
        config: Config object containing the cities names
    
    Returns:
        population_perms: list of lists of cities names, each list is a permutation of the cities
    """
    population_perms = []
    possible_perms = list(permutations(config.cities_names))
    random_ids = random.sample(range(0, len(possible_perms)), config.n_population)

    for i in random_ids:
        population_perms.append(list(possible_perms[i]))

    return population_perms


def total_dist_individual(config: Config, individual):
    """
    Calculating the total distance traveled by individual,
    one individual means one possible solution (1 permutation)
    Input:
    1- Individual list of cities
    Output:
    Total distance traveled
    """

    total_dist = 0
    for i in range(0, len(individual)):
        if i == len(individual) - 1:
            total_dist += config.dist_two_cities(individual[i], individual[0])
        else:
            total_dist += config.dist_two_cities(individual[i], individual[i + 1])
    return total_dist


def fitness_prob(config, population):
    """
    Calculating the fitness probability
    Input:
    1- Population
    Output:
    Population fitness probability
    """
    total_dist_all_individuals = []
    for i in range(0, len(population)):
        total_dist_all_individuals.append(total_dist_individual(config, population[i]))

    max_population_cost = max(total_dist_all_individuals)
    population_fitness = max_population_cost - total_dist_all_individuals
    population_fitness_sum = sum(population_fitness)
    population_fitness_probs = population_fitness / population_fitness_sum
    return population_fitness_probs


def roulette_wheel(population, fitness_probs):
    """
    Implement selection strategy based on roulette wheel proportionate selection.
    Input:
    1- population
    2- fitness probabilities
    Output:
    selected individual
    """
    population_fitness_probs_cumsum = fitness_probs.cumsum()
    bool_prob_array = population_fitness_probs_cumsum < np.random.uniform(0, 1, 1)
    selected_individual_index = len(bool_prob_array[bool_prob_array]) - 1
    return population[selected_individual_index]


def crossover(config: Config, parent_1, parent_2):
    """
    Implement mating strategy using simple crossover between 2 parents
    Input:
    1- parent 1
    2- parent 2
    Output:
    1- offspring 1
    2- offspring 2
    """
    n_cities_cut = config.n_cities - 1
    cut = round(random.uniform(1, n_cities_cut))
    offspring_1 = []
    offspring_2 = []

    offspring_1 = parent_1[0:cut]
    offspring_1 += [city for city in parent_2 if city not in offspring_1]

    offspring_2 = parent_2[0:cut]
    offspring_2 += [city for city in parent_1 if city not in offspring_2]

    return offspring_1, offspring_2


def mutation(config: Config, offspring):
    """
    Implement mutation strategy in a single offspring
    Input:
    1- offspring individual
    Output:
    1- mutated offspring individual
    """
    n_cities_cut = config.n_cities - 1
    index_1 = round(random.uniform(0, n_cities_cut))
    index_2 = round(random.uniform(0, n_cities_cut))

    temp = offspring[index_1]
    offspring[index_1] = offspring[index_2]
    offspring[index_2] = temp
    return offspring


def draw_parents(config: Config, population, fitness_probs):
    return [
        roulette_wheel(population, fitness_probs)
        for _ in range(int(config.crossover_per * config.n_population))
    ]


def create_offspring(config: Config, parents_list):
    offspring_list = []
    for i in range(0, len(parents_list), 2):
        offspring_1, offspring_2 = crossover(
            config, parents_list[i], parents_list[i + 1]
        )

        mutate_threashold = random.random()
        if mutate_threashold > (1 - config.mutation_per):
            offspring_1 = mutation(config, offspring_1)

        mutate_threashold = random.random()
        if mutate_threashold > (1 - config.mutation_per):
            offspring_2 = mutation(config, offspring_2)

        offspring_list.append(offspring_1)
        offspring_list.append(offspring_2)
    return offspring_list


def run_ga(config: Config):
    population = initial_population(config)
    fitness_probs = fitness_prob(config, population)
    parents_list = draw_parents(config, population, fitness_probs)
    offspring_list = create_offspring(config, parents_list)
    mixed_offspring = parents_list + offspring_list

    fitness_probs = fitness_prob(config, mixed_offspring)
    sorted_fitness_indices = np.argsort(fitness_probs)[::-1]
    best_fitness_indices = sorted_fitness_indices[0 : config.n_population]
    best_mixed_offsrping = []
    for i in best_fitness_indices:
        best_mixed_offsrping.append(mixed_offspring[i])

    for i in range(0, config.n_generations):
        if i % 10 == 0:
            log_info(
                f"Generation: {i=}, Best fitness: {total_dist_individual(config, best_mixed_offsrping[0])}"
            )

        fitness_probs = fitness_prob(config, best_mixed_offsrping)
        parents_list = draw_parents(config, best_mixed_offsrping, fitness_probs)
        offspring_list = create_offspring(config, parents_list)
        mixed_offspring = parents_list + offspring_list
        fitness_probs = fitness_prob(config, mixed_offspring)
        sorted_fitness_indices = np.argsort(fitness_probs)[::-1]
        best_fitness_indices = sorted_fitness_indices[
            0 : int(0.8 * config.n_population)
        ]

        best_mixed_offsrping = []
        for i in best_fitness_indices:
            best_mixed_offsrping.append(mixed_offspring[i])

        old_population_indices = [
            random.randint(0, (config.n_population - 1))
            for _ in range(int(0.2 * config.n_population))
        ]
        for i in old_population_indices:
            best_mixed_offsrping.append(population[i])

        random.shuffle(best_mixed_offsrping)

    return best_mixed_offsrping


def main():
    args = parse_args()
    config = Config.from_files(args.hparams_fp, args.cities_fp)
    log_info("Loaded config:\n%s", json.dumps(config.model_dump(), indent=2))

    trainer = GeneticTrainer(config)
    best_individual = trainer.fit()
    log_info(
        "Best individual found by the algorithm: %s", best_individual
    )

    # best_mixed_offsrping = run_ga(config)
    # total_dist_all_individuals = []
    # for i in range(0, config.n_population):
    #     total_dist_all_individuals.append(
    #         total_dist_individual(config, best_mixed_offsrping[i])
    #     )
    # index_minimum = np.argmin(total_dist_all_individuals)
    # minimum_distance = min(total_dist_all_individuals)
    # print("Minimum distance: ", minimum_distance)
    # shortest_path = best_mixed_offsrping[index_minimum]
    # print("Shortest path: ", shortest_path)


if __name__ == "__main__":
    main()
