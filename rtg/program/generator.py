import random

from rtg.program.program import Program
from rtg.rv_categories.riscv_infor import riscv32_classes
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.base_instruction import BaseIntegerIns, BaseVectorIns
from rtg.rv_instructions.v_extension.base_vector import ConfigurationSetting
from rtg.settings import (
    HAS_VECTOR,
    INSTRUCTIONS_PER_PATH,
    PROGRAM_INS,
    PROGRAM_LEN,
    RISCV_32_INS,
    settings,
    vsetvl_vlmul,
    vsetvl_vsew,
)

cfg_setting_ins: list[str] = ["vsetvli", "vsetivli"]
riscv32_types: list[str] = list(PROGRAM_INS.keys())


def generate_obj(current_type: str, current_index: int, lmul: float, sew: int):
    while True:
        current_ins = random.choice(RISCV_32_INS[current_type])
        riscv_class = riscv32_classes.get(current_ins)
        if riscv_class is None:
            continue

        try:
            if issubclass(riscv_class, BaseVectorIns):
                riscv_obj = riscv_class(current_ins, current_index, lmul, sew)
            else:
                riscv_obj = riscv_class(current_ins, current_index)

            break
        except ValueError:
            continue
    return riscv_obj


def only_integer(asm_program: Program, chosen_ins: list[str]):
    for type, number in PROGRAM_INS.items():
        random_ins = [random.choice(RISCV_32_INS[type]) for _ in range(number)]
        chosen_ins.extend(random_ins)

    for _ in range(2):
        random.shuffle(chosen_ins)
        for instruction in chosen_ins:
            riscv_class = riscv32_classes.get(instruction)
            if (riscv_class is not None) and issubclass(riscv_class, BaseIntegerIns):
                riscv_obj = riscv_class(instruction, len(asm_program.body))
                asm_program.body.append(riscv_obj)

    asm_program.body = asm_program.body[:PROGRAM_LEN]
    return asm_program


def generate_random_program(_: int):
    asm_program = Program()
    chosen_ins: list[str] = []

    if not HAS_VECTOR:
        return only_integer(asm_program, chosen_ins)

    # Has Vector Instructions
    sew, lmul = -1, -1.0
    for i in range(len(settings)):
        SETTING = settings[i]
        sew, lmul = SETTING[0], SETTING[1]
        cfg_ins: str = (
            "vsetvl"
            if (sew == vsetvl_vsew and lmul == vsetvl_vlmul)
            else (random.choice(cfg_setting_ins))
        )
        cfg_obj = ConfigurationSetting(cfg_ins, len(asm_program.body), lmul, sew)
        asm_program.count_type[cfg_obj.type] += 1
        riscv32_objects: list[BaseIntegerIns | BaseVectorIns] = []

        while len(riscv32_objects) < INSTRUCTIONS_PER_PATH - 1:
            missing_flag: bool = False
            for type, number in PROGRAM_INS.items():
                if number == 0.0:
                    continue

                if asm_program.count_type[type] < number:
                    missing_flag = True
                    break

            if not missing_flag:
                break

            current_type: str = random.choice(riscv32_types)
            if current_type == RISCVTypes.V_OPCFG:
                continue

            if (
                asm_program.count_type[current_type]
                < PROGRAM_INS[RISCVTypes(current_type)]
            ):
                current_index: int = len(asm_program.body) + len(riscv32_objects) + 1
                riscv_obj = generate_obj(current_type, current_index, lmul, sew)
                riscv32_objects.append(riscv_obj)
                asm_program.count_type[riscv_obj.type] += 1

        random.shuffle(riscv32_objects)
        asm_program.body.append(cfg_obj)
        asm_program.body.extend(riscv32_objects)

    missing_ins: list[BaseIntegerIns | BaseVectorIns] = []
    for type, number in PROGRAM_INS.items():
        if asm_program.count_type[type] < number:
            riscv32_objects = []
            missing_number: int = number - asm_program.count_type[type]
            while len(riscv32_objects) < missing_number:
                current_index = len(asm_program.body) + len(riscv32_objects) + 1
                riscv_obj = generate_obj(type, current_index, lmul, sew)
                riscv32_objects.append(riscv_obj)
                asm_program.count_type[riscv_obj.type] += 1

            missing_ins.extend(riscv32_objects)

    random.shuffle(missing_ins)
    asm_program.body.extend(missing_ins)

    while len(asm_program.body) < PROGRAM_LEN:
        current_type = random.choice(riscv32_types)
        if current_type == RISCVTypes.V_OPCFG:
            continue

        riscv_obj = generate_obj(current_type, len(asm_program.body), lmul, sew)
        asm_program.body.append(riscv_obj)
        asm_program.count_type[riscv_obj.type] += 1

    asm_program.body = asm_program.body[:PROGRAM_LEN]
    return asm_program
