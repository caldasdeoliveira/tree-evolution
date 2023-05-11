import numpy as np
import copy


class Gene:
    def __init__(self, id, adjacent=None, genome_size=10):
        self.id = id
        if adjacent is None:
            self.random_init(genome_size)
        else:
            self.adjacent = adjacent

    def random_init(self, genome_size):
        self.adjacent = np.random.randint(-genome_size, genome_size + 1, 6).clip(0)

    def get_top(self):
        return self.adjacent[0]

    def get_right(self):
        return self.adjacent[1]

    def get_bottom(self):
        return self.adjacent[2]

    def get_left(self):
        return self.adjacent[3]

    def get_front(self):
        return self.adjacent[4]

    def get_back(self):
        return self.adjacent[5]

    def __str__(self) -> str:
        return f"{self.id}: {', '.join([str(x) for x in self.adjacent])}"

    def __repr__(self) -> str:
        return f"{self.id}: {', '.join([str(x) for x in self.adjacent])}"

    def copy(self, deep=True):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)


class Genome:
    def __init__(self, seed=42, genome_size=10, genome=None, mutation_rate=0.1):
        self.mutation_rate = mutation_rate
        self.genome_size = genome_size
        self.seed = seed
        if genome is None:
            self.genes = self.random_init()
        else:
            self.genes = genome

    def random_init(self):
        np.random.seed(self.seed)
        genes = []
        for i in range(1, self.genome_size + 1):
            genes.append(Gene(i, genome_size=self.genome_size))
        return genes

    def get_gene(self, id):
        return self.genes[id]

    def get_genes(self):
        return self.genes

    def create_offspring(self):
        genes = np.array([])
        for gene in self.genes:
            if np.random.uniform() < self.mutation_rate:
                genes = np.append(
                    genes,
                    Gene(
                        gene.id,
                        genome_size=self.genome_size,
                    ),
                )
            else:
                genes = np.append(genes, gene.copy(deep=True))
        return Genome(genome=genes)

    def __str__(self) -> str:
        return str(self.genes)

    def __repr__(self) -> str:
        nl = "\n"
        return f"[\n{f', {nl}'.join([str(x) for x in self.genes])}\n]"

    def copy(self, deep=True):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)
