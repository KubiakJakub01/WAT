import csv
import json
from datetime import datetime
from pathlib import Path

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
    log_interval: int = 10
    log_dir: Path = Path("logs")

    def model_post_init(self, __context):
        self.log_dir = self.log_dir / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_dir.mkdir(exist_ok=True, parents=True)

    @property
    def city_coords(self):
        return {city.name: (city.x, city.y) for city in self.cities}

    @property
    def cities_names(self):
        return [city.name for city in self.cities]

    @property
    def n_cities(self):
        return len(self.cities)

    @property
    def crossover_size(self):
        return int(self.n_population * self.crossover_per)

    @property
    def mutation_size(self):
        return self.n_population - self.crossover_size

    @classmethod
    def from_files(cls, hparams_fp: Path, cities_fp: Path) -> "Config":
        with open(cities_fp, "r", encoding="utf-8") as f:
            cities = [City(**row) for row in csv.DictReader(f, delimiter="\t")]
        hparams = json.loads(hparams_fp.read_text())
        return cls(cities=cities, **hparams)
