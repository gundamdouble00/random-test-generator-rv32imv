import json
from collections import defaultdict

from coverage_analyzer.analyzer.types.log_file import LogFile
from rtg.settings import PROGRAM_INS, RISCV_32_INS

TEMP_DATA_FILE: str = "./coverage_analyzer/analyzer/temp_data.json"


def save_to_json_file(log_files: list[LogFile]):
    riscv32_ins: dict[int, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    coverage_percent: dict[int, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for file in log_files:
        for type in PROGRAM_INS.keys():
            riscv32_ins[file.index + 1] = riscv32_ins[file.index]
            for ins, num in file.count_ins[type].items():
                riscv32_ins[file.index + 1][type][ins] += num
            coverage_percent[file.index + 1][type] = round(
                (len(riscv32_ins[file.index + 1][type]) / len(RISCV_32_INS[type]))
                * 100,
                2,
            )

    with open(TEMP_DATA_FILE, "w") as json_file:
        json.dump(coverage_percent, json_file)
