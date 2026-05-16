from typing import final

from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.settings import PROGRAM_INS, RISCV_32_INS


@final
class Program:
    __slots__: tuple[str, ...] = ("fitness", "count_ins", "count_type", "body", "label")

    def __init__(self) -> None:
        self.body: list[BaseIntegerIns | BaseVectorIns] = []
        self.count_ins: dict[str, dict[str, int]] = {}
        self.count_type: dict[str, int] = {}
        self.fitness: float = -1.00
        self.label: list[int] = []

    def __len__(self) -> int:
        return len(self.body)

    def update_numbers_type(self) -> None:
        """
        self.count_type = {
            "I_OP_R": 12,
            "I_OP_I": 12,
            ...
        }
        """
        for key, number in PROGRAM_INS.items():
            if number == 0:
                continue
            self.count_type[key] = 0

        for ins in self.body:
            self.count_type[ins.type] += 1

    def update_numbers_ins(self) -> None:
        """
        self.count_ins = {
            "I_OP_R": {
                "add": 12,
                "sub": 14,
                "and": 26,
                ...
            },
            "I_OP_I": {
                "addi": 12,
                "andi": 14,
                "xori": 26,
            },
            ...
        }
        """
        self.count_ins.clear()
        for key, number in PROGRAM_INS.items():
            if number == 0:
                continue
            self.count_ins[key] = {}

        for ins in self.body:
            if ins.name in self.count_ins[ins.type]:
                self.count_ins[ins.type][ins.name] += 1
            else:
                self.count_ins[ins.type][ins.name] = 1

    def to_assembly(self):
        assembly_program: list[str] = []
        for rv_ins in self.body:
            assembly_program.append(rv_ins.generate())
        return assembly_program
