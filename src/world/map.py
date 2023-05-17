import numpy as np
import copy
import logging
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from src.configs.config import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Map:
    def __init__(
        self, width=10000, height=100, depth=10000, sun_value=5, block_decrease=1
    ):
        self.width = width
        self.height = height
        self.depth = depth

        self.sun_value = sun_value
        self.block_decrease = block_decrease

        self.voxels = np.zeros((width, height, depth), dtype=np.uint8)
        self.energy_map = np.zeros((width, height, depth), dtype=np.uint8)

        self.color_map = {}

    def get_voxel(self, x, y, z):
        return self.voxels[x, y, z]

    def set_voxel(self, x, y, z, value):
        if isinstance(value, str):
            value = int(value.replace(".", ""))
        logger.debug(f"Setting voxel {x}, {y}, {z} to {value}")
        self.voxels[x, y, z] = value

    def get_voxel_energy(self, x, y, z):
        return self.energy_map[x, y, z]

    def set_voxel_energy(self, x, y, z, value):
        self.energy_map[x, y, z] = value

    def is_voxel_occupied(self, x, y, z):
        if (
            (x >= 0)
            and (x < self.width)
            and (z >= 0)
            and (z < self.depth)
            and (y >= 0)
            and (y < self.height)
        ):
            if self.get_voxel(x, y, z) != 0:
                return True
        return False

    def is_voxel_free(self, x, y, z):
        if (
            (x >= 0)
            and (x < self.width)
            and (z >= 0)
            and (z < self.depth)
            and (y >= 0)
            and (y < self.height)
        ):
            if self.get_voxel(x, y, z) == 0:
                return True
        return False

    def update_energy_map(self):
        """
        Update energy map based on sun value and block decrease.
        Sun value is the amount of energy at the highest layer of the map.
        Energy is propagated downwards until it reaches a occupied voxel,
        that voxel will decrease the energy in the voxels below by `block_decrease`."""
        self.energy_map = np.zeros(
            (self.width, self.height, self.depth), dtype=np.uint8
        )
        for x in range(self.width):
            for z in range(self.depth):
                energy_left = self.sun_value
                self.set_voxel_energy(x, self.height - 1, z, energy_left)
                for y in range(self.height - 2, -1, -1):
                    self.set_voxel_energy(x, y, z, energy_left)
                    if self.is_voxel_occupied(x, y, z):
                        energy_left -= self.block_decrease
                        if energy_left < 0:
                            energy_left = 0

    def __repr__(self) -> str:
        repr = f"Map("
        repr += f"width={self.width}, "
        repr += f"height={self.height}, "
        repr += f"depth={self.depth}, "
        repr += f"sun_value={self.sun_value}, "
        repr += f"block_decrease={self.block_decrease})"
        repr += "\n"
        repr += f"Voxels:\n{self.voxels}"
        repr += "\n"
        repr += f"Energy:\n{self.energy_map}"
        return repr

    def copy(self, deep=True):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)

    def plot_voxels(self):
        voxelarray = self.voxels != 0

        colors = np.empty(voxelarray.shape, dtype=object)
        for i in np.unique(self.voxels):
            if i == 0:
                continue

            if i not in self.color_map:
                self.color_map[i] = np.random.choice(
                    list(mcolors.CSS4_COLORS.values()), replace=False
                )

            colors[self.voxels == i] = self.color_map[i]

        ax = plt.figure().add_subplot(projection="3d")
        ax.voxels(voxelarray, facecolors=colors, edgecolor="k")

        plt.show(block=True)
