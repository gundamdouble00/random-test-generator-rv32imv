import random
import sys
from pathlib import Path

from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.settings_utils import (
    check_data_text_segment,
    get_float_value,
    get_integer_value,
    get_segment_value,
    load_config,
)

BASE_DIR = Path(__file__).resolve().parent
RTG_CFG_PATH: Path = BASE_DIR / "rtg_config.toml"
USR_CFG_PATH: Path = BASE_DIR.parent / "user_config.toml"
USER_CONFIG = load_config(USR_CFG_PATH)
RTG_CONFIG = load_config(RTG_CFG_PATH)

if (USER_CONFIG is None) or (RTG_CONFIG is None):
    sys.exit(1)

# Check TEST_CASES's value
TEST_CASES: int = get_integer_value(USER_CONFIG, "TEST_CASES")

# Check PROGRAM_LEN's value
PROGRAM_LEN: int = get_integer_value(USER_CONFIG, "PROGRAM_LEN")
PROGRAM_SIZE_IN_KB = (PROGRAM_LEN * 32) // (8 * 1024) + 1

# Check SIZE's value ([TEXT])
TEXT_SIZE: int | None = get_segment_value(USER_CONFIG, "TEXT", "SIZE")
if TEXT_SIZE is None:
    sys.exit(1)

if PROGRAM_SIZE_IN_KB > TEXT_SIZE:
    print("The length of text segment is not enough for program!!!")
    sys.exit(1)

DATA_SIZE: int | None = get_segment_value(USER_CONFIG, "DATA", "SIZE")
if DATA_SIZE is None:
    sys.exit(1)

WORD_MEMORY = (DATA_SIZE * 8 * 1024) // 32

TEXT_ORIGIN: int | None = get_segment_value(USER_CONFIG, "TEXT", "ORIGIN")
DATA_ORIGIN: int | None = get_segment_value(USER_CONFIG, "DATA", "ORIGIN")
if (TEXT_ORIGIN is None) or (DATA_ORIGIN is None):
    sys.exit(1)

if not check_data_text_segment(TEXT_ORIGIN, TEXT_SIZE, DATA_ORIGIN, DATA_SIZE):
    sys.exit(1)


# Check sum of rates
sum_of_rates: int = 0
RV32_RATES = USER_CONFIG["RV32_RATES"]
for key in RV32_RATES.keys():
    value = RV32_RATES[key]
    if not isinstance(value, int):
        print(f"The value of {key} must be an integer")
        sys.exit(1)
    sum_of_rates += value
if sum_of_rates != 100:
    print(f"The sum of rates must be equal 100 (Current sum: {sum_of_rates})")
    sys.exit(1)

NUM_GENERATIONS = get_integer_value(RTG_CONFIG, "NUM_GENERATIONS")
MUTATION_RATE = get_float_value(RTG_CONFIG, "MUTATION_RATE")
CROSSOVER_RATE = get_float_value(RTG_CONFIG, "CROSSOVER_RATE")

LOOP_N: int = 0
# LOOP_N: int = random.randint(0, 3)
LOOP_TIME: int = 0 if (LOOP_N <= 0) else (random.randint(1, 10))

RISCV_32_INS = USER_CONFIG["RV32_INSTRUCTIONS"]
RISCV_32_TYPES: dict[str, RISCVTypes] = {}
for type, instructions in RISCV_32_INS.items():
    for ins in instructions:
        RISCV_32_TYPES[ins] = type

PROGRAM_INS: dict[RISCVTypes, int] = {}
vector_rate: int = 0
for key, val in RV32_RATES.items():
    if val > 0.0:
        PROGRAM_INS[RISCVTypes(key)] = (PROGRAM_LEN * val) // 100

    if key.startswith("V"):
        vector_rate += val
        if key == RISCVTypes.V_OP_STRIDED:
            HAS_STRIDED: bool = False if (val == 0) else True

HAS_VECTOR: bool = False if (vector_rate == 0) else True

DATA_HAZARD_SCORE = get_integer_value(RTG_CONFIG, "DATA_HAZARD_SCORE")
NEGATIVE_IMM_SCORE = get_integer_value(RTG_CONFIG, "NEGATIVE_IMM_SCORE")
SAME_OPERANDS_SCORE = get_integer_value(RTG_CONFIG, "SAME_OPERANDS_SCORE")
PENALTY_PER_MISSING = get_integer_value(RTG_CONFIG, "PENALTY_PER_MISSING")

settings: list[tuple[int, float]] = []
instructions_per_path: int = -1
if HAS_VECTOR:
    v_sew: list[int] = [8, 16, 32]
    v_lmul: list[float] = [1 / 4, 1 / 2, 1, 2, 4, 8]
    vector_cfg_num: int = PROGRAM_INS[RISCVTypes.V_OPCFG]
    if vector_cfg_num == 0:
        vector_cfg_num = 1

    instructions_per_path = PROGRAM_LEN // vector_cfg_num
    while len(settings) < vector_cfg_num:
        sew = random.choice(v_sew)
        lmul = random.choice(v_lmul)
        if lmul >= (sew / 32):
            settings.append((sew, lmul))
INSTRUCTIONS_PER_PATH = instructions_per_path
