import pygame
import numpy as np
import random

from shmupMachineLearningGame import *
from shmupSettings import *
from shmupNN import *

class genetic_algorithm:
    def __init__(self, genes_len = GENES_LEN, mutation_rate = MUTATION_RATE):
        self.genes_dictionary = dict()
        self.genes_len = genes_len
        self.sorted_genes = []
        self.next_generation = []
        self.fitness_sum = 0
        self.generation_num = 0
        self.mutation_rate = mutation_rate
        self.generate_ancestors()

    def sort_by_fitness(self):
        self.generation_num += 1
        print(self.fitness_sum / 10, ',')
        self.sorted_genes = sorted(self.genes_dictionary.items(), reverse = True)

    def wheel_selection(self):
        wheel_gene = []
        wheel_num = random.randint(0, self.fitness_sum)
        for couple in self.sorted_genes:
            if wheel_num <= couple[0]:
                wheel_gene = couple[1]
                break
                #print(couple[0])
            else:
                wheel_num -= couple[0]

        return wheel_gene
    
    def crossover(self, gene1, gene2):
        c_gene1 = gene1.copy()
        c_gene2 = gene2.copy()
        point = np.random.randint(0, self.genes_len)
        c_gene1[: point + 1], c_gene2[: point + 1] = c_gene2[: point + 1], c_gene1[: point + 1]
        return c_gene1, c_gene2
    
    def mutate(self, gene):
        c_gene = gene.copy()
        c_gene = np.array(c_gene)
        mutation_array = np.random.random(c_gene.shape) < self.mutation_rate
        mutation = np.random.normal(size = c_gene.shape)
        mutation[mutation_array] *= 2
        c_gene[mutation_array] += mutation[mutation_array]
        return c_gene.tolist()
    
    def evolve(self, genes_dictionary):
        self.genes_dictionary = genes_dictionary.copy()
        self.fitness_sum = 0
        for score in genes_dictionary:
            self.fitness_sum += score
            #print(len(genes_dictionary[score]))
        self.next_generation.clear()
        self.sort_by_fitness()
        #for couple in self.sorted_genes:
        #    print(couple[0])
        for i in range(5):
            gene1, gene2 = self.crossover(self.wheel_selection(),
                                          self.wheel_selection())

            gene1 = self.mutate(gene1)
            gene2 = self.mutate(gene2)
            #print(len(gene1), '\n', len(gene2))

            self.next_generation.append(gene1)
            self.next_generation.append(gene2)
    
    def generate_ancestors(self):
        for i in range(10):
            gene = np.random.uniform(-1, 1, self.genes_len)
            self.next_generation.append(gene.tolist())
            

def main():
    ga = genetic_algorithm(GENES_LEN, MUTATION_RATE)
    game = Game()
    while game.running and game.current_generation <= 20:
        game.reset(ga.next_generation)
        game.run()
        ga.evolve(game.record)

        
if __name__ == '__main__':
    main()






    

