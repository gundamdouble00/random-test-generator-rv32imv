from pathlib import Path

from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.analyze_files import check_programs
from coverage_analyzer.analyzer.utils.read_log_files import (
    find_body_footer_address,
    get_executed_ins,
)
from coverage_analyzer.analyzer.utils.write_reports import generate_reports

REPORTS_PATH: str = "./coverage_analyzer/reports"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"
OUTPUTS: str = "./outputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"
COVERAGE_ANALYZER_LOG: str = "./coverage_analyzer/log_files"


def coverage_testing(log_files: list[LogFile]):
    for current_file in log_files:
        if len(current_file.body_ins) != 520:
            print(f"{current_file.index} ({len(current_file.body_ins)})")
            for ins in current_file.body_ins:
                print(ins)
            break


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

    generate_reports(log_files)

    # # # # TESTING # # # # # #
    # coverage_testing(log_files)
    # # # # # # # # # # # # # #

    failed: int = 0
    for file in log_files:
        if not file.success:
            failed += 1
            print(f"Program {file.index}: Failed")

    print(f"{failed} programs failed")


if __name__ == "__main__":
    main()
