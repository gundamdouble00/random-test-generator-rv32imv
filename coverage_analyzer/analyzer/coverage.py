from pathlib import Path

from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.read_log_files import (
    find_body_footer_address,
    get_executed_ins,
)

REPORTS_PATH: str = "./coverage_analyzer/reports"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"
OUTPUTS: str = "./outputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"
COVERAGE_ANALYZER_LOG: str = "./coverage_analyzer/log_files"


def main():
    num_log_files: int = 0
    for file_folder in Path(SPIKE_LOG_FILES).iterdir():
        if Path.is_file(file_folder):
            num_log_files += 1

    log_files = [LogFile(i) for i in range(num_log_files)]
    BODY_ADDR, FOOTER_ADDR = find_body_footer_address()
    for i in range(num_log_files):
        log_files[i].body_addr = BODY_ADDR
        log_files[i].footer_addr = FOOTER_ADDR

    get_executed_ins(log_files)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     result_iterator = executor.map(read_write_file, log_files)
    #     _ = list(result_iterator)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     result_iterator = executor.map(count_riscv_ins, log_files)
    #     _ = list(result_iterator)

    # delete_all_files.execute_deletion(REPORTS_PATH)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     result_iterator = executor.map(writing_report, log_files)
    #     _ = list(result_iterator)


if __name__ == "__main__":
    main()
