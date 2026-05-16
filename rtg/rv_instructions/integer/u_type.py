import random
from typing import override

from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_active_regs


class UTypeIns(BaseIntegerIns):
    """
    lui/auipc rd, imm
    """

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[UTypeIns.__name__]

        step, end = 1, 1048575
        self.des: str = rand_active_regs()
        self.imm: str = str(random.randrange(0, stop=end, step=step))

    @override
    def generate(self) -> str:
        # lui/auipc rd, imm
        return f"{self.name} {self.des}, {self.imm}"
