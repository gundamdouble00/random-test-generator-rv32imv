from abc import ABC, abstractmethod
from typing import override


class BaseInstruction(ABC):
    __slots__: tuple[str, ...] = ("name", "type", "index")

    def __init__(self, name: str, index: int):
        self.name: str = name
        self.index: int = index
        self.type: str = ""

    @abstractmethod
    def generate(self) -> str:
        return ""


class BaseIntegerIns(BaseInstruction):
    """
    des: Destination Register\n
    src1: First Source Register\n
    src2: Second Source Register\n
    src3: Third Source Register\n
    imm: Immediate\n
    label: Label's name\n
    """

    __slots__: tuple[str, ...] = ("des", "src1", "src2", "src3", "imm", "label")

    def __init__(self, name: str, index: int) -> None:
        super().__init__(name, index)

        self.des: str = ""
        self.src1: str = ""
        self.src2: str = ""
        self.src3: str = ""
        self.imm: str = ""
        self.label: str = ""

    @override
    def generate(self) -> str:
        return ""


class BaseVectorIns(BaseInstruction):
    """
    lmul: [1/8, 1/4, 1/2, 1, 2, 4, 8]\n
    sew: [8, 16, 32]\n
    des: Destination Vector Register\n
    src2: Second Source Vector Register\n
    src1: First Source Vector Register\n
    """

    __slots__: tuple[str, ...] = ("lmul", "sew", "des", "src2", "src1")

    def __init__(self, name: str, index: int, lmul: float, sew: int) -> None:
        super().__init__(name, index)
        self.lmul: float = lmul
        self.sew: int = sew
        self.des: str = ""
        self.src2: str = ""
        self.src1: str = ""

    @override
    def generate(self) -> str:
        return ""
