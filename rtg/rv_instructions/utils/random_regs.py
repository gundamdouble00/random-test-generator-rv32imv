import random

from rtg.rv_categories.registers import ACTIVE_REG


def rand_all_regs() -> str:
    return f"x{random.randint(0, 31)}"


def rand_active_regs() -> str:
    return random.choice(ACTIVE_REG)
