import concurrent.futures
import os
from collections import defaultdict

from rtg.program.program import Program
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.v_extension.base_vector import LoadsStores
from rtg.settings import (
    DATA_HAZARD_SCORE,
    NEGATIVE_IMM_SCORE,
    PENALTY_PER_MISSING,
    PROGRAM_INS,
    PROGRAM_LEN,
    SAME_OPERANDS_SCORE,
)


def is_integer_num(s: str):
    try:
        return int(s)
    except Exception:
        return False


def data_hazards(dictionary: dict[str, int], value: str):
    if value in dictionary and dictionary[value] != 0:
        return DATA_HAZARD_SCORE
    return 0


def reg_dictionary(dictionary: dict[str, int], value: str):
    if is_integer_num(value) or value == "":
        return
    dictionary[value] += 1


def update_dictionary(dictionary: dict[str, int], value: str):
    if value in dictionary:
        dictionary[value] -= 1


def same_registers(regs: set[str], cur_reg: str):
    if not is_integer_num(cur_reg) and cur_reg in regs and cur_reg != "":
        return SAME_OPERANDS_SCORE
    return 0


def calculate_fitness(individual: Program):
    # Update number of types and number of instructions in individual.body
    individual.update_numbers_type()
    individual.update_numbers_ins()

    fitness_score: float = 0.0
    for type, want in PROGRAM_INS.items():
        # Subtract score if the program doesn't have enough instructions in a type
        if want == 0:
            continue

        actual = individual.count_type[type]
        if want > actual:
            fitness_score -= PENALTY_PER_MISSING

        # Calculate variety of instructions in a specific type
        if actual == 0:
            continue

        min_num: int = PROGRAM_LEN
        cur_type_ins = individual.count_ins[type]
        for nums in cur_type_ins.values():
            min_num = min(min_num, nums)
        variety: float = (min_num * len(cur_type_ins)) / actual

        fitness_score += variety

    # Data Hazards - Using "Sliding Window" for calculating hazard score
    des_reg: dict[str, int] = defaultdict(int)
    src_reg: dict[str, int] = defaultdict(int)

    for i in range(0, PROGRAM_LEN):
        cur_ins = individual.body[i]
        src3: str = ""

        # Read After Write (RAW)
        fitness_score += data_hazards(des_reg, cur_ins.src1)
        fitness_score += data_hazards(des_reg, cur_ins.src2)
        if isinstance(cur_ins, (BaseIntegerIns, LoadsStores)):
            src3 = cur_ins.src3
            fitness_score += data_hazards(des_reg, cur_ins.src3)

        # Write After Read - WAR
        fitness_score += data_hazards(src_reg, cur_ins.des)

        # Write After Write - WAW
        fitness_score += data_hazards(des_reg, cur_ins.des)

        # Current instruction has same registers
        fitness_score += same_registers({cur_ins.src1, cur_ins.src2}, cur_ins.des)
        fitness_score += same_registers({cur_ins.src1, cur_ins.src2}, src3)

        reg_dictionary(des_reg, cur_ins.des)
        reg_dictionary(src_reg, cur_ins.src1)
        reg_dictionary(src_reg, cur_ins.src2)
        if isinstance(cur_ins, (BaseIntegerIns, LoadsStores)):
            reg_dictionary(src_reg, cur_ins.src3)

        if isinstance(cur_ins, BaseIntegerIns):
            num = is_integer_num(cur_ins.imm)
        else:
            num = is_integer_num(cur_ins.src1)
        if num and num < 0:
            fitness_score += NEGATIVE_IMM_SCORE

        if i > 6:
            cur_ins = individual.body[i - 7]
            update_dictionary(des_reg, cur_ins.des)
            update_dictionary(src_reg, cur_ins.src1)
            update_dictionary(src_reg, cur_ins.src2)
            if isinstance(cur_ins, (BaseIntegerIns, LoadsStores)):
                update_dictionary(src_reg, cur_ins.src3)

    individual.fitness = fitness_score


def cal_non_multithreading(population: list[Program]):
    for individual in population:
        calculate_fitness(individual)


def fitness_multithreading(population: list[Program]):
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(calculate_fitness, individual) for individual in population
        ]
        _ = concurrent.futures.wait(futures)
