PSEUDO_INS: dict[str, str] = {
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
    "blez": "bge",  # blez rs, offset (bge x0, rs, offset)
    "bgez": "bge",  # bgez rs, offset (bge rs, x0, offset)
    "bltz": "blt",  # bltz rs, offset (blt rs, x0, offset)
    "bgtz": "blt",  # bgtz rs, offset (blt x0, rs, offset)
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
