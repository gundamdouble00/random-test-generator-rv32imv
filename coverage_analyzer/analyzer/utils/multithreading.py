import concurrent.futures
import os
from typing import Callable, TypeVar

from coverage_analyzer.analyzer.types.log_file import LogFile

T = TypeVar("T")


def using_multithreading(log_files: list[LogFile], func: Callable[[LogFile], T]):
    max_workers = os.cpu_count()
    if max_workers is not None:
        max_workers = max(max_workers // 2, 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, file) for file in log_files]
        _ = concurrent.futures.wait(futures)
