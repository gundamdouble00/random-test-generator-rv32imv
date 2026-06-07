import concurrent.futures
import os
import time

from delete_all_files import execute_deletion

SOURCE_DIR: str = "outputs/rtg_outputs"
DEST_DIR: str = "outputs/spike_inputs"
BARE_METAL: str = '\tli t0, 1\n\tla t1, tohost\n\tsw t0, 0(t1)\n\tloop_stop:\n\t\tj loop_stop\n.section .tohost, "aw", @progbits\n.align 8\n.globl tohost\ntohost: .quad 0\n.globl fromhost\nfromhost: .quad 0\n'

enable_vector: str = "\tli t0, 0x00000600\n\tcsrs mstatus, t0\n"
vector_flag: str = "\t# Has Vector\n"


def write_to_new_file(file_name: str):
    src_path = os.path.join(SOURCE_DIR, file_name)
    des_path = os.path.join(DEST_DIR, file_name)
    with open(des_path, "w") as f_out, open(src_path, "r") as f_in:
        for line in f_in:
            _ = f_out.write(line)
            if line == vector_flag:
                _ = f_out.write(enable_vector)

        _ = f_out.write(BARE_METAL)


def main():
    execute_deletion("outputs/spike_inputs")

    files = [
        f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))
    ]

    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(1, max_workers // 2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        _ = executor.map(write_to_new_file, files)


if __name__ == "__main__":
    start = time.time()
    print("Starting adding Startup and Exit code")
    main()
    end = time.time()
    print(f"Finished in {end - start:.2f} seconds.")
