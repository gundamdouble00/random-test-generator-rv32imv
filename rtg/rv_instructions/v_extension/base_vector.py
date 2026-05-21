import math
import random
from typing import override

from rtg.rv_categories.registers import ACTIVE_REG, BASE_MEM_ADDR, VECTOR_VSETVL
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.base_instruction import BaseVectorIns
from rtg.rv_instructions.utils.get_eew import get_eew

v_sew: list[int] = [8, 16, 32]
v_lmul: list[float] = [1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8]
v_tail: list[str] = ["ta", "tu"]
v_mask: list[str] = ["ma", "mu"]

LMUL_STRING = {
    1 / 8: "mf8",
    1 / 4: "mf4",
    1 / 2: "mf2",
    1: "m1",
    2: "m2",
    4: "m4",
    8: "m8",
}

V32_REG: int = 32
des_src1_src2 = [
    "vmacc.vv",
    "vmacc.vx",
    "vnmsac.vv",
    "vnmsac.vx",
    "vmadd.vv",
    "vmadd.vx",
    "vnmsub.vv",
    "vnmsub.vx",
    "vwmaccu.vv",
    "vwmaccu.vx",
    "vwmacc.vv",
    "vwmacc.vx",
    "vwmaccsu.vv",
    "vwmaccsu.vx",
    "vwmaccus.vx",
]
des_src2 = [
    "vzext.vf2",
    "vsext.vf2",
    "vzext.vf4",
    "vsext.vf4",
    "vzext.vf8",
    "vsext.vf8",
]
v0 = [
    "vmerge.vvm",
    "vmerge.vxm",
    "vmerge.vim",
    "vadc.vvm",
    "vadc.vxm",
    "vadc.vim",
    "vmadc.vvm",
    "vmadc.vxm",
    "vmadc.vim",
    "vmadc.vv",
    "vmadc.vx",
    "vmadc.vi",
    "vsbc.vvm",
    "vsbc.vxm",
    "vmsbc.vvm",
    "vmsbc.vxm",
    "vmsbc.vv",
    "vmsbc.vx",
]


class ConfigurationSetting(BaseVectorIns):
    """
    # vsetvl rd, rs1, rs2\n
    vsetvl t0, a3, x0\t (rd = new vl, rs1 = AVL, rs2 = new vtype value)\n

    # vsetvli rd, rs1, vtypei\n
    vsetvli t0, a3, e32, m1, ta, ma\t (rd = new vl, rs1 = AVL, vtypei = new vtype setting)\n

    # vsetivli rd, uimm, vtypei\n
    vsetivli t0, 12, e32, m1, ta, ma\t (rd = new vl, uimm = AVL, vtypei = new vtype setting)\n
    """

    __slots__: tuple[str, ...] = ("vma", "vta")

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type: str = TYPE_OF_INS[ConfigurationSetting.__name__]

        self.vta: str = ""  # Vector tail agnostic
        self.vma: str = ""  # Vector mask agnostic
        self.des: str = random.choice(ACTIVE_REG[1:])
        self.src1: str = ""

        if name in {"vsetvl", "vsetvli"}:
            self.src1 = random.choice(ACTIVE_REG[1:])
        else:
            # vsetivli
            self.src1 = f"{random.randint(1, 31)}"

        if self.name == "vsetvl":
            self.src2: str = f"x{VECTOR_VSETVL}"
            self.lmul: float = 1.0
            self.sew: int = 32
            self.vta = "tu"
            self.vma = "mu"
            return

        # LMUL >= SEW/ELEN
        while True:
            self.sew = random.choice(v_sew)
            self.lmul = random.choice(v_lmul)
            if self.lmul * 32 >= float(self.sew):
                break
        self.vta = random.choice(v_tail)
        self.vma = random.choice(v_mask)

    @override
    def generate(self) -> str:
        prefix: str = f"{self.name} {self.des}, {self.src1}, "
        if self.name == "vsetvl":
            return prefix + self.src2

        vtype = f"e{self.sew}, {LMUL_STRING[self.lmul]}, {self.vta}, {self.vma}"
        return prefix + vtype


class LoadsStores(BaseVectorIns):
    __slots__: tuple[str, ...] = ("src3", "mask", "is_loads")

    def _vl_vs_stride(self):
        eew = get_eew(self.name)
        emul = self.lmul * (eew / self.sew)
        if emul > 8.0:
            raise ValueError("emul must be equal or smaller than 8")

        step: int = max(1, int(emul))
        start: int = 0 if (not self.mask) else step
        v_reg = f"v{random.randrange(start=start, stop=32, step=step)}"
        if self.is_loads:
            self.des: str = v_reg
        else:
            self.src3 = v_reg

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        if lmul < (sew / 32):
            raise ValueError("lmul must be smaller than sew/elen (elen = 32)")

        super().__init__(name, index, lmul, sew)

        self.src3: str = ""
        self.src1: str = f"x{BASE_MEM_ADDR}"
        self.sew: int = sew
        self.lmul: float = lmul
        self.mask: bool = random.choice([True, False])
        self.is_loads: bool = True if (self.name.startswith("vl")) else False

    @override
    def generate(self) -> str:
        return ""


