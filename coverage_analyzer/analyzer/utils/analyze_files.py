from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading
from rtg.settings import PROGRAM_INS


def check_number_ins(file: LogFile):
    for type, want in PROGRAM_INS.items():
        if want == 0:
            continue

        if file.count_type[type] < want:
            file.success = False
            break


def check_programs(log_files: list[LogFile]):
    using_multithreading(log_files, check_number_ins)
