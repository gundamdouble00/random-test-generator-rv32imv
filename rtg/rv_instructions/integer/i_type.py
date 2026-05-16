import random
from typing import override

from rtg.rv_categories.registers import (
    BASE_MEM_ADDR,
    EXTRA_FUNC1,
    EXTRA_FUNC2,
    RETURN_ADDR,
    VECTOR_STRIDED,
)
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseIntegerIns
from rtg.rv_instructions.utils.random_regs import rand_active_regs, rand_all_regs
from rtg.settings import HAS_STRIDED, WORD_MEMORY


class ITypeIns(BaseIntegerIns):
    def _jalr_ins(self) -> None:
        """
        jalr des, imm(src1)\n\n
        e.g.\n
        func:\n
          jalr x0, 0(x12)\n
        body:\n
          lui x14, %hi(func)\n
          addi x14, x14, %lo(func)\n\n
          jalr x12, 0(x14)\n
        """
        self.des: str = f"x{RETURN_ADDR}"
        self.src1: str = f"x{random.choice([EXTRA_FUNC1, EXTRA_FUNC2])}"
        self.imm: str = "0"

    def _load_ins(self) -> None:
        """
        "lb/lbu/lh/lhu/lw des, imm(src1)"\n
        e.g. lb des, imm(src1)
        """
        num: int = WORD_MEMORY // 2
        while num % 4 != 0:
            num -= 1
        if self.name in {"lb", "lbu"}:
            offset = random.randrange(-num, num)
        elif self.name in {"lh", "lhu"}:
            offset = random.randrange(-num, num, 2)
        else:
            offset = random.randrange(-num, num, 4)

        self.src1 = f"x{BASE_MEM_ADDR}"
        self.imm = f"{offset}"

    def _alu_ins(self):
        """
        addi, andi, ori, xori, slti, sltiu, slli, srli, srai rd, rs1, imm
        """

        if (self.name == "add") and (random.random() < 0.26) and HAS_STRIDED:
            self.des, self.src1 = f"x{VECTOR_STRIDED}", "x0"
            num: int = WORD_MEMORY // 2
            while num % 4 != 0:
                num -= 1
            start: int = max(-120, -num)
            end: int = min(121, num)
            self.imm = str(random.randrange(start, end, 4))
            return

        start, end = -2048, 2047
        if self.name in {"slli", "srli", "srai"}:
            imm = random.randint(0, 31)
        else:
            imm = random.randint(start, end)

        self.src1 = rand_all_regs()
        self.imm = f"{imm}"

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)
        self.type: str = TYPE_OF_INS[ITypeIns.__name__]

        self.des = rand_active_regs()

        if self.name == "jalr":
            self._jalr_ins()
            return

        # lb, lbu, lh, lhu, lw
        if self.name.startswith("l"):
            self._load_ins()
            return

        # addi, andi, ori, xori, slti, sltiu
        # slli, srli, srai
        self._alu_ins()

    @override
    def generate(self) -> str:
        # ins_name des, imm(src1)
        if self.name.startswith(("l", "j")):
            return f"{self.name} {self.des}, {self.imm}({self.src1})"

        # ins_name des, src1, imm
        return f"{self.name} {self.des}, {self.src1}, {self.imm}"
