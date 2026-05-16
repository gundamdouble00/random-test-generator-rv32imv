import concurrent.futures
import os

import compile_execute
import delete_all_files
from coverage_analyzer.analyzer.utils.count_ins import count_riscv_ins
from coverage_analyzer.analyzer.utils.read_log_files import read_write_file
from coverage_analyzer.analyzer.utils.write_reports import writing_report

REPORTS_PATH: str = "./coverage_analyzer/reports"


def main():
    log_files = compile_execute.main()

    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        result_iterator = executor.map(read_write_file, log_files)
        _ = list(result_iterator)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        result_iterator = executor.map(count_riscv_ins, log_files)
        _ = list(result_iterator)

    delete_all_files.execute_deletion(REPORTS_PATH)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        result_iterator = executor.map(writing_report, log_files)
        _ = list(result_iterator)


if __name__ == "__main__":
    main()
