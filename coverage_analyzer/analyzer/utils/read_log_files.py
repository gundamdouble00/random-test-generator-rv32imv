import subprocess

from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.types.pseudo_ins import PSEUDO_INS
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.settings import RISCV_32_TYPES

FILE_NAME: str = "rv_assembly"
BINARY: str = ".elf"
LOG: str = ".log"


OUTPUTS: str = "./outputs"
BIN_FILES: str = OUTPUTS + "/bin_files"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"

BODY_LABEL: str = "<body>:"
FOOTER_LABEL: str = "<footer>:"


def read_file(spike_log: LogFile):
    log_file: str = (
        f"{SPIKE_LOG_FILES}/" + f"{FILE_NAME}{spike_log.index}{LOG}"
    )  # "./outputs/spike_log_files/rv_assembly26.log"

    with open(log_file, "r") as file:
        for log_record in file:
            # core   0: 0x12000478 (0x019d8457) vadd.vv v8, v25, v27, v0.t
            # core   0: 0x12000298 (0x01e20eb3) add     t4, tp, t5
            # core   0: >>>>  body
            # core   0: >>>>  label179
            # core   0: exception trap_illegal_instruction, epc 0x12000454
            log_fields: list[str] = log_record.split()
            if log_fields[2] == ">>>>":
                continue

            if log_fields[2] == "exception":
                break

            cur_ins: list[str] = log_fields[4:]
            if cur_ins[0] in PSEUDO_INS.keys():
                cur_ins = PSEUDO_INS[cur_ins[0]](cur_ins)

            address: int = int(log_fields[2], 16)
            if (spike_log.body_addr <= address < spike_log.footer_addr) and (
                address not in spike_log.address_flag
            ):
                spike_log.body_ins.append(cur_ins)
                spike_log.address_flag[address] = True
                ins_name: str = cur_ins[0]
                ins_type: RISCVTypes = RISCV_32_TYPES[ins_name]
                spike_log.count_type[ins_type] += 1
                spike_log.count_ins[ins_type][ins_name] += 1
            spike_log.executed_ins.append(cur_ins)


def find_body_footer_address() -> tuple[int, int]:
    file_name: str = f"{FILE_NAME}0{BINARY}"  # "rv_assembly0.elf"
    elf_file: str = (
        f"{BIN_FILES}/" + file_name
    )  # "./outputs/bin_files/rv_assembly0.elf"
    objdump_cmd: list[str] = ["riscv32-linux-objdump", "-d", f"{elf_file}"]
    result = subprocess.run(objdump_cmd, capture_output=True, text=True)
    body_addr: int = -1
    footer_addr: int = -1
    for line in result.stdout.splitlines():
        parts: list[str] = line.split()
        if len(parts) != 2:
            continue

        final_str: str = parts[len(parts) - 1]
        if final_str == BODY_LABEL:
            body_addr = int(parts[0], 16)
            continue
        if FOOTER_LABEL in line:
            footer_addr = int(parts[0], 16)
            break

    return (body_addr, footer_addr)


def get_executed_ins(log_files: list[LogFile]):
    using_multithreading(log_files, read_file)
