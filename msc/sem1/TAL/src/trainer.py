import random
from itertools import permutations

import numpy as np
from torch.utils.tensorboard import SummaryWriter

from .config import Config
from .utils import euclidean_distance, log_info, plot_route


class GeneticTrainer:
    def __init__(self, config: Config):
        self.config = config
        self.writer = SummaryWriter(self.config.log_dir)
        self.writer.add_text(
            "config", config.model_dump_json(exclude=("log_dir", "cities"), indent=2)
        )

    def fit(self):
        """Implementing the genetic algorithm to find the optimal solution for the TSP problem

        Returns:
            outputs: Dictionary containing the best individual and best fitness
        """
        outputs = {}
        population = self.initial_population()
        for i in range(0, self.config.n_generations):
            self._log(i, population)
            fitness_probs = self.fitness_prob(population)
            parents_list = self.draw_parents(population, fitness_probs)
            offspring_list = self.create_offspring(parents_list)
            mixed_offspring = parents_list + offspring_list
            fitness_probs = self.fitness_prob(mixed_offspring)
            sorted_fitness_indices = np.argsort(fitness_probs)[::-1]
            best_fitness_indices = sorted_fitness_indices[
                0 : self.config.crossover_size
            ]

            best_mixed_offspring = []
            for i in best_fitness_indices:
                best_mixed_offspring.append(mixed_offspring[i])

            old_population_indices = [
                random.randint(0, (self.config.n_population - 1))
                for _ in range(self.config.mutation_size)
            ]
            for i in old_population_indices:
                best_mixed_offspring.append(population[i])

            random.shuffle(best_mixed_offspring)
            population = best_mixed_offspring

        best_individual = self.best_individual(population)
        outputs = {
            "best_individual": best_individual,
            "best_fitness": self.total_dist_individual(best_individual),
        }
        return outputs

    def initial_population(self):
        """Generating initial population of cities randomly \
            selected from the all possible permutations of the given cities. 

        Returns:
            population_perms: list of lists of cities names, each list is a permutation of the cities
        """
        all_permutations = permutations(self.config.cities_names)
        population_perms = []
        for _ in range(self.config.n_population):
            population_perms.append(list(next(all_permutations)))
        return population_perms

    def total_dist_individual(self, individual):
        """Calculating the total distance traveled by individual, \
        one individual means one possible solution (1 permutation)

        Args:
            individual: List of cities names

        Returns:
            Total distance traveled
        """
        total_dist = 0
        for i in range(0, len(individual)):
            if i == len(individual) - 1:
                total_dist += self._dist_to_cities(individual[i], individual[0])
            else:
                total_dist += self._dist_to_cities(individual[i], individual[i + 1])
        return total_dist

    def fitness_prob(self, population):
        """Calculating the fitness probability

        Args:
            population: Population of individuals

        Returns:
            Population fitness probability
        """
        total_dist_all_individuals = []
        for i in range(0, len(population)):
            total_dist_all_individuals.append(self.total_dist_individual(population[i]))

        max_population_cost = max(total_dist_all_individuals)
        population_fitness = max_population_cost - total_dist_all_individuals
        population_fitness_sum = sum(population_fitness)
        population_fitness_probs = population_fitness / population_fitness_sum
        return population_fitness_probs

    def roulette_wheel(self, population, fitness_probs):
        """Implement selection strategy based on roulette wheel proportionate selection.

        Args:
            population: Population of individuals
            fitness_probs: Population fitness probability

        Returns:
            Selected individual
        """
        population_fitness_probs_cumsum = fitness_probs.cumsum()
        bool_prob_array = population_fitness_probs_cumsum < np.random.uniform(0, 1, 1)
        selected_individual_index = len(bool_prob_array[bool_prob_array]) - 1
        return population[selected_individual_index]

    def crossover(self, parent_1, parent_2):
        """Implement mating strategy using simple crossover between 2 parents

        Args:
            parent_1: First parent
            parent_2: Second parent

        Returns:
            offspring_1: First offspring
            offspring_2: Second offspring
        """
        n_cities_cut = self.config.n_cities - 1
        cut = round(random.uniform(1, n_cities_cut))
        offspring_1 = []
        offspring_2 = []

        offspring_1 = parent_1[0:cut]
        offspring_1 += [city for city in parent_2 if city not in offspring_1]

        offspring_2 = parent_2[0:cut]
        offspring_2 += [city for city in parent_1 if city not in offspring_2]

        return offspring_1, offspring_2

    def mutation(self, offspring):
        """Implement mutation strategy in a single offspring

        Args:
            offspring: Offspring individual

        Returns:
            Mutated offspring
        """
        n_cities_cut = self.config.n_cities - 1
        index_1 = round(random.uniform(0, n_cities_cut))
        index_2 = round(random.uniform(0, n_cities_cut))

        temp = offspring[index_1]
        offspring[index_1] = offspring[index_2]
        offspring[index_2] = temp
        return offspring

    def draw_parents(self, population, fitness_probs):
        """Drawing parents from the population based on fitness probabilities

        Args:
            population: Population of individuals
            fitness_probs: Population fitness probability

        Returns:
            List of selected parents
        """
        return [
            self.roulette_wheel(population, fitness_probs)
            for _ in range(int(self.config.crossover_per * self.config.n_population))
        ]

    def create_offspring(self, parents_list):
        """Creating offspring from the selected parents

        Args:
            parents_list: List of selected parents

        Returns:
            List of offspring
        """
        offspring_list = []
        for i in range(0, len(parents_list), 2):
            offspring_1, offspring_2 = self.crossover(
                parents_list[i], parents_list[i + 1]
            )

            mutate_threashold = random.random()
            if mutate_threashold > (1 - self.config.mutation_per):
                offspring_1 = self.mutation(offspring_1)

            mutate_threashold = random.random()
            if mutate_threashold > (1 - self.config.mutation_per):
                offspring_2 = self.mutation(offspring_2)

            offspring_list.append(offspring_1)
            offspring_list.append(offspring_2)
        return offspring_list

    def best_individual(self, population):
        """Finding the best individual from the population

        Args:
            population: Population of individuals

        Returns:
            Best individual
        """
        total_dist_all_individuals = []
        for i in range(0, len(population)):
            total_dist_all_individuals.append(self.total_dist_individual(population[i]))

        best_individual_index = total_dist_all_individuals.index(
            min(total_dist_all_individuals)
        )
        best_individual = population[best_individual_index]

        return best_individual

    def _dist_to_cities(self, city_1: str, city_2: str):
        """Calculating the distance between two cities

        Args:
            city_1: City one name
            city_2: City two name

        Returns:
            Calculated Euclidean distance between two cities
        """
        city_coords = self.config.city_coords
        return euclidean_distance(city_coords[city_1], city_coords[city_2])

    def _log(self, n_generation, population):
        """Logging the information to tensorboard

        Args:
            n_generation: Current generation number
            population: Population of individuals
        """
        if n_generation % self.config.log_interval == 0:
            fitness = self.total_dist_individual(self.best_individual(population))
            log_info("Generation: %d, Best fitness: %.2f", n_generation, fitness)
            self.writer.add_scalar("fitness", fitness, n_generation)
            route_plot = plot_route(
                self.config,
                self.best_individual(population),
                fitness,
                n_generation,
            )
            self.writer.add_image("route", route_plot, n_generation, dataformats="HWC")
