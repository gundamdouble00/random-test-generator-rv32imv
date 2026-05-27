from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading

LOG_FILES_PATH: str = "./coverage_analyzer/log_files"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"


OUTPUTS: str = "./outputs"
BIN_FILES: str = OUTPUTS + "/bin_files"
SPIKE_INPUTS: str = OUTPUTS + "/spike_inputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"
COVERAGE_ANALYZER_LOG: str = "./coverage_analyzer/log_files"


def read_file(program: LogFile):
    log_file: str = (
        f"{SPIKE_LOG_FILES}/" + f"{FILE_NAME}{program.index}{LOG}"
    )  # "./outputs/spike_log_files/rv_assembly26.log"

    with open(log_file, "r") as file:
        for log_record in file:
            # e.g. log_record:
            # core   0: 0x12000478 (0x019d8457) vadd.vv v8, v25, v27, v0.t
            # core   0: 0x12000298 (0x01e20eb3) add     t4, tp, t5
            # core   0: >>>>  body
            log_fields: list[str] = log_record.split()
            if log_fields[2] == ">>>>":
                continue

            if log_fields[2] == "exception":
                break

            address: int = int(log_fields[2], 16)
            if program.body_addr <= address < program.footer_addr:
                program.executed_ins.append(log_fields[4:])


def find_body_footer_address() -> tuple[int, int]:
    log_name: str = f"{FILE_NAME}0{LOG}"  # "rv_assembly0.log"
    input_file: str = (
        f"{SPIKE_LOG_FILES}/" + log_name
    )  # "./outputs/spike_log_files/rv_assembly0.log"
    body_flag, body_addr = 0, -1
    footer_flag, footer_addr = 0, -1

    with open(input_file, "r") as log_file:
        for log_record in log_file:
            log_fields: list[str] = log_record.split()
            num_fields: int = len(log_fields)
            if log_fields[num_fields - 1] == "body":
                body_flag += 1
                continue

            if body_flag == 1:
                body_addr = int(log_fields[2], 16)
                body_flag += 2026
                continue

            if log_fields[num_fields - 1] == "footer":
                footer_flag += 1
                continue

            if footer_flag == 1:
                footer_addr = int(log_fields[2], 16)
                footer_flag += 2026
                break

    return (body_addr, footer_addr)


def get_executed_ins(log_files: list[LogFile]):
    using_multithreading(log_files, read_file)
