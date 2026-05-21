import concurrent.futures
import itertools
import os
import random
from copy import deepcopy

from rtg.program.program import Program
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.rv_instructions.v_extension.base_vector import ConfigurationSetting
from rtg.settings import CROSSOVER_RATE, HAS_VECTOR, PROGRAM_LEN


def get_cfg_ins(individual: Program) -> list[list[BaseIntegerIns | BaseVectorIns]]:
    temp_list: list[BaseIntegerIns | BaseVectorIns] = []
    result: list[list[BaseIntegerIns | BaseVectorIns]] = []

    for i in range(len(individual.body)):
        cur_ins = individual.body[i]
        if cur_ins.type != RISCVTypes.V_OPCFG:
            temp_list.append(cur_ins)
            continue

        # cur_ins.type == RISCVTypes.V_OPCFG
        if len(temp_list) != 0:
            if temp_list[0].type != RISCVTypes.V_OPCFG:
                cfg_obj = ConfigurationSetting("vsetvli", 0, 8.0, 32)
                cfg_obj.sew, cfg_obj.lmul = 32, 8.0
                temp_list.insert(0, cfg_obj)

            result.append(temp_list)

        temp_list = [cur_ins]

    result.append(temp_list)
    return result


def random_sampling_crossover(parent1: Program, parent2: Program):
    gene1, gene2 = get_cfg_ins(parent1), get_cfg_ins(parent2)
    pool: list[list[BaseIntegerIns | BaseVectorIns]] = []
    pool = gene1 + gene2
    random.shuffle(pool)

    offspring1 = Program()
    for gene in pool:
        if len(offspring1.body) > PROGRAM_LEN:
            break
        offspring1.body.extend(gene)
    offspring1.body = offspring1.body[:PROGRAM_LEN]

    offspring2 = Program()
    total_length, flag = 0, -1
    for i in range(len(pool) - 1, -1, -1):
        total_length += len(pool[i])
        if total_length > PROGRAM_LEN:
            flag = i
            break
    for i in range(flag, len(pool)):
        offspring2.body.extend(pool[i])
    offspring2.body = offspring2.body[:PROGRAM_LEN]

    return [offspring1, offspring2]


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
    if probability > CROSSOVER_RATE:
        offspring1 = deepcopy(parent1)
        offspring2 = deepcopy(parent2)
        return [offspring1, offspring2]

    # probability <= CROSSOVER_RATE
    # Have "V" Extension Instruction
    if HAS_VECTOR:
        return random_sampling_crossover(parent1, parent2)
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
