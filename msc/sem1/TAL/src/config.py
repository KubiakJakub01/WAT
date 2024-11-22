import csv
import json
from pathlib import Path

import numpy as np
from pydantic import BaseModel


class City(BaseModel):
    name: str
    x: float
    y: float


class Config(BaseModel):
    cities: list[City]
    n_population: int = 250
    n_generations: int = 200
    crossover_per: float = 0.8
    mutation_per: float = 0.2

    @property
    def city_coords(self):
        return {city.name: (city.x, city.y) for city in self.cities}

    @property
    def cities_names(self):
        return [city.name for city in self.cities]

    @property
    def n_cities(self):
        return len(self.cities)

    @classmethod
    def from_files(cls, hparams_fp: Path, cities_fp: Path) -> "Config":
        with open(cities_fp, "r", encoding="utf-8") as f:
            cities = [City(**row) for row in csv.DictReader(f, delimiter="\t")]
        hparams = json.loads(hparams_fp.read_text())
        return cls(cities=cities, **hparams)

    def dist_two_cities(self, city_1, city_2):
        """Calculating the distance between two cities

        Args:
            city_1: City one name
            city_2: City two name

        Returns:
            Calculated Euclidean distance between two cities
        """
        city_coords = self.city_coords
        return np.sqrt(
            np.sum((np.array(city_coords[city_1]) - np.array(city_coords[city_2])) ** 2)
        )
