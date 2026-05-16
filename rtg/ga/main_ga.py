from rtg.ga.calculate_fitness import fitness_multithreading
from rtg.ga.crossover import crossover
from rtg.ga.initialization import initialization
from rtg.ga.mutation import mutation
from rtg.ga.selection import rank_selection
from rtg.ga.utils import add_label_loop, save_to_file, set_up_link_origin
from rtg.program.program import Program
from rtg.settings import NUM_GENERATIONS, PROGRAM_INS, RV32_RATES, TEST_CASES


def genetic_algorithm():
    # Initialize Population
    population: list[Program] = initialization()

    # # Calculate Individuals' fitness
    # fitness_multithreading(population)

    # # Start Evolutionary Generational Cycle
    # for _ in range(NUM_GENERATIONS):
    #     # Sort the population in decreasing order of fitness score
    #     population = sorted(population, key=lambda x: x.fitness, reverse=True)

    #     # Generate new offsprings for new generation
    #     new_generation: list[Program] = []

    #     # Perform Elitism, that mean 5% of fittest population goes to the next generation
    #     elitism = int((5 * TEST_CASES) / 100)
    #     new_generation.extend(population[:elitism])

    #     # Selection
    #     selected_parents = rank_selection(population, elitism)

    #     # Crossover
    #     offsprings = crossover(selected_parents)

    #     # Mutation
    #     mutation(offsprings)

    #     # New Generation Formation
    #     offsprings.extend(population[elitism:])
    #     new_generation.extend(offsprings)
    #     population = new_generation[:TEST_CASES]

    for i in range(TEST_CASES):
        add_label_loop(population[i])

    save_to_file(population)

    set_up_link_origin()
