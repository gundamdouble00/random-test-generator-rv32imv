from collections import defaultdict
from typing import final


@final
class LogFile:
    __slots__: tuple[str, ...] = (
        "index",
        "body_addr",
        "footer_addr",
        "executed_ins",
        "count_type",
        "count_ins",
        "success",
    )

    def __init__(self, index: int) -> None:
        self.index: int = index
        self.body_addr: int = 0x0
        self.footer_addr: int = 0x0
        self.executed_ins: list[list[str]] = []
        self.count_type: dict[str, int] = defaultdict(int)
        self.count_ins: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.success: bool = True
