import random
from typing import override

from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_active_regs, rand_all_regs


class RTypeIns(BaseIntegerIns):
    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[RTypeIns.__name__]

        self.des: str = rand_active_regs()
        first_src, second_src = rand_active_regs(), rand_all_regs()
        if random.random() >= 0.5:
            first_src, second_src = second_src, first_src
        self.src1: str = first_src
        self.src2: str = second_src

    @override
    def generate(self) -> str:
        # instruction rd, rs1, rs2
        return f"{self.name} {self.des}, {self.src1}, {self.src2}"