class IntegerArithmeticIns(BaseVectorIns):
    __slots__: tuple[str, ...] = ("mask",)

    def _integer_extension(self):
        vf: int = int(self.name[-1])
        eew = self.sew / vf
        emul = self.lmul / vf

        if eew < 8.0:
            raise ValueError("eew must be equal or bigger than 8")
        if emul < (1 / 8):
            raise ValueError("emul must be equal or bigger than 1/8")

        LMUL: int = max(1, int(self.lmul))
        EMUL: int = max(1, int(emul))
        while True:
            des_reg = random.randrange(LMUL, V32_REG, LMUL)
            src2_reg = random.randrange(EMUL, V32_REG, EMUL)

            if (des_reg + LMUL - 1 < src2_reg) or (src2_reg + EMUL - 1) < des_reg:
                break

        self.des: str = f"v{des_reg}"
        self.src2: str = f"v{src2_reg}"

    def _integer_divide_multiply(self):
        step: int = max(1, int(self.lmul))
        des_reg: int = random.randrange(step, V32_REG, step)
        src2_reg: int = random.randrange(step, V32_REG, step)

        self.des = f"v{des_reg}"
        self.src2 = f"v{src2_reg}"

        if self.name.endswith(".vv"):
            src1_reg: int = random.randrange(step, V32_REG, step)
            self.src1: str = f"v{src1_reg}"
        else:
            self.src1 = random.choice(ACTIVE_REG)

    def _widening(self):
        if int(self.lmul == 8) or self.sew == 32:
            raise ValueError(
                "lmul cannot be 8 and sew cannot be 32 (widening instruction)"
            )

        src_step = max(1, math.ceil(self.lmul))
        des_step = max(1, math.ceil(self.lmul * 2))
        des_start = des_step if self.mask else 0
        while True:
            des_reg = random.randrange(des_start, 32, des_step)
            curr_src2_step = (
                des_step if self.name.endswith((".wv", ".wx")) else src_step
            )
            src2_reg = random.randrange(0, 32, curr_src2_step)
            if (src2_reg + curr_src2_step - 1) < des_reg or (
                des_reg + des_step - 1
            ) < src2_reg:
                break

        if self.name.endswith("v"):
            while True:
                src1_reg = random.randrange(0, 32, src_step)
                if (src1_reg + src_step - 1) < des_reg or (
                    des_reg + des_step - 1
                ) < src1_reg:
                    break
            self.src1 = f"v{src1_reg}"
        else:
            self.src1 = random.choice(ACTIVE_REG)

        self.des = f"v{des_reg}"
        self.src2 = f"v{src2_reg}"

    def _narrowing_integer_right_shift(self):
        if self.sew == 32 or self.lmul > 4.0:
            raise ValueError("sew must be 8 or 16, and lmul*2 must be <= 8")

        des_step = max(1, math.ceil(self.lmul))
        src2_step = max(1, math.ceil(self.lmul * 2))

        des_start = des_step if self.mask else 0

        while True:
            src2_reg = random.randrange(0, 32, src2_step)
            des_reg = random.randrange(des_start, 32, des_step)

            if des_reg == src2_reg:
                break

            if (des_reg + des_step - 1) < src2_reg or (
                src2_reg + src2_step - 1
            ) < des_reg:
                break

        self.des = f"v{des_reg}"
        self.src2 = f"v{src2_reg}"

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        if lmul < (sew / 32):
            raise ValueError("lmul must be equal or bigger than sew/elen (elen = 32)")

        super().__init__(name, index, lmul, sew)

        self.sew: int = sew
        self.lmul: float = lmul
        self.mask: bool = random.choice([True, False])
        if self.name in v0:
            self.mask = True if self.name.endswith("m") else False

    @override
    def generate(self) -> str:
        # e.g. vmv.v.x v26, x14
        if self.name.startswith("vmv"):
            return f"{self.name} {self.des}, {self.src1}"

        ins: str = ""
        if self.mask:
            ins = ", v0" if self.name.endswith("m") else ", v0.t"

        if self.name in des_src1_src2:
            return f"{self.name} {self.des}, {self.src1}, {self.src2}" + ins

        if self.name in des_src2:
            return f"{self.name} {self.des}, {self.src2}" + ins

        return f"{self.name} {self.des}, {self.src2}, {self.src1}" + ins
