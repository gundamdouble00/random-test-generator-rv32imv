from rtg.rv_categories.riscv_types import RISCVTypes
from rtg.rv_instructions.integer.b_type import BTypeIns
from rtg.rv_instructions.integer.i_type import ITypeIns
from rtg.rv_instructions.integer.j_type import JTypeIns
from rtg.rv_instructions.integer.r_type import RTypeIns
from rtg.rv_instructions.integer.s_type import STypeIns
from rtg.rv_instructions.integer.u_type import UTypeIns
from rtg.rv_instructions.m_extension.mul_div import MulDivIns
from rtg.rv_instructions.v_extension.base_vector import ConfigurationSetting
from rtg.rv_instructions.v_extension.integer_arithmetic import (
    VectorOPIVI,
    VectorOPIVV,
    VectorOPIVX,
    VectorOPMVV,
    VectorOPMVX,
)
from rtg.rv_instructions.v_extension.loads_stores import (
    FaultOnlyFirstLoads,
    Indexed,
    Strided,
    UnitStride,
)

CLASS_OF_TYPE = {
    # RV32I Base Integer Instruction Set
    RISCVTypes.I_OP_R: RTypeIns,
    RISCVTypes.I_OP_I: ITypeIns,
    RISCVTypes.I_OP_S: STypeIns,
    RISCVTypes.I_OP_B: BTypeIns,
    RISCVTypes.I_OP_U: UTypeIns,
    RISCVTypes.I_OP_J: JTypeIns,
    # M Extension for Integer Multiplication and Division
    RISCVTypes.M_OP_M: MulDivIns,
    # V Standard Extension for VectorOperations
    # Vector Integer Arithmetic Instructions
    RISCVTypes.V_OPIVV: VectorOPIVV,
    RISCVTypes.V_OPIVX: VectorOPIVX,
    RISCVTypes.V_OPIVI: VectorOPIVI,
    RISCVTypes.V_OPMVV: VectorOPMVV,
    RISCVTypes.V_OPMVX: VectorOPMVX,
    # Configuration-Setting Instructions
    RISCVTypes.V_OPCFG: ConfigurationSetting,
    # Vector Loads and Stores
    RISCVTypes.V_OP_UNIT_STRIDE: UnitStride,
    RISCVTypes.V_OP_FAULT_ONLY_FIRST_LOADS: FaultOnlyFirstLoads,
    RISCVTypes.V_OP_STRIDED: Strided,
    RISCVTypes.V_OP_INDEXED: Indexed,
}
