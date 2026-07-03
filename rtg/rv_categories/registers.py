import random

from rtg.settings import HAS_STRIDED, HAS_VECTOR

ACTIVE_REG: list[str] = ["x0"]
integer_index_ua: set[int] = {
    1,  # ra: return address
    2,  # sp: stack pointer
    3,  # gp: global pointer
    4,  # tp: thread pointer
}
integer_index_a: set[int] = {0}


def random_func_reg() -> int:
    while True:
        result: int = random.randint(5, 31)
        if result not in integer_index_ua:
            break

    integer_index_ua.add(result)
    return result


EXTRA_FUNC1: int = random_func_reg()
EXTRA_FUNC2: int = random_func_reg()
BASE_MEM_ADDR: int = random_func_reg()

VECTOR_VSETVL: int = -1 if (not HAS_VECTOR) else random_func_reg()
VECTOR_STRIDED: int = -1 if (not HAS_STRIDED) else random_func_reg()

for i in range(5, 32):
    if i not in integer_index_ua:
        ACTIVE_REG.append(f"x{i}")
        integer_index_a.add(i)

RETURN_ADDR: int = random.choice(list(integer_index_a)[1:])

WORD_DATA_LABEL: str = "data2"
EXTRA_FUNC1_LABEL: str = "extra_func1"
EXTRA_FUNC2_LABEL: str = "extra_func2"

MEM_REG = {
    WORD_DATA_LABEL: f"x{BASE_MEM_ADDR}",
    EXTRA_FUNC1_LABEL: f"x{EXTRA_FUNC1}",
    EXTRA_FUNC2_LABEL: f"x{EXTRA_FUNC2}",
}
