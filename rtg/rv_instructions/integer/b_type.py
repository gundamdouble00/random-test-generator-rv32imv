from typing import override

from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_all_regs


class BTypeIns(BaseIntegerIns):
    """
    "ins_name src1, src2, label"\n
    e.g.\n
    beq x12, x14, label2026
    """

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[BTypeIns.__name__]

        self.src1: str = rand_all_regs()
        self.src2: str = rand_all_regs()

    @override
    def generate(self) -> str:
        return f"{self.name} {self.src1}, {self.src2}, {self.label}"
