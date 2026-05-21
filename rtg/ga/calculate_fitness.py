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


def is_integer(s: str) -> int | bool:
    try:
        return int(s)
    except Exception:
        return False


def data_hazards(dictionary: dict[str, int], value: str):
    """
    # Read after Write (RAW)\n
    add r1, --, --;\n
    sub --, r1, --;\n

    # Write after Read (WAR)\n
    add --, r1, --; \n
    sub r1, --, --; \n

    # Write after Write (WAW)\n
    add r1, --, --;\n
    sub r1, --, --;\n
    """
    if (value in dictionary) and (dictionary[value] != 0):
        return DATA_HAZARD_SCORE
    return 0


def update_reg_dict(dictionary: dict[str, int], register: str, value: int):
    if len(register) != 3:
        return
    if (register[0] not in {"v", "x"}) or (not is_integer(register[1:])):
        return
    dictionary[register] += value


def same_registers(regs: set[str], cur_reg: str):
    if (not is_integer(cur_reg)) and (cur_reg in regs) and (cur_reg != ""):
        return SAME_OPERANDS_SCORE
    return 0


def calculate_fitness(individual: Program):
    # Update number of types and number of instructions in individual.body
    individual.update_numbers_type()
    individual.update_numbers_ins()

    fitness_score: float = 0.0
    for type, want in PROGRAM_INS.items():
        if want == 0:
            continue

        # Subtract score if the program doesn't have enough instructions in a type
        actual = individual.count_type[type]
        if want > actual:
            fitness_score -= PENALTY_PER_MISSING

        # Calculate variety of instructions in a specific type
        if actual == 0:
            continue

        min_num: int = PROGRAM_LEN
        cur_type_ins = individual.count_ins[type]
        for nums in cur_type_ins.values():
            if nums != 0:
                min_num = min(min_num, nums)
        variety: float = (min_num * len(cur_type_ins)) / actual
        fitness_score += variety

    # Data Hazards - Using "Sliding Window" for calculating hazard score
    des_reg: dict[str, int] = defaultdict(int)  # Destination Registers Set
    src_reg: dict[str, int] = defaultdict(int)  # Source Registers Set
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

        # Update the number of registers in des_reg and src_reg
        update_reg_dict(des_reg, cur_ins.des, 1)
        update_reg_dict(src_reg, cur_ins.src1, 1)
        update_reg_dict(src_reg, cur_ins.src2, 1)
        if isinstance(cur_ins, (BaseIntegerIns, LoadsStores)):
            update_reg_dict(src_reg, cur_ins.src3, 1)

        # Negative immediate score
        num = (
            is_integer(cur_ins.imm)
            if isinstance(cur_ins, BaseIntegerIns)
            else is_integer(cur_ins.src1)
        )
        if num and num < 0:
            fitness_score += NEGATIVE_IMM_SCORE

        # Decrease the number of instruction's registers in des_reg and src_reg
        if i > 6:
            cur_ins = individual.body[i - 7]
            update_reg_dict(des_reg, cur_ins.des, -1)
            update_reg_dict(src_reg, cur_ins.src1, -1)
            update_reg_dict(src_reg, cur_ins.src2, -1)
            if isinstance(cur_ins, (BaseIntegerIns, LoadsStores)):
                update_reg_dict(src_reg, cur_ins.src3, -1)

    individual.fitness = fitness_score


def fitness_evaluation(population: list[Program]):
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(calculate_fitness, individual) for individual in population
        ]
        _ = concurrent.futures.wait(futures)
