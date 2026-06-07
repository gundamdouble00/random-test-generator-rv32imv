from collections import defaultdict
from pathlib import Path

from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.analyze_files import check_programs
from coverage_analyzer.analyzer.utils.read_log_files import (
    find_body_footer_address,
    get_executed_ins,
)
from coverage_analyzer.analyzer.utils.stress_cases import count_stress_cases
from coverage_analyzer.analyzer.utils.write_reports import generate_reports
from rtg.settings import PROGRAM_INS, RISCV_32_INS

REPORTS_PATH: str = "./coverage_analyzer/"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"
OUTPUTS: str = "./outputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"

SUMMARY_FILE: str = "summary.txt"


def main():
    num_log_files: int = 0
    for file_folder in Path(SPIKE_LOG_FILES).iterdir():
        if Path.is_file(file_folder):
            num_log_files += 1

    log_files: list[LogFile] = [LogFile(i) for i in range(num_log_files)]
    BODY_ADDR, FOOTER_ADDR = find_body_footer_address()
    for i in range(num_log_files):
        log_files[i].body_addr = BODY_ADDR
        log_files[i].footer_addr = FOOTER_ADDR

    get_executed_ins(log_files)

    check_programs(log_files)

    count_stress_cases(log_files)

    generate_reports(log_files)

    # Generate Summary Report

    failed: int = 0
    data_hazards: dict[str, int] = defaultdict(int)
    riscv32_ins: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for file in log_files:
        if not file.success:
            failed += 1

        for type in file.count_type.keys():
            for ins, num in file.count_ins[type].items():
                riscv32_ins[type][ins] += num

    summary_file_path = REPORTS_PATH + "/" + SUMMARY_FILE
    with open(summary_file_path, "w") as summary:
        _ = summary.write(f"Passed: {len(log_files) - failed} programs\n")
        _ = summary.write("\n")

        _ = summary.write("Coverage:\n")
        _ = summary.write("\tPercent:\n")
        for type in PROGRAM_INS.keys():
            coverage: float = len(riscv32_ins[type]) / len(RISCV_32_INS[type])
            _ = summary.write(f'\t\t- "{type}" instructions: {coverage * 100:.2f}%\n')

        _ = summary.write("\n")
        _ = summary.write("\tData Hazards:\n")
        data_hazards = log_files[0].data_hazards
        for file in log_files:
            for type, num in file.data_hazards.items():
                data_hazards[type] = min(data_hazards[type], num)
        for type, num in data_hazards.items():
            _ = summary.write(f"\t\t- {type}: {num}\n")

        _ = summary.write("\n")
        _ = summary.write("\tInstructions:\n")
        for type in PROGRAM_INS.keys():
            total: int = 0
            for num in riscv32_ins[type].values():
                total += num
            _ = summary.write(f"\t\t- {type}: {total} instructions\n")


if __name__ == "__main__":
    main()
