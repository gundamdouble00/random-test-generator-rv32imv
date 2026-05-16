from coverage_analyzer.analyzer.types.log_file import LogFile

LOG_FILES_PATH: str = "./coverage_analyzer/log_files"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"


OUTPUTS: str = "./outputs"
BIN_FILES: str = OUTPUTS + "/bin_files"
SPIKE_INPUTS: str = OUTPUTS + "/spike_inputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"
COVERAGE_ANALYZER_LOG: str = "./coverage_analyzer/log_files"


def read_write_file(program: LogFile):
    body_flag: bool = False

    # e.g. log_name == "rv_assembly26.log"
    log_name: str = f"{FILE_NAME}{program.index}{LOG}"
    # e.g. input_file == "./outputs/spike_log_files/rv_assembly26.log"
    input_file: str = f"{SPIKE_LOG_FILES}/" + log_name
    # e.g. output_file == "./coverage_analyzer/log_files/rv_assembly26.log"
    output_file: str = f"{COVERAGE_ANALYZER_LOG}/" + log_name

    with open(input_file, "r") as in_file, open(output_file, "w") as out_file:
        for line in in_file:
            if program.body_addr in line:
                body_flag = True

            if (program.footer_addr in line) or (body_flag and "trap" in line):
                break

            if body_flag:
                _ = out_file.write(line)
                instruction: list[str] = []
                parts = line.strip().split(" ")
                for cur_part in parts:
                    if len(cur_part) != 0:
                        instruction.append(cur_part)
                program.executed_ins.append(instruction)

    print(f"Finished reading {log_name}")
