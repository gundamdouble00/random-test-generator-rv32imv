from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.types.pseudo_ins import PSEUDO_INS
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.settings import PROGRAM_INS, RISCV_32_TYPES


def count_type_ins(log_file: LogFile):
    for i in range(len(log_file.executed_ins)):
        cur_ins = log_file.executed_ins[i]  # cur_ins == ["auipc", "s9,", "0x528d1"]
        if cur_ins[0] in PSEUDO_INS.keys():
            log_file.executed_ins[i] = PSEUDO_INS[cur_ins[0]](log_file.executed_ins[i])
            cur_ins = log_file.executed_ins[i]

        ins_name: str = cur_ins[0]
        ins_type: RISCVTypes = RISCV_32_TYPES[ins_name]
        log_file.count_type[ins_type] += 1
        log_file.count_ins[ins_type][ins_name] += 1

    for type in RISCVTypes:
        if log_file.count_type[type] < PROGRAM_INS[type]:
            log_file.success = False
            break


def count_executed_ins(log_files: list[LogFile]):
    using_multithreading(log_files, count_type_ins)
