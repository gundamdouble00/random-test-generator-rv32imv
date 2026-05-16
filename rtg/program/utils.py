import random

from rtg.rv_categories.registers import (
    ACTIVE_REG,
    EXTRA_FUNC1_LABEL,
    EXTRA_FUNC2_LABEL,
    MEM_REG,
    RETURN_ADDR,
    VECTOR_STRIDED,
    VECTOR_VSETVL,
    WORD_DATA_LABEL,
)
from rtg.settings import HAS_VECTOR, WORD_MEMORY

b_ins: list[str] = [
    "beq",
    "bne",
    "blt",
    "bge",
    "bltu",
    "bgeu",
]

DATA_SEGMENT: str = ".data"
ALIGN_4: str = "\t.align 4"

TEXT_SEGMENT: str = ".text"
GLOBL: str = ".globl main"
MAIN_LABEL: str = "main:"
HEADER_LABEL: str = "header:"


gef_counter: int = 0  # gen_extra_func's counter


def generate_extra_func() -> list[str]:
    global gef_counter

    gef_counter += 1
    addr_register: str = f"x{RETURN_ADDR}"
    branch_ins: str = random.choice(b_ins)
    extra_func: list[str] = [f"extra_func{gef_counter % 2 + 1}:"]

    if branch_ins == "beq":
        extra_func.append(f"\tjalr x0, 0({addr_register})")
        return extra_func

    reg1: str = random.choice(ACTIVE_REG[1:])
    while reg1 == addr_register:
        reg1 = random.choice(ACTIVE_REG[1:])

    reg2: str = random.choice(ACTIVE_REG[1:])
    while reg2 in {addr_register, reg1}:
        reg2 = random.choice(ACTIVE_REG[1:])

    imm1: int = random.randint(0, 13)
    imm2: int = random.randint(14, 26)
    if branch_ins in {"bgeu", "bge"}:
        imm1, imm2 = imm2, imm1

    extra_func.append(f"\taddi {reg1}, x0, {imm1}")
    extra_func.append(f"\taddi {reg2}, x0, {imm2}")
    extra_func.append(f"\tloop{gef_counter}:")
    imm: int = -1 if (branch_ins in {"bgeu", "bge"}) else 1
    extra_func.append(f"\t\taddi {reg1}, {reg1}, {imm}")
    extra_func.append(f"\t\t{branch_ins} {reg1}, {reg2}, loop{gef_counter}")
    extra_func.append(f"\tjalr x0, 0({addr_register})")

    return extra_func


def get_base_address(region: str) -> list[str]:
    header_base_address: list[str] = []
    lui: str = f"\tlui {MEM_REG[region]}, %hi({region})"
    addi: str = f"\taddi {MEM_REG[region]}, {MEM_REG[region]}, %lo({region})"

    header_base_address.append(lui)
    header_base_address.append(addi)
    return header_base_address


def generate_header() -> list[str]:
    """
    .text\n
    .globl main\n
    main:\n
    header:\n
        addi x0, x0, 2047\n
        ...\n
        addi x31, x0, 1814\n

        lui x12, %hi(data2)\n
        addi x12, x12, %lo(data2)\n

        lui x14, %hi(extra_func1)\n
        addi x14, x14, %lo(extra_func1)\n
        lui x26, %hi(extra_func2)\n
        addi x26, x26, %lo(extra_func2)\n

        vsetvli x6, x1, e32, m8, tu, ma\n
        vmv.v.x v0, x12\n
        vmv.v.x v8, x14\n
        vmv.v.x v16, x26\n
        vmv.v.x v24, x18\n

        addi x18, x0, 208\n
        jal x0, body\n
    extra_func2:\n
        addi x8, x0, 1\n
        addi x24, x0, 19\n
        loop1:\n
            addi x8, x8, 1\n
            bltu x8, x24, loop1\n
        jalr x0, 0(x6)\n
    body:\n
    """
    program_header: list[str] = [TEXT_SEGMENT, GLOBL, MAIN_LABEL, HEADER_LABEL]
    if HAS_VECTOR:
        program_header.append("\t# Has Vector\n")

    for register in ACTIVE_REG:
        imm: int = random.randint(a=-2048, b=2047)
        program_header.append(f"\taddi {register}, x0, {imm}")

    program_header.extend(get_base_address(WORD_DATA_LABEL))
    program_header.extend(get_base_address(EXTRA_FUNC1_LABEL))
    program_header.extend(get_base_address(EXTRA_FUNC2_LABEL))

    if HAS_VECTOR:
        program_header.append(f"\taddi x{VECTOR_VSETVL}, x0, 208")
        program_header.append(
            f"\tvsetvli {random.choice(ACTIVE_REG[1:])}, x1, e32, m8, tu, ma"
        )
        if VECTOR_STRIDED != -1:
            program_header.append(
                f"\taddi x{VECTOR_STRIDED}, x0, {random.randrange(-120, 121, 4)}"
            )

        for i in range(0, 32, 8):
            program_header.append(f"\tvmv.v.x v{i}, x{random.randint(0, 31)}")

    program_header.append("\tjal x0, body")
    program_header.extend(generate_extra_func())
    program_header.append("body:")

    return program_header


def generate_footer() -> list[str]:
    program_footer: list[str] = ["footer:", "\tjal x0, end"]
    program_footer.extend(generate_extra_func())
    program_footer.append("end:")
    program_footer.append("\tadd x0, x0, x0")

    return program_footer


def generate_data_segment():
    """
    .data\n
        data1: .word 0x66959435, 0xfedc4717, ...\n
        data2: .word -0xce0dd128, 0x8e848b09, ...\n
    """
    data1: list[str] = []
    data2: list[str] = []
    start, end = -(2**32), 2**32 - 1
    mem_region: list[str] = [DATA_SEGMENT]

    for _ in range(WORD_MEMORY // 2):
        data1.append(hex(random.randint(start, end)))
        data2.append(hex(random.randint(start, end)))

    print(f"Length of data1: {len(data1)}")
    print(f"Length of data2: {len(data2)}")

    first_region: str = "\tdata1: .word " + ", ".join(data1)
    second_region: str = "\tdata2: .word " + ", ".join(data2)
    mem_region.append(first_region)
    mem_region.append(second_region)

    return mem_region
