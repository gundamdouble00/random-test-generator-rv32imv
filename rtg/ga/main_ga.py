from rtg.ga.calculate_fitness import fitness_evaluation
from rtg.ga.crossover import crossover
from rtg.ga.initialization import initialization
from rtg.ga.mutation import mutation
from rtg.ga.selection import rank_selection
from rtg.ga.utils import add_label_loop, save_to_file, set_up_link_origin
from rtg.program.program import Program
from rtg.settings import NUM_GENERATIONS, TEST_CASES


def genetic_algorithm():
    # Initialize Population
    population: list[Program] = initialization()

    # Start Evolutionary Generational Cycle
    new_generation: list[Program] = []
    for _ in range(NUM_GENERATIONS):
        # Calculate Individuals' fitness
        fitness_evaluation(population)

        # Sort the population in decreasing order of fitness score
        population = sorted(population, key=lambda x: x.fitness, reverse=True)

        # Generate new offsprings for new generation
        new_generation = []

        # Perform Elitism, that mean 5% of fittest population goes to the next generation
        elitism = (5 * TEST_CASES) // 100
        new_generation.extend(population[:elitism])

        # Selection
        selected_parents = rank_selection(population, elitism)

        # Crossover
        offsprings = crossover(selected_parents)

        # Mutation
        mutation(offsprings)

        # New Generation Formation
        offsprings.extend(population[elitism:])
        new_generation.extend(offsprings)
        population = new_generation[:TEST_CASES]

    fitness_evaluation(population)
    population = sorted(population, key=lambda x: x.fitness, reverse=True)

    for i in range(TEST_CASES):
        add_label_loop(population[i])

    save_to_file(population)

    set_up_link_origin()
