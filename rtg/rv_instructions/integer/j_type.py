import random
from typing import override

from rtg.rv_categories.registers import RETURN_ADDR
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns


class JTypeIns(BaseIntegerIns):
    """
    jal extra_func
    """

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[JTypeIns.__name__]

        self.des: str = f"x{RETURN_ADDR}"

    @override
    def generate(self) -> str:
        return f"{self.name} {self.des}, extra_func{random.randint(1, 2)}"
