import concurrent.futures
import itertools
import os
import random
from copy import deepcopy

from rtg.program.program import Program
from rtg.settings import CROSSOVER_RATE, PROGRAM_LEN


def uniform_crossover(parent1: Program, parent2: Program):
    offspring1 = Program()
    offspring2 = Program()

    for i in range(PROGRAM_LEN):
        if random.random() < 0.5:
            offspring1.body.append(parent1.body[i])
            offspring2.body.append(parent2.body[i])
        else:
            offspring1.body.append(parent2.body[i])
            offspring2.body.append(parent1.body[i])

    return [offspring1, offspring2]


def execute_crossover(parent1: Program, parent2: Program, probability: float):
    if probability >= CROSSOVER_RATE:
        offspring1 = deepcopy(parent1)
        offspring2 = deepcopy(parent2)
        return [offspring1, offspring2]

    # probability <= CROSSOVER_RATE
    return uniform_crossover(parent1, parent2)


def crossover(parents: list[Program]) -> list[Program]:
    len_parents: int = len(parents)
    middle_index: int = len_parents // 2

    pool_1 = parents[: middle_index + 1]
    pool_2 = parents[middle_index + 1 :]

    parent1 = random.choices(pool_1, k=len_parents)
    parent2 = random.choices(pool_2, k=len_parents)
    probabilities = [random.random() for _ in range(len_parents)]

    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results_iterator = executor.map(
            execute_crossover, parent1, parent2, probabilities
        )
        result = list(itertools.chain.from_iterable(results_iterator))

    return result
