from enum import StrEnum


class RISCVTypes(StrEnum):
    # RV32I Base Integer Instruction Set
    I_OP_R = "I_OP_R"
    I_OP_I = "I_OP_I"
    I_OP_S = "I_OP_S"
    I_OP_U = "I_OP_U"
    I_OP_B = "I_OP_B"
    I_OP_J = "I_OP_J"

    # M Extension for Integer Multiplication and Division
    M_OP_M = "M_OP_M"

    # V Standard Extension for VectorOperations
    # Vector Integer Arithmetic Instructions
    V_OPIVV = "V_OPIVV"
    V_OPIVX = "V_OPIVX"
    V_OPIVI = "V_OPIVI"
    V_OPMVV = "V_OPMVV"
    V_OPMVX = "V_OPMVX"
    # Configuration-Setting Instructions
    V_OPCFG = "V_OPCFG"
    # Vector Loads and Stores
    V_OP_UNIT_STRIDE = "V_OP_UNIT_STRIDE"
    V_OP_FAULT_ONLY_FIRST_LOADS = "V_OP_FAULT_ONLY_FIRST_LOADS"
    V_OP_STRIDED = "V_OP_STRIDED"
    V_OP_INDEXED = "V_OP_INDEXED"


TYPE_OF_INS = {
    # RV32I Base Integer Instruction Set
    "RTypeIns": RISCVTypes.I_OP_R,
    "ITypeIns": RISCVTypes.I_OP_I,
    "STypeIns": RISCVTypes.I_OP_S,
    "BTypeIns": RISCVTypes.I_OP_B,
    "UTypeIns": RISCVTypes.I_OP_U,
    "JTypeIns": RISCVTypes.I_OP_J,
    # M Extension for Integer Multiplication and Division
    "MulDivIns": RISCVTypes.M_OP_M,
    # V Standard Extension for VectorOperations
    # Vector Integer Arithmetic Instructions
    "VectorOPIVV": RISCVTypes.V_OPIVV,
    "VectorOPIVX": RISCVTypes.V_OPIVX,
    "VectorOPIVI": RISCVTypes.V_OPIVI,
    "VectorOPMVV": RISCVTypes.V_OPMVV,
    "VectorOPMVX": RISCVTypes.V_OPMVX,
    # Configuration-Setting Instructions
    "ConfigurationSetting": RISCVTypes.V_OPCFG,
    # Vector Loads and Stores
    "UnitStride": RISCVTypes.V_OP_UNIT_STRIDE,
    "FaultOnlyFirstLoads": RISCVTypes.V_OP_FAULT_ONLY_FIRST_LOADS,
    "Strided": RISCVTypes.V_OP_STRIDED,
    "Indexed": RISCVTypes.V_OP_INDEXED,
}
