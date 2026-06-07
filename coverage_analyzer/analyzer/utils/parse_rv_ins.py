import re
from typing import final, override

LOAD_INT: list[str] = ["lb", "lh", "lw", "lbu", "lhu"]


@final
class PartsInIns:
    __slots__: tuple[str, ...] = ("name", "des", "src1", "src2", "src3", "imm")

    def __init__(
        self,
        name: str = "",
        des: str = "",
        src1: str = "",
        src2: str = "",
        src3: str = "",
        imm: str = "",
    ) -> None:
        self.name: str = name
        self.des: str = des
        self.src1: str = src1
        self.src2: str = src2
        self.src3: str = src3
        self.imm: str = imm

    @override
    def __repr__(self) -> str:
        return f"name: {self.name}, des: {self.des}, src1: {self.src1}, src2: {self.src2}, src3: {self.src3}, imm: {self.imm}"


def delete_comma(ins_parts: list[str]):
    for i in range(len(ins_parts)):
        cur_len: int = len(ins_parts[i])
        if ins_parts[i][cur_len - 1] == ",":
            ins_parts[i] = ins_parts[i][: cur_len - 1]

    return ins_parts


def is_integer(string: str) -> bool:
    try:
        _ = int(string)
        return True
    except ValueError:
        return False


def parse_R_M_ins(ins_parts: list[str]):
    # ins_parts == ['add', 's2', 's8', 's8']
    r_parts = PartsInIns(
        name=ins_parts[0], des=ins_parts[1], src1=ins_parts[2], src2=ins_parts[3]
    )
    return r_parts


def parse_I_ins(ins_parts: list[str]):
    # ['andi', 'a6', 'zero', '-1158']
    # ['lw', 's11', '-680(s9)']
    # ['jalr', 'x1', 's4', '0']
    ins_name: str = ins_parts[0]
    i_parts = PartsInIns(name=ins_name, des=ins_parts[1])
    if ins_name in LOAD_INT:
        address: list[str] = re.split(
            r"[()]", ins_parts[2]
        )  # address = ["-680", "s9", ""]
        i_parts.src1 = address[1]
        i_parts.imm = address[0]
    else:
        i_parts.src1 = ins_parts[2]
        i_parts.imm = ins_parts[3]

    return i_parts


def parse_S_ins(ins_parts: list[str]):
    # ['sw', 's0', '1156(s9)']
    ins_name: str = ins_parts[0]
    address: list[str] = re.split(r"[()]", ins_parts[2])  # address = ["1156", "s9", ""]
    s_parts = PartsInIns(
        name=ins_name, src3=ins_parts[1], src1=address[1], imm=address[0]
    )
    return s_parts


def parse_U_ins(ins_parts: list[str]):
    # ['auipc', 's1', '0x760a']
    # ['lui', 's8', '0x24583']
    u_parts = PartsInIns(name=ins_parts[0], des=ins_parts[1], imm=ins_parts[2])
    return u_parts


def parse_B_ins(ins_parts: list[str]):
    # ['bge', 'a4', 'ra', 'pc', '+', '16']
    b_parts = PartsInIns(name=ins_parts[0], src1=ins_parts[1], src2=ins_parts[2])
    return b_parts


def parse_J_ins(ins_parts: list[str]):
    # ['jal', 'x1', 't1']
    j_parts = PartsInIns(name=ins_parts[0], des=ins_parts[1])
    return j_parts


def parse_V_3_operands(ins_parts: list[str]):
    # vop.vv vd, vs2, vs1, vm
    # vop.vx vd, vs2, rs1, vm
    # vop.vi vd, vs2, imm, vm
    vector_3_opr = PartsInIns(name=ins_parts[0], des=ins_parts[1], src2=ins_parts[2])
    if not is_integer(ins_parts[3]):
        vector_3_opr.src1 = ins_parts[3]
    else:
        vector_3_opr.imm = ins_parts[3]

    return vector_3_opr


def parse_V_2_operands(ins_parts: list[str]):
    # vzext.vf2 vd, vs2, vm
    # vmv.v.v vd, vs1
    vector_2_opr = PartsInIns(name=ins_parts[0], des=ins_parts[1])
    if not is_integer(ins_parts[2]):
        vector_2_opr.src2 = ins_parts[2]
    else:
        vector_2_opr.imm = ins_parts[2]

    return vector_2_opr


def parse_unit_stride(ins_parts: list[str]):
    # ['vle16.v', 'v16', '(s9)']
    # ['vsm.v', 'vs3', '(rs1)']
    ins_name = ins_parts[0]
    unit_stride = PartsInIns(name=ins_name)
    if ins_name.startswith(("vle", "vlm")):
        unit_stride.des = ins_parts[1]
    else:
        unit_stride.src3 = ins_parts[1]

    base_addr = re.split(r"[()]", ins_parts[2])[1]  # ['', 's8', '']
    unit_stride.src1 = base_addr
    return unit_stride


def parse_strided_indexed(ins_parts: list[str]):
    # vlse8.v vd, (rs1), rs2, vm
    # vluxei8.v vd, (rs1), vs2, vm
    ins_name = ins_parts[0]
    strided_indexed = PartsInIns(name=ins_name)
    if ins_name.startswith(("vls", "vlu", "vlo")):
        strided_indexed.des = ins_parts[1]
    else:
        strided_indexed.src3 = ins_parts[1]

    base_addr = re.split(r"[()]", ins_parts[2])[1]  # ['', 's8', '']
    strided_indexed.src1 = base_addr
    strided_indexed.src2 = ins_parts[3]
    return strided_indexed


def parse_cfg_vector(ins_parts: list[str]):
    cfg_vector = PartsInIns(name=ins_parts[0], des=ins_parts[1])
    if is_integer(ins_parts[2]):
        cfg_vector.imm = ins_parts[2]
    else:
        cfg_vector.src1 = ins_parts[2]

    return cfg_vector
