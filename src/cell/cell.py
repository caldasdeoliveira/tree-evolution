import numpy as np
from src.cell.genome import Gene
import logging

from src.configs.config import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Cell:
    def __init__(
        self,
        tree_id,
        x,
        y,
        z,
        map,
        genome,
        gene: int,
        energy_consumption=1,
    ):
        self.tree_id = tree_id
        self.x = x
        self.y = y
        self.z = z
        self.genome = genome
        self.gene = self.genome.get_gene(gene)
        self.active = True
        self.energy_consumption = energy_consumption

        map.set_voxel(x, y, z, tree_id)

    def is_seed(self):
        return False

    def new_cell(self, x, y, z, map, genome, gene):
        if gene == SEEDCELL_GENE_NUMBER:
            return Seed(
                tree_id=self.tree_id,
                x=x,
                y=y,
                z=z,
                map=map,
                genome=genome,
                gene=gene,
                energy_consumption=self.energy_consumption,
            )
        else:
            return Cell(
                tree_id=self.tree_id,
                x=x,
                y=y,
                z=z,
                map=map,
                genome=genome,
                gene=gene,
                energy_consumption=self.energy_consumption,
            )

    def divide(self, map):
        new_cells = []
        if self.active:
            if self.gene.has_adjacent():
                if self.gene.get_top() != 0 and map.is_voxel_free(
                    self.x, self.y + 1, self.z
                ):
                    map.set_voxel(self.x, self.y + 1, self.z, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x,
                            y=self.y + 1,
                            z=self.z,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_top(),
                        )
                    )
                if self.gene.get_bottom() != 0 and map.is_voxel_free(
                    self.x, self.y - 1, self.z
                ):
                    map.set_voxel(self.x, self.y - 1, self.z, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x,
                            y=self.y - 1,
                            z=self.z,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_bottom(),
                        )
                    )
                if self.gene.get_left() != 0 and map.is_voxel_free(
                    self.x - 1, self.y, self.z
                ):
                    map.set_voxel(self.x - 1, self.y, self.z, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x - 1,
                            y=self.y,
                            z=self.z,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_left(),
                        )
                    )
                if self.gene.get_right() != 0 and map.is_voxel_free(
                    self.x + 1, self.y, self.z
                ):
                    map.set_voxel(self.x + 1, self.y, self.z, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x + 1,
                            y=self.y,
                            z=self.z,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_right(),
                        )
                    )
                if self.gene.get_front() != 0 and map.is_voxel_free(
                    self.x, self.y, self.z + 1
                ):
                    map.set_voxel(self.x, self.y, self.z + 1, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x,
                            y=self.y,
                            z=self.z + 1,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_front(),
                        )
                    )
                if self.gene.get_back() != 0 and map.is_voxel_free(
                    self.x, self.y, self.z - 1
                ):
                    map.set_voxel(self.x, self.y, self.z - 1, self.tree_id)
                    new_cells.append(
                        self.new_cell(
                            x=self.x,
                            y=self.y,
                            z=self.z - 1,
                            map=map,
                            genome=self.genome,
                            gene=self.gene.get_back(),
                        )
                    )

        self.active = False
        return new_cells

    def produce_energy(self, map):
        energy_produced = 0
        if self.gene.id != SEEDCELL_GENE_NUMBER:
            energy_produced = map.get_voxel_energy(self.x, self.y, self.z)
        logger.debug(f"Energy produced: {energy_produced}")
        return energy_produced

    def consume_energy(self):
        return self.energy_consumption

    def __repr__(self) -> str:
        return f"Cell({self.x}, {self.y}, {self.z}, {self.gene.id})"


