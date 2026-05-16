import random
from typing import final, override

from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_active_regs, rand_all_regs


@final
class MulDivIns(BaseIntegerIns):
    """
    mul rd, rs1, rs2\n
    mulh rd, rs1, rs2\n
    mulhu rd, rs1, rs2\n
    mulhsu rd, rs1, rs2\n
    div rd, rs1, rs2\n
    divu rd, rs1, rs2\n
    rem rd, rs1, rs2\n
    remu rd, rs1, rs2\n
    """

    def __init__(self, name: str, index: int):
        super().__init__(name, index)

        self.type: str = TYPE_OF_INS[MulDivIns.__name__]
        self.des: str = rand_active_regs()

        first_src, second_src = rand_active_regs(), rand_all_regs()
        if random.random() >= 0.5:
            first_src, second_src = second_src, first_src
        self.src1: str = first_src
        self.src2: str = second_src

    @override
    def generate(self) -> str:
        return f"{self.name} {self.des}, {self.src1}, {self.src2}"
