import random
from typing import override

from rtg.rv_categories.registers import BASE_MEM_ADDR
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_all_regs
from rtg.settings import WORD_MEMORY


class STypeIns(BaseIntegerIns):
    """sb rs2, offset(rs1)"""

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[STypeIns.__name__]

        self.src1: str = f"x{BASE_MEM_ADDR}"
        self.src2: str = rand_all_regs()
        num: int = WORD_MEMORY // 2
        while num % 4 != 0:
            num -= 1
        step: int = 4
        if self.name == "sb":
            step = 1
        elif self.name == "sh":
            step = 2

        self.imm: str = f"{random.randrange(-num, num, step)}"

    @override
    def generate(self) -> str:
        # name rs2, offset(rs1)
        return f"{self.name} {self.src2}, {self.imm}({self.src1})"