class Seed(Cell):
    def __init__(self, tree_id, x, y, z, map, genome, gene, energy_consumption=1):
        super().__init__(tree_id, x, y, z, map, genome, gene, energy_consumption)
        self.genome = genome.create_offspring()
        self.energy = INITIAL_ENERGY
        self.energy_consumption = 0
        self.active = False
        self.grown = False

    def fall_to_ground(self, map):
        if self.grown == True:
            logger.debug("Seed is already grown")
            map.set_voxel(self.x, self.y, self.z, 0)

        if sum(map.voxels[self.x, 0 : self.y, self.z]) == 0:
            map.set_voxel(self.x, self.y, self.z, 0)
            map.set_voxel(self.x, 0, self.z, self.tree_id)
            self.y = 0
        else:
            logger.debug("Seed cannot fall to ground")
            map.set_voxel(self.x, self.y, self.z, 0)

    def germinate(self, map, seed_number):
        if self.y != GROUND:
            logger.debug("Seed is not on the ground")
            return None

        self.active = True
        self.energy_consumption = CELL_ENERGY_CONSUMPTION
        self.grown = True

        self.tree_id = f"{self.tree_id}.{seed_number:03}"
        map.set_voxel(self.x, self.y, self.z, self.tree_id)

        return Tree(
            self.tree_id,
            [self],
            self.genome,
            initial_energy=self.energy,
            growth_cost=GROWTH_COST,
        )
        ## TODO develop this idea further

    def is_seed(self):
        return not self.grown


class Tree:
    def __init__(self, id, cells, genome, initial_energy=100, growth_cost=1):
        self.id = id
        self.cells = cells
        self.genome = genome
        self.energy = initial_energy
        self.alive = True
        self.age = 0
        self.growth_cost = growth_cost

    def get_cell(self, id):
        return self.cells[id]

    def get_cells(self):
        return self.cells

    def get_genome(self):
        return self.genome

    def get_energy(self):
        return self.energy

    def get_age(self):
        return self.age

    def check_alive(self):
        if self.energy <= 0:
            return False
        return True

    def update_age(self):
        self.age += 1

    def update_alive(self):
        self.alive = self.check_alive()
        if self.alive == False:
            logger.info(f"Tree {self.id} has died")

    def get_seeds(self):
        return [cell for cell in self.cells if cell.is_seed()]

    def day_behaviour(self, map):
        if self.alive:
            self.update_age()
            logger.info(f"######## Start of day for Tree {self.id}")
            logger.debug(f"Tree {self.id} Energy: {self.energy}")
            self.produce_energy(map)
            self.consume_energy()
            if self.alive:
                self.grow(map)
                logger.debug(f"Tree {self.id} Energy: {self.energy}")
                logger.info(f"######## End of day for Tree {self.id}")

            return self.alive

    def consume_energy(self):
        logger.debug(f"Tree {self.id} has {self.energy} energy before comsumption")
        energy_consumption = 0
        for cell in self.cells:
            cell_energy_increase_ratio = int(
                1 + self.age * ENERGY_CONSUMPTION_INCREASE_RATE
            )
            energy_consumption += cell.energy_consumption * cell_energy_increase_ratio
        logger.info(f"Tree {self.id} Energy consumed: {energy_consumption}")

        self.energy -= energy_consumption
        logger.debug(f"Tree {self.id} has {self.energy} energy after comsumption")
        if ~self.check_alive():
            self.update_alive()

    def grow(self, map):
        if self.energy >= self.age * self.growth_cost:
            new_cells = []
            for cell in self.cells:
                new_cells = new_cells + cell.divide(map)
            self.cells = self.cells + new_cells
            if new_cells:
                self.energy -= self.age * self.growth_cost
                logger.debug(
                    f"Tree {self.id} growth cost: {self.age * self.growth_cost}"
                )
                logger.info(f"Tree {self.id} grew")
        else:
            logger.info(f"Tree {self.id} did not grow due to lack of energy")

    def die_procedure(self, map):
        logger.info(f"Tree {self.id} died")
        for cell in self.cells:
            if cell.is_seed():
                cell.fall_to_ground(map)
            else:
                map.set_voxel(cell.x, cell.y, cell.z, 0)
        return self.get_seeds()

    def produce_energy(self, map):
        energy_produced = 0
        for cell in self.cells:
            energy_produced += cell.produce_energy(map)
        logger.info(f"Tree {self.id} produced {energy_produced} energy")

        self.energy += energy_produced

    def __repr__(self) -> str:
        repr = f"##### Tree {self.id} #####\n"
        repr += f"number of cells: {len(self.cells)}\n"
        repr += f"cells: {self.cells}\n"
        repr += f"Genome: {self.genome}\n"
        repr += f"Energy: {self.energy}\n"
        repr += f"Alive: {self.alive}\n"
        repr += f"Age: {self.age}\n"
        repr += f"##########################\n"
        return repr
