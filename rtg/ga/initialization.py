import concurrent.futures
import os

from rtg.program.generator import generate_random_program
from rtg.program.program import Program
from rtg.settings import TEST_CASES


def initialization_multithreading():
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(generate_random_program, range(TEST_CASES)))
    return results


def initialization() -> list[Program]:
    result = initialization_multithreading()

    return result
