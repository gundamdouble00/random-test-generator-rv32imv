import random

from rtg.program.program import Program
from rtg.rv_categories.riscv_infor import riscv32_classes
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.rv_instructions.v_extension.base_vector import ConfigurationSetting
from rtg.settings import PROGRAM_INS, PROGRAM_LEN, RISCV_32_INS


def generate_obj(
    name: str,
    index: int,
    lmul: float,
    sew: int,
) -> BaseIntegerIns | BaseVectorIns | None:
    riscv_class = riscv32_classes.get(name)

    if not riscv_class:
        return None

    try:
        if issubclass(riscv_class, BaseIntegerIns):
            riscv_obj = riscv_class(name, index)
        else:
            riscv_obj = riscv_class(name, index, lmul, sew)
    except ValueError:
        return None

    return riscv_obj


def choose_random_ins(type: str, number: int) -> list[str]:
    return [random.choice(RISCV_32_INS[type]) for _ in range(number)]


def add_new_instructions(
    chosen_ins: list[str],
    sew_flag: int,
    lmul_flag: float,
    body_program: list[BaseIntegerIns | BaseVectorIns],
) -> tuple[int, float]:
    for ins in chosen_ins:
        riscv_obj = generate_obj(ins, len(body_program), lmul_flag, sew_flag)
        if riscv_obj is not None:
            body_program.append(riscv_obj)
            if isinstance(riscv_obj, ConfigurationSetting):
                sew_flag = riscv_obj.sew
                lmul_flag = riscv_obj.lmul
    return (sew_flag, lmul_flag)


def generate_random_program(_: int):
    asm_program = Program()
    chosen_ins: list[str] = []

    for key, val in PROGRAM_INS.items():
        # PROGRAM_INS[RISCVTypes.I_OP_R (key)] = 12 (val)
        # PROGRAM_INS[RISCVTypes.V_OPIVV (key)] = 14 (val)
        chosen_ins.extend(choose_random_ins(key, val))

    random.shuffle(chosen_ins)

    # Create instructions
    sew_flag: int = 32
    lmul_flag: float = 8.0
    sew_flag, lmul_flag = add_new_instructions(
        chosen_ins, sew_flag, lmul_flag, asm_program.body
    )

    asm_program.update_numbers_type()

    while len(asm_program.body) < PROGRAM_LEN:
        # PROGRAM_INS[RISCVTypes.I_OP_R] = 12 -> key == "I_OP_R" && val == 12
        chosen_ins = []
        for key, number in asm_program.count_type.items():
            if number >= PROGRAM_INS[RISCVTypes(key)]:
                continue

            missing_num: int = PROGRAM_INS[RISCVTypes(key)] - number
            chosen_ins.extend(choose_random_ins(key, missing_num))

        original_body_len: int = len(asm_program.body)
        sew_flag, lmul_flag = add_new_instructions(
            chosen_ins, sew_flag, lmul_flag, asm_program.body
        )

        if original_body_len == len(asm_program.body):
            cfg_setting = ConfigurationSetting(
                random.choice(["vsetvl", "vsetivl", "vsetivli"]),
                len(asm_program.body),
                lmul_flag,
                sew_flag,
            )
            asm_program.body.append(cfg_setting)
            lmul_flag = cfg_setting.lmul
            sew_flag = cfg_setting.sew

    return asm_program
