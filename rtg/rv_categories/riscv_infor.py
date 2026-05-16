from rtg.rv_categories.riscv_classes import CLASS_OF_TYPE
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.settings import RISCV_32_INS

riscv32_classes: dict[str, type[BaseIntegerIns | BaseVectorIns]] = {}


def class_of_instruction(
    instructions: list[str], instruction_class: type[BaseIntegerIns | BaseVectorIns]
) -> None:
    for cur_instruction in instructions:
        riscv32_classes[cur_instruction] = instruction_class


for ins_type, ins_list in RISCV_32_INS.items():
    ins_class = CLASS_OF_TYPE[ins_type]
    class_of_instruction(ins_list, ins_class)
