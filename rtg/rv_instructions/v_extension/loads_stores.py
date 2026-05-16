import random
from typing import final, override

from rtg.rv_categories.registers import VECTOR_STRIDED
from rtg.rv_categories.riscv_types import TYPE_OF_INS
from rtg.rv_instructions.utils.get_eew import get_eew
from rtg.rv_instructions.v_extension.base_vector import LoadsStores


@final
class UnitStride(LoadsStores):
    """
    # vd destination, rs1 base address, vm is mask encoding (v0.t or <missing>)\n
    vle8.v vd, (rs1), vm # 8-bit unit-stride load\n
    vle16.v vd, (rs1), vm # 16-bit unit-stride load\n
    vle32.v vd, (rs1), vm # 32-bit unit-stride load\n

    # vs3 store data, rs1 base address, vm is mask encoding (v0.t or <missing>)\n
    vse8.v vs3, (rs1), vm # 8-bit unit-stride store\n
    vse16.v vs3, (rs1), vm # 16-bit unit-stride store\n
    vse32.v vs3, (rs1), vm # 32-bit unit-stride store\n

    # Load byte vector of length ceil(vl/8)\n
    vlm.v vd, (rs1)\n
    # Store byte vector of length ceil(vl/8)\n
    vsm.v vs3, (rs1)\n
    """

    def _vlm_vsm(self):
        vreg: str = f"v{random.randint(0, 31)}"
        if self.name == "vlm.v":
            self.des = vreg
        else:
            self.src3 = vreg

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[UnitStride.__name__]

        if self.name in {"vlm.v", "vsm.v"}:
            self._vlm_vsm()
        else:
            # vle8.v, vle16.v, vle32.v
            # vse8.v, vse16.v, vse32.v
            self._vl_vs_stride()

    @override
    def generate(self) -> str:
        suffix: str = (
            ", v0.t" if (self.mask and (not self.name.endswith("m.v"))) else ""
        )
        if self.name.startswith("vl"):
            return f"{self.name} {self.des}, ({self.src1}){suffix}"
        return f"{self.name} {self.src3}, ({self.src1}){suffix}"


@final
class Strided(LoadsStores):
    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        """
        # vd destination, rs1 base address, rs2 byte stride\n
        vlse8.v vd, (rs1), rs2, vm # 8-bit strided load\n
        vlse16.v vd, (rs1), rs2, vm # 16-bit strided load\n
        vlse32.v vd, (rs1), rs2, vm # 32-bit strided load\n

        # vs3 store data, rs1 base address, rs2 byte stride\n
        vsse8.v vs3, (rs1), rs2, vm # 8-bit strided store\n
        vsse16.v vs3, (rs1), rs2, vm # 16-bit strided store\n
        vsse32.v vs3, (rs1), rs2, vm # 32-bit strided store\n
        """
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[Strided.__name__]

        self._vl_vs_stride()
        self.src2 = f"x{VECTOR_STRIDED}"

    @override
    def generate(self) -> str:
        suffix: str = "" if (not self.mask) else ", v0.t"
        if self.is_loads:
            return f"{self.name} {self.des}, ({self.src1}), {self.src2}{suffix}"
        return f"{self.name} {self.src3}, ({self.src1}), {self.src2}{suffix}"


@final
class Indexed(LoadsStores):
    """
    # Vector indexed-unordered load instructions\n
    # vd destination, rs1 base address, vs2 byte offsets\n
    vluxei8.v vd, (rs1), vs2, vm # unordered 8-bit indexed load of SEW data\n
    vluxei16.v vd, (rs1), vs2, vm # unordered 16-bit indexed load of SEW data\n
    vluxei32.v vd, (rs1), vs2, vm # unordered 32-bit indexed load of SEW data\n

    # Vector indexed-ordered load instructions\n
    # vd destination, rs1 base address, vs2 byte offsets\n
    vloxei8.v vd, (rs1), vs2, vm # ordered 8-bit indexed load of SEW data\n
    vloxei16.v vd, (rs1), vs2, vm # ordered 16-bit indexed load of SEW data\n
    vloxei32.v vd, (rs1), vs2, vm # ordered 32-bit indexed load of SEW data\n

    # Vector indexed-unordered store instructions\n
    # vs3 store data, rs1 base address, vs2 byte offsets\n
    vsuxei8.v vs3, (rs1), vs2, vm # unordered 8-bit indexed store of SEW data\n
    vsuxei16.v vs3, (rs1), vs2, vm # unordered 16-bit indexed store of SEW data\n
    vsuxei32.v vs3, (rs1), vs2, vm # unordered 32-bit indexed store of SEW data\n

    # Vector indexed-ordered store instructions\n
    # vs3 store data, rs1 base address, vs2 byte offsets\n
    vsoxei8.v vs3, (rs1), vs2, vm # ordered 8-bit indexed store of SEW data\n
    vsoxei16.v vs3, (rs1), vs2, vm # ordered 16-bit indexed store of SEW data\n
    vsoxei32.v vs3, (rs1), vs2, vm # ordered 32-bit indexed store of SEW data\n
    """

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[Indexed.__name__]

        eew: int = get_eew(self.name)
        emul: float = (eew / self.sew) * self.lmul
        if emul > 8.0:
            raise ValueError("emul must be equal or smaller than 8.0")

        vreg_step: int = max(1, int(self.lmul))
        vreg_start: int = 0 if (not self.mask) else vreg_step

        src2_step: int = max(1, int(emul))
        src2_start: int = 0 if (not self.mask) else src2_step

        while True:
            vreg = random.randrange(vreg_start, 32, vreg_step)
            src2_reg = random.randrange(src2_start, 32, src2_step)
            if vreg == src2_reg:
                continue
            if ((vreg + vreg_step - 1) < src2_reg) or (
                (src2_reg + src2_step - 1) < vreg
            ):
                break

        if self.is_loads:
            self.des = f"v{vreg}"
        else:
            self.src3 = f"v{vreg}"
        self.src2 = f"v{src2_reg}"

    @override
    def generate(self) -> str:
        suffix = ", v0.t" if self.mask else ""
        if self.is_loads:
            return f"{self.name} {self.des}, ({self.src1}), {self.src2}{suffix}"
        else:
            return f"{self.name} {self.src3}, ({self.src1}), {self.src2}{suffix}"


@final
class FaultOnlyFirstLoads(LoadsStores):
    """
    # vd destination, rs1 base address, vm is mask encoding (v0.t or <missing>)\n
    vle8ff.v vd, (rs1), vm # 8-bit unit-stride fault-only-first load\n
    vle16ff.v vd, (rs1), vm # 16-bit unit-stride fault-only-first load\n
    vle32ff.v vd, (rs1), vm # 32-bit unit-stride fault-only-first load\n
    """

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index, lmul, sew)
        self.type = TYPE_OF_INS[FaultOnlyFirstLoads.__name__]

        self._vl_vs_stride()

    @override
    def generate(self) -> str:
        suffix: str = "" if (not self.mask) else ", v0.t"
        if self.is_loads:
            return f"{self.name} {self.des}, ({self.src1}){suffix}"
        return f"{self.name} {self.src3}, ({self.src1}){suffix}"
