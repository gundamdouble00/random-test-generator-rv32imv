import bisect
import concurrent.futures
import itertools
import os
from pathlib import Path

from delete_all_files import execute_deletion
from rtg.program.program import Program
from rtg.program.utils import generate_data_segment, generate_footer, generate_header
from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.integer.b_type import BTypeIns
from rtg.settings import (
    DATA_ORIGIN,
    DATA_SIZE,
    HAS_VECTOR,
    PROGRAM_LEN,
    TEST_CASES,
    TEXT_ORIGIN,
    TEXT_SIZE,
)

BRANCH_STEP: int = min(PROGRAM_LEN // 3, 1023)


def write_to_file(
    individual: Program,
    header: list[str],
    footer: list[str],
    data_segment: list[str],
    index: int,
):
    with open(f"outputs/rtg_outputs/rv_assembly{index}.s", "w") as f:
        # Writing Data Segment
        for data in data_segment:
            _ = f.write(f"{data}\n")
        _ = f.write("\n")

        # Writing Header
        for instruction in header:
            _ = f.write(f"{instruction}\n")

        # Writing Body
        riscv_ins = individual.body
        for j in range(len(riscv_ins)):
            if j in individual.label:
                _ = f.write(f"label{j}:\n")

            cur_ins = riscv_ins[j]
            if isinstance(cur_ins, BTypeIns):
                idx: int = bisect.bisect_left(individual.label, j)
                if idx >= len(individual.label):
                    cur_ins.label = "footer"
                else:
                    if individual.label[idx] == j:
                        idx += 1

                    if idx < len(individual.label):
                        cur_ins.label = f"label{individual.label[idx]}"
                    else:
                        cur_ins.label = "footer"

            _ = f.write(f"\t{cur_ins.generate()}\n")

        # Writing Footer
        for instruction in footer:
            _ = f.write(f"{instruction}\n")
        _ = f.write("\n")


def save_to_file(population: list[Program]):
    data_segemnt = generate_data_segment()
    header_part = generate_header()
    footer_part = generate_footer()

    execute_deletion("outputs/rtg_outputs")

    num_files = [i for i in range(TEST_CASES)]

    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        _ = executor.map(
            write_to_file,
            population,
            itertools.repeat(header_part),
            itertools.repeat(footer_part),
            itertools.repeat(data_segemnt),
            num_files,
        )


def add_label_loop(individual: Program):
    for j in range(PROGRAM_LEN):
        is_vset: bool = False
        individual.body[j].index = j  # Store old index's instruction
        instructions_type = individual.body[j].type  # Get current instruction's type

        if HAS_VECTOR and instructions_type == RISCVTypes.V_OPCFG:
            is_vset = True
            individual.label.append(j)

        if (j + 1) % BRANCH_STEP == 0 and (not is_vset):
            individual.label.append(j)


def byte_to_hex(num: int) -> str:
    return hex(num * 1024)


def set_up_link_origin():
    with open("link.ld", "w") as _:
        pass

    text_origin: str = "0x0" if (TEXT_ORIGIN is None) else hex(TEXT_ORIGIN)
    data_origin: str = "0x0" if (DATA_ORIGIN is None) else hex(DATA_ORIGIN)
    text_size: int = (0 if (TEXT_SIZE is None) else TEXT_SIZE) + 1
    data_size: int = (0 if (DATA_SIZE is None) else DATA_SIZE) + 1
    entry_memory: str = f"""ENTRY(main)\n
MEMORY
{{
    text_mem(rx) : ORIGIN = {text_origin}, LENGTH = {text_size}K
    data_mem (rwx) : ORIGIN = {data_origin}, LENGTH = {data_size}K
}}
"""
    sections: str = """SECTIONS
{
    .text : { *(.text) } > text_mem

    .data : { *(.data) *(.sdata) } > data_mem

    .tohost : {
        . = ALIGN(8);
        KEEP(*(.tohost))
        . = ALIGN(8);
    } > data_mem
}"""

    with open("link.ld", "w") as link_ld:
        _ = link_ld.write(entry_memory)
        _ = link_ld.write(sections)

    ORIGIN_TOML_DIR = Path(__file__).resolve().parent
    FILE_NAME: str = "origin.toml"
    with open(ORIGIN_TOML_DIR.joinpath(FILE_NAME)) as _:
        pass
    with open(ORIGIN_TOML_DIR.joinpath(FILE_NAME), "w") as origin_toml:
        _ = origin_toml.write(f"TEXT_MEM_ORIGIN = {text_origin}\n")
        _ = origin_toml.write(f"TEXT_MEM_LENGTH = {byte_to_hex(text_size)}\n")
        _ = origin_toml.write(f"DATA_MEM_ORIGIN = {data_origin}\n")
        _ = origin_toml.write(f"DATA_MEM_LENGTH = {byte_to_hex(data_size)}\n")
