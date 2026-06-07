from collections import defaultdict

from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading
from coverage_analyzer.analyzer.utils.parse_rv_ins import (
    parse_B_ins,
    parse_cfg_vector,
    parse_I_ins,
    parse_J_ins,
    parse_R_M_ins,
    parse_S_ins,
    parse_strided_indexed,
    parse_U_ins,
    parse_unit_stride,
    parse_V_2_operands,
    parse_V_3_operands,
)
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.settings import RISCV_32_INS


def func_multiplexer(ins_name: str):
    if (
        ins_name in RISCV_32_INS[RISCVTypes.I_OP_R]
        or ins_name in RISCV_32_INS[RISCVTypes.M_OP_M]
    ):
        return parse_R_M_ins

    if ins_name in RISCV_32_INS[RISCVTypes.I_OP_I]:
        return parse_I_ins

    if ins_name in RISCV_32_INS[RISCVTypes.I_OP_S]:
        return parse_S_ins

    if ins_name in RISCV_32_INS[RISCVTypes.I_OP_U]:
        return parse_U_ins

    if ins_name in RISCV_32_INS[RISCVTypes.I_OP_B]:
        return parse_B_ins

    if ins_name in RISCV_32_INS[RISCVTypes.I_OP_J]:
        return parse_J_ins

    if ins_name in RISCV_32_INS[RISCVTypes.V_OPCFG]:
        return parse_cfg_vector

    if (
        ins_name in RISCV_32_INS[RISCVTypes.V_OP_UNIT_STRIDE]
        or ins_name in RISCV_32_INS[RISCVTypes.V_OP_FAULT_ONLY_FIRST_LOADS]
    ):
        return parse_unit_stride

    if (
        ins_name in RISCV_32_INS[RISCVTypes.V_OP_STRIDED]
        or ins_name in RISCV_32_INS[RISCVTypes.V_OP_INDEXED]
    ):
        return parse_strided_indexed

    if ins_name.startswith(("vmv", "vzext", "vsext")):
        return parse_V_2_operands

    return parse_V_3_operands


def read_after_write(des_reg: dict[str, int], cur_reg: str):
    if cur_reg == "":
        return 0
    return 1 if des_reg[cur_reg] != 0 else 0


def write_after_read(src_reg: dict[str, int], cur_reg: str):
    if cur_reg == "":
        return 0
    return 1 if src_reg[cur_reg] != 0 else 0


def write_after_write(des_reg: dict[str, int], cur_reg: str):
    if cur_reg == "":
        return 0
    return 1 if des_reg[cur_reg] != 0 else 0


def update_reg_dict(reg_dict: dict[str, int], key: str, value: int):
    if key == "":
        return
    reg_dict[key] += value


def verification_stress_cases(spike_log: LogFile):
    des_reg: dict[str, int] = defaultdict(int)
    src_reg: dict[str, int] = defaultdict(int)
    for i in range(len(spike_log.executed_ins)):
        cur_ins = spike_log.executed_ins[i]
        # print(cur_ins)
        ins_name: str = cur_ins[0]
        parse_func = func_multiplexer(ins_name)
        rv_obj = parse_func(cur_ins)
        # print(rv_obj.__repr__())

        spike_log.data_hazards["Read after Write"] += read_after_write(
            des_reg, rv_obj.src1
        )
        spike_log.data_hazards["Read after Write"] += read_after_write(
            des_reg, rv_obj.src2
        )
        spike_log.data_hazards["Read after Write"] += read_after_write(
            des_reg, rv_obj.src3
        )

        spike_log.data_hazards["Write after Read"] += write_after_read(
            src_reg, rv_obj.des
        )

        spike_log.data_hazards["Write after Write"] += write_after_write(
            des_reg, rv_obj.des
        )

        update_reg_dict(des_reg, rv_obj.des, 1)
        update_reg_dict(src_reg, rv_obj.src1, 1)
        update_reg_dict(src_reg, rv_obj.src2, 1)
        update_reg_dict(src_reg, rv_obj.src3, 1)

        if i > 6:
            cur_ins = spike_log.executed_ins[i - 6]
            ins_name = cur_ins[0]
            parse_func = func_multiplexer(ins_name)
            rv_obj = parse_func(cur_ins)
            update_reg_dict(des_reg, rv_obj.des, -1)
            update_reg_dict(src_reg, rv_obj.src1, -1)
            update_reg_dict(src_reg, rv_obj.src2, -1)
            update_reg_dict(src_reg, rv_obj.src3, -1)


def count_stress_cases(log_files: list[LogFile]):
    using_multithreading(log_files, verification_stress_cases)
