import random
from typing import final

from rtg.rv_categories.registers import ACTIVE_REG
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.v_extension.base_vector import IntegerArithmeticIns

vector_narrowing_integer_right_shift: tuple[str, ...] = ("vnsrl", "vnsra")
vector_integer_extension: tuple[str, ...] = ("vzext", "vsext")
V32_REG: int = 32


@final
class VectorOPIVV(IntegerArithmeticIns):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[VectorOPIVV.__name__]

        step: int = max(1, int(self.lmul))
        start: int = 0 if (not self.mask) else step

        if self.name.startswith(vector_narrowing_integer_right_shift):
            self._narrowing_integer_right_shift()
            self.src1 = f"v{random.randrange(start, V32_REG, step)}"
            return

        self.des = f"v{random.randrange(start, V32_REG, step)}"
        self.src2 = f"v{random.randrange(start, V32_REG, step)}"
        self.src1 = f"v{random.randrange(start, V32_REG, step)}"

        if self.name.endswith("m"):
            self.mask = True


@final
class VectorOPIVX(IntegerArithmeticIns):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[VectorOPIVX.__name__]

        if self.name.startswith(vector_narrowing_integer_right_shift):
            self._narrowing_integer_right_shift()
            self.src1 = random.choice(ACTIVE_REG)
            return

        step: int = max(1, int(self.lmul))
        start: int = 0 if (not self.mask) else step

        self.des = f"v{random.randrange(start, V32_REG, step)}"
        self.src2 = f"v{random.randrange(start, V32_REG, step)}"
        self.src1 = random.choice(ACTIVE_REG)

        if self.name.endswith("m"):
            self.mask = True


@final
class VectorOPIVI(IntegerArithmeticIns):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[VectorOPIVI.__name__]

        step: int = max(1, int(self.lmul))
        start_num: int = -16
        end_num: int = 15

        start: int = 0 if (not self.mask) else step
        if self.name in {
            "vsll.vi",
            "vsrl.vi",
            "vsra.vi",
            "vnsrl.wi",
            "vnsra.wi",
        }:
            start_num, end_num = 0, 31

        if self.name.startswith(vector_narrowing_integer_right_shift):
            self._narrowing_integer_right_shift()
            self.src1 = f"{random.randint(start_num, end_num)}"
            return

        self.des = f"v{random.randrange(start, V32_REG, step)}"
        self.src2 = f"v{random.randrange(start, 32, step)}"
        self.src1 = str(random.randint(start_num, end_num))

        if self.name.endswith("m"):
            self.mask = True


@final
class VectorOPMVV(IntegerArithmeticIns):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[VectorOPMVV.__name__]

        if self.name.startswith("vw"):
            self._widening()
            return

        if self.name.startswith(vector_integer_extension):
            self._integer_extension()
            return

        self._integer_divide_multiply()


@final
class VectorOPMVX(IntegerArithmeticIns):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[VectorOPMVX.__name__]

        if self.name.startswith("vw"):
            self._widening()
            return

        if self.name.startswith(vector_integer_extension):
            self._integer_extension()
            return

        self._integer_divide_multiply()
