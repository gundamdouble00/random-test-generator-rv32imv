import random

from rtg.program.program import Program
from rtg.settings import TEST_CASES

sum_of_ranks: int = (TEST_CASES * (TEST_CASES + 1)) // 2


def rank_selection(population: list[Program], elitism: int) -> list[Program]:
    ranks_list: list[float] = []
    selected_parents: list[Program] = []
    num_selections: int = TEST_CASES - elitism

    cumulative_prob: float = 0.0
    for i in range(TEST_CASES):
        rank = TEST_CASES - i
        cumulative_prob += rank / sum_of_ranks
        ranks_list.append(cumulative_prob)

    while len(selected_parents) < num_selections:
        position: int = -1
        left, right = 0, TEST_CASES - 1
        probability: float = random.random()

        # Binary Search
        while left <= right:
            mid = (left + right) // 2
            if ranks_list[mid] >= probability:
                position = mid
                right = mid - 1
            else:
                left = mid + 1

        selected_parents.append(population[position])

    return selected_parents
