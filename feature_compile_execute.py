import concurrent.futures
import os
import subprocess
import sys
import time
from pathlib import Path

from delete_all_files import execute_deletion
from rtg.settings_utils import load_config

OUTPUTS: str = "./outputs"
BIN_FILES: str = OUTPUTS + "/bin_files"
SPIKE_INPUTS: str = OUTPUTS + "/spike_inputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"

LOG: str = ".log"
BINARY: str = ".elf"
ASSEMBLY: str = ".s"
FILE_NAME: str = "rv_assembly"

SUCCESSFULL: str = "successfull"
UNSUCCESSFULL: str = "unsuccessfull"

base_dir = os.path.dirname(os.path.abspath(__file__))
linker_script = os.path.join(base_dir, "link.ld")
num_programs: int = -1


def delete_old_files():
    execute_deletion(BIN_FILES)
    execute_deletion(SPIKE_LOG_FILES)


def running_riscv_toolchain(command_list: list[str], program_index: int):
    try:
        _ = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=True,
        )
        return f"Program {program_index}: Compilation successfull"
    except subprocess.CalledProcessError as _:
        return f"Program {program_index}: Compilation unsuccessfull"


def compile_asm_files():
    """
    Compiles assembly file to ELF files. Using "riscv32-linux-gcc"\n

    # riscv32-linux-gcc -T link.ld -march=rv32imv -mabi=ilp32 -nostdlib -static -o output.elf input.s\n
    - riscv32-linux-gcc: cross-compiler driver\n
    - -T link.ld: -T represents for Linker Script\n
    - -march=rv32imv: ISA\n
    - -mabi=ilp32: Application Binary Interface\n
    - -nostdlib: No Standard Library\n
    - -static: Static Linker\n
    """
    print("""RISC-V GNU Compiler Toolchain""")

    contents_in_dir = os.listdir(SPIKE_INPUTS)
    input_files: list[str] = []

    for item in contents_in_dir:
        if os.path.isfile(os.path.join(SPIKE_INPUTS, item)):
            input_files.append(item)

    global num_programs
    num_programs = len(input_files)

    compile_cmds = [
        [
            "riscv32-linux-gcc",
            "-T",
            linker_script,
            "-march=rv32imv",
            "-mabi=ilp32",
            "-nostdlib",
            "-static",
            "-o",
            f"{BIN_FILES}/{FILE_NAME}{i}{BINARY}",
            f"{SPIKE_INPUTS}/{FILE_NAME}{i}{ASSEMBLY}",
        ]
        for i in range(num_programs)
    ]

    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        result_iterator = executor.map(
            running_riscv_toolchain,
            compile_cmds,
            [i for i in range(num_programs)],
        )
        results = list(result_iterator)

    compile_failed: int = 0
    for info in results:
        messages: list[str] = info.split()
        messages_len: int = len(messages)
        if messages[messages_len - 1] == UNSUCCESSFULL:
            print(info)
            compile_failed += 1

    print(f"Compilation unsuccessful: {compile_failed} programs")


def running_spike_riscv_isa_sim(cmd: list[str], program_index: int):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    log_file: str = SPIKE_LOG_FILES + f"/{FILE_NAME}{program_index}{LOG}"
    while not os.path.exists(log_file):
        time.sleep(0.01)

    with open(log_file, "r") as file:
        while True:
            if process.poll() is not None:
                return f"Program {program_index}: Execution successfull"

            line = file.readline()
            if not line:
                time.sleep(0.01)
                continue

            if "trap_" in line:
                process.terminate()
                return f"Program {program_index}: Execution unsuccessfull"


def spike_executing():
    print("\nSpike RISC-V ISA Simulator")

    origin_toml_path: Path = Path(__file__).resolve().parent / "rtg/ga/origin.toml"
    ORIGIN_TOML = load_config(origin_toml_path)
    if ORIGIN_TOML is None:
        print(f"{origin_toml_path} is not valid")
        sys.exit(1)

    TEXT_MEM_ORIGIN = ORIGIN_TOML["TEXT_MEM_ORIGIN"]
    TEXT_MEM_LENGTH = ORIGIN_TOML["TEXT_MEM_LENGTH"]
    DATA_MEM_ORIGIN = ORIGIN_TOML["DATA_MEM_ORIGIN"]
    DATA_MEM_LENGTH = ORIGIN_TOML["DATA_MEM_LENGTH"]
    spike_cmds = [
        [
            "spike",
            "-l",
            f"--log={SPIKE_LOG_FILES}/" + f"{FILE_NAME}{i}{LOG}",
            # "--isa=rv32gcv_zve32x_zvl128b",
            "--isa=rv32gc_zve32x_zvl128b",
            f"-m{hex(TEXT_MEM_ORIGIN)}:{hex(TEXT_MEM_LENGTH)},{hex(DATA_MEM_ORIGIN)}:{hex(DATA_MEM_LENGTH)}",
            f"{BIN_FILES}/{FILE_NAME}{i}.elf",
        ]
        for i in range(num_programs)
    ]

    # print(" ".join(spike_cmd[0]))
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        result_iterator = executor.map(
            running_spike_riscv_isa_sim,
            spike_cmds,
            [i for i in range(num_programs)],
        )
        results = list(result_iterator)

    execute_failed: int = 0
    for info in results:
        messages: list[str] = info.split()
        messages_len: int = len(messages)
        if messages[messages_len - 1] == UNSUCCESSFULL:
            print(info)
            execute_failed += 1

    print(f"Execution unsuccessful: {execute_failed} programs")


def main():
    # Delete old files in "bin_files" and "spike_log_files" folder
    delete_old_files()

    # Compile assembly files to binary files
    compile_asm_files()

    # Use multithread for running spike concurrently
    spike_executing()


if __name__ == "__main__":
    start = time.time()
    print("Starting Compiling and Executing")
    main()
    end = time.time()
    print(f"Finished in {end - start:.2f} seconds.")
