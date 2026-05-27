from coverage_analyzer.analyzer.types.log_file import LogFile
from coverage_analyzer.analyzer.utils.multithreading import using_multithreading
from delete_all_files import execute_deletion
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.settings import PROGRAM_INS

FILE_NAME: str = "program"
REPORTS_PATH: str = "./coverage_analyzer/reports"


def write_report(log_file: LogFile):
    result: str = ""
    file: str = f"{FILE_NAME}{log_file.index}.txt"
    file_path = REPORTS_PATH + "/" + file
    with open(file_path, "w") as f:
        _ = f.write(f"Program {log_file.index}\n")

        result = "Passed" if log_file.success else "Failed"
        _ = f.write(f"Resuls: {result}\n")

        _ = f.write("\n")
        _ = f.write("Instruction types in program:\n")
        for key, value in log_file.count_type.items():
            _ = f.write(
                f"\tType {key}: {value} (Want: {PROGRAM_INS[RISCVTypes(key)]})\n"
            )
            for name, value in log_file.count_ins[key].items():
                _ = f.write(f"\t\t- {name}: {value}\n")
            _ = f.write("\n")


def generate_reports(log_files: list[LogFile]):
    execute_deletion(REPORTS_PATH)
    using_multithreading(log_files, write_report)
