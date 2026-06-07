from collections import defaultdict
from typing import final


@final
class LogFile:
    __slots__: tuple[str, ...] = (
        "index",
        "success",
        "body_addr",
        "footer_addr",
        "body_ins",
        "executed_ins",
        "address_flag",
        "count_type",
        "count_ins",
        "data_hazards",
        "same_operands",
        "immediate",
    )

    def __init__(self, index: int) -> None:
        self.index: int = index
        self.success: bool = True

        self.body_addr: int = 0x0
        self.footer_addr: int = 0x0

        self.body_ins: list[list[str]] = []
        self.executed_ins: list[list[str]] = []

        self.address_flag: dict[int, bool] = defaultdict(bool)

        self.count_type: dict[str, int] = defaultdict(int)
        self.count_ins: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        self.data_hazards: dict[str, int] = defaultdict(int)
        self.same_operands: int = 0
        self.immediate: int = 0
