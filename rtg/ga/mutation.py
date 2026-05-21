import concurrent.futures
import os
import random

from rtg.program.program import Program
from rtg.rv_categories.riscv_infor import riscv32_classes
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.settings import MUTATION_RATE, PROGRAM_LEN, RISCV_32_INS


def mutate_instruction(
    rv_ins: BaseIntegerIns | BaseVectorIns,
) -> BaseIntegerIns | BaseVectorIns:
    if rv_ins.type == RISCVTypes.V_OPCFG:
        return rv_ins

    riscv_class = riscv32_classes[rv_ins.name]
    ins_of_type = RISCV_32_INS[RISCVTypes(rv_ins.type)]

    if issubclass(riscv_class, BaseIntegerIns):
        return riscv_class(random.choice(ins_of_type), rv_ins.index)

    mutated_ins: list[BaseVectorIns] = []
    for vector_ins in ins_of_type:
        try:
            if isinstance(rv_ins, BaseVectorIns):
                riscv_obj = riscv_class(
                    vector_ins, rv_ins.index, rv_ins.lmul, rv_ins.sew
                )
                mutated_ins.append(riscv_obj)
        except ValueError:
            continue

    if len(mutated_ins) == 0:
        return rv_ins

    return random.choice(mutated_ins)


def execute_mutation(asm_program: Program):
    for i in range(PROGRAM_LEN):
        if random.random() < MUTATION_RATE:
            asm_program.body[i] = mutate_instruction(asm_program.body[i])


def mutation(offsprings: list[Program]):
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(max_workers // 2, 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results_iterator = executor.map(execute_mutation, offsprings)
        _ = list(results_iterator)
