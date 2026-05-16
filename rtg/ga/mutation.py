import random

from rtg.ga.calculate_fitness import calculate_fitness
from rtg.program.program import Program
from rtg.rv_categories.riscv_infor import riscv32_classes
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.settings import MUTATION_RATE, PROGRAM_LEN, RISCV_32_INS


def execute_mutation(
    rv_ins: BaseIntegerIns | BaseVectorIns,
) -> BaseIntegerIns | BaseVectorIns:
    if rv_ins.type == RISCVTypes.V_OPCFG:
        return rv_ins

    riscv_class = riscv32_classes[rv_ins.name]
    ins_of_type = RISCV_32_INS[RISCVTypes(rv_ins.type)]

    if issubclass(riscv_class, BaseIntegerIns):
        riscv_obj = riscv_class(random.choice(ins_of_type), rv_ins.index)
        return riscv_obj

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


def mutation(offsprings: list[Program]):
    num_offsprings: int = len(offsprings)
    for i in range(num_offsprings):
        for j in range(PROGRAM_LEN):
            if random.random() <= MUTATION_RATE:
                offsprings[i].body[j] = execute_mutation(offsprings[i].body[j])

        calculate_fitness(offsprings[i])
