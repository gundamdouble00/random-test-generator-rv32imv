# from config import RISCV_32_RATE
from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.types.pseudo_ins import PSEUDO_INS

# from rtg.rtg_config import RISCV_32_INS


def count_riscv_ins(log_file: LogFile):
    for line in log_file.executed_ins:
        # line == ["core", "0:", "0x0001072c", "(0x528d1c97)", "auipc", "s9", "0x528d1"]
        # line == ["core", "0:", "0x00010730", "(0x034443b3)", "div", "t2", "s0", "s4"]
        # line == ["core", "0:", "0x00010788", "(0xc3cb0ca3)", "sb", "t3", "-967(s6)"]
        ins_name: str = line[4]
        current_addr: int = int(line[2], 16)
        if (
            current_addr < int(log_file.body_addr, 16)
            or int(log_file.footer_addr, 16) <= current_addr
        ):
            continue

        for key, ins_list in RISCV_32_INS.items():
            if RISCV_32_RATE[key] == 0:
                continue

            if ins_name in PSEUDO_INS:
                ins_name = PSEUDO_INS[ins_name]
            if ins_name in ins_list:
                log_file.count_type[key] += 1
                log_file.count_ins[key][ins_name] += 1
                break
