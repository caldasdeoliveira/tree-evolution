from src.world.map import Map
from src.cell.cell import Cell, Tree
from src.cell.genome import Genome

import numpy as np
import random

# %matplotlib notebook
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from src.configs.config import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

## create world
world = Map(WORLD_WIDTH, WORLD_HEIGHT, WORLD_DEPTH, SUN_VALUE, BLOCK_DECREASE)
world.update_energy_map()


## create population
population = []
for i in range(1, INITIAL_POPULATION_SIZE + 1):
    x = np.random.randint(0, WORLD_WIDTH)
    y = 0
    z = np.random.randint(0, WORLD_DEPTH)
    id = f"{i:03}"
    cell = Cell(
        tree_id=id,
        x=x,
        y=y,
        z=z,
        map=world,
        genome=Genome(
            seed=GENOME_SEED,
            genome_size=GENOME_SIZE,
            mutation_rate=GENOME_MUTATION_RATE,
        ),
        gene=1,
        energy_consumption=CELL_ENERGY_CONSUMPTION,
    )
    population.append(
        Tree(
            id,
            [cell],
            cell.genome,
            initial_energy=INITIAL_ENERGY,
            growth_cost=GROWTH_COST,
        )
    )

## run experiment
logger.info("Starting experiment")
world_history = [world.copy(deep=True)]
historic_population = []
world.plot_voxels()
for t in range(EXPERIMENT_DURATION):
    logger.info(f"Day {t}")
    logger.info(f"Population size: {len(population)}")
    random.shuffle(population)
    for tree in population:
        world.update_energy_map()
        still_alive = tree.day_behaviour(map=world)
        if not still_alive:
            offspring = tree.die_procedure(map=world)
            historic_population.append(tree)
            population.remove(tree)
            for seed_number, seed in enumerate(offspring):
                new_seed = seed.germinate(map=world, seed_number=seed_number)
                if new_seed is not None:
                    population.append(new_seed)
    world.plot_voxels()
    world_history.append(world.copy(deep=True))


