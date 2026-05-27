jr_jalr: set[str] = {"jr", "jalr"}
bgtz_blez: set[str] = {"bgtz", "blez"}

NATIVE_INS: dict[str, str] = {
    "nop": "addi",  # nop (addi x0, x0, 0)
    "li": "addi",  # li rd, imm (addi rd, x0, imm)
    "mv": "addi",  # mv rd, rs (addi rd, rs, 0)
    "not": "xori",  # not rd, rs (xor rd, rs, -1)
    "neg": "sub",  # neg rd, rs (sub rd, x0, rs)
    "seqz": "sltiu",  # seqz rd, rs (sltiu rd, rs, 1)
    "snez": "sltu",  # snez rd, rs (sltu rd, x0, rs)
    "sltz": "slt",  # sltz rd, rs (slt rd, rs, x0)
    "sgtz": "slt",  # sgtz rd, rs (slt rd, x0, rs)
    #
    "beqz": "beq",  # beqz rs, offset (beq rs, x0, offset)
    "bnez": "bne",  # bnez rs, offset (bne rs, x0, offset)
    "bgez": "bge",  # bgez rs, offset (bge rs, x0, offset)
    "bltz": "blt",  # bltz rs, offset (blt rs, x0, offset)
    "bgtz": "blt",  # bgtz rs, offset (blt x0, rs, offset)
    "blez": "bge",  # blez rs, offset (bge x0, rs, offset)
    #
    "bgt": "blt",  # bgt rs, rt, offset (blt rt, rs, offset)
    "ble": "bge",  # ble rs, rt, offset (bge rt, rs, offset)
    "bgtu": "bltu",  # bgtu rs, rt, offset (bltu rt, rs, offset)
    "bleu": "bgeu",  # bleu rs, rt, offset (bgeu rt, rs, offset)
    #
    "j": "jal",  # j offset (jal x0, offset)
    "jal": "jal",  # jal offset (jal x1, offset)
    "jr": "jalr",  # jr rs (jalr x0, rs, 0)
    "jalr": "jalr",  # jalr rs (jalr x1, rs, 0)
    "ret": "jalr",  # ret (jalr x0, x1, 0)
}


def compare_with_zero(ins_parts: list[str]) -> list[str]:
    pseudo_ins: str = ins_parts[0]
    rs: str = ins_parts[1]
    offset: str = ins_parts[2]
    native_ins: str = NATIVE_INS[pseudo_ins]
    if pseudo_ins in bgtz_blez:
        return [pseudo_ins, "x0,", rs, offset]
    return [native_ins, rs, "x0,", offset]


def compare_with_reg(ins_parts: list[str]) -> list[str]:
    pseudo_ins: str = ins_parts[0]
    native_ins: str = NATIVE_INS[pseudo_ins]
    rs: str = ins_parts[1]
    rt: str = ins_parts[2]
    offset: str = ins_parts[3]
    return [native_ins, rt, rs, offset]


def jump_ins(ins_parts: list[str]) -> list[str]:
    pseudo_ins: str = ins_parts[0]
    native_ins: str = NATIVE_INS[pseudo_ins]
    reg: str = ""
    if pseudo_ins == "ret":
        return ["jalr", "x0,", "x1,", "0"]

    if pseudo_ins in jr_jalr:
        rs: str = ins_parts[1]
        reg = "x0," if pseudo_ins == "jr" else "x1,"
        return [native_ins, reg, rs, "0"]

    offset: str = ins_parts[1]
    reg = "x0," if pseudo_ins == "j" else "x1,"
    return [native_ins, reg, offset]


def arithmetic_ins(ins_parts: list[str]) -> list[str]:
    pseudo_ins: str = ins_parts[0]
    native_ins: str = NATIVE_INS[pseudo_ins]
    if pseudo_ins == "nop":
        return ["addi", "x0,", "x0,", "0"]

    rd: str = ins_parts[1]
    if pseudo_ins == "li":
        imm: str = ins_parts[2]
        return [native_ins, rd, "x0,", imm]

    rs: str = ins_parts[2]
    match pseudo_ins:
        case "mv":
            return [native_ins, rd, rs, "0"]
        case "not":
            return [native_ins, rd, rs, "-1"]
        case "neg":
            return [native_ins, rd, "x0,", rs]
        case "seqz":
            return [native_ins, rd, rs, "1"]
        case "snez":
            return [native_ins, rd, "x0,", rs]
        case "sltz":
            return [native_ins, rd, rs, "x0"]
        case _:  # case "sgtz":
            return [native_ins, rd, "x0", rs]
