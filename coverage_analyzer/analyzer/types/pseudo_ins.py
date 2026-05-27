from coverage_analyzer.analyzer.utils.pseudo_to_native import (
    arithmetic_ins,
    compare_with_reg,
    compare_with_zero,
    jump_ins,
)

PSEUDO_INS = {
    "nop": arithmetic_ins,  # nop (addi x0, x0, 0)
    "li": arithmetic_ins,  # li rd, imm (addi rd, x0, imm)
    "mv": arithmetic_ins,  # mv rd, rs (addi rd, rs, 0)
    "not": arithmetic_ins,  # not rd, rs (xor rd, rs, -1)
    "neg": arithmetic_ins,  # neg rd, rs (sub rd, x0, rs)
    "seqz": arithmetic_ins,  # seqz rd, rs (sltiu rd, rs, 1)
    "snez": arithmetic_ins,  # snez rd, rs (sltu rd, x0, rs)
    "sltz": arithmetic_ins,  # sltz rd, rs (slt rd, rs, x0)
    "sgtz": arithmetic_ins,  # sgtz rd, rs (slt rd, x0, rs)
    #
    "beqz": compare_with_zero,  # beqz rs, offset (beq rs, x0, offset)
    "bnez": compare_with_zero,  # bnez rs, offset (bne rs, x0, offset)
    "bgez": compare_with_zero,  # bgez rs, offset (bge rs, x0, offset)
    "bltz": compare_with_zero,  # bltz rs, offset (blt rs, x0, offset)
    "bgtz": compare_with_zero,  # bgtz rs, offset (blt x0, rs, offset)
    "blez": compare_with_zero,  # blez rs, offset (bge x0, rs, offset)
    #
    "bgt": compare_with_reg,  # bgt rs, rt, offset (blt rt, rs, offset)
    "ble": compare_with_reg,  # ble rs, rt, offset (bge rt, rs, offset)
    "bgtu": compare_with_reg,  # bgtu rs, rt, offset (bltu rt, rs, offset)
    "bleu": compare_with_reg,  # bleu rs, rt, offset (bgeu rt, rs, offset)
    #
    "j": jump_ins,  # j offset (jal x0, offset)
    "jal": jump_ins,  # jal offset (jal x1, offset)
    "jr": jump_ins,  # jr rs (jalr x0, rs, 0)
    "jalr": jump_ins,  # jalr rs (jalr x1, rs, 0)
    "ret": jump_ins,  # ret (jalr x0, x1, 0)
}
