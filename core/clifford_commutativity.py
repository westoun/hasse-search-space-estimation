import numpy as np
from quasim.gates import (
    IGate,
    Swap,
    T, S, H, CX
)
from typing import List

from core.gate_sets import CLIFFORD_PLUS_T


def lists_overlap(list1: List, list2: List) -> bool:
    for value1 in list1:
        for value2 in list2:
            if value1 == value2:
                return True

    return False


def commutes(gate1: IGate, gate2: IGate) -> bool:
    if type(gate1) not in CLIFFORD_PLUS_T:
        raise NotImplementedError(
            f"No implementation found for gate type {type(gate1)}")

    if type(gate2) not in CLIFFORD_PLUS_T:
        raise NotImplementedError(
            f"No implementation found for gate type {type(gate2)}")

    # gates acting on different qubits always commute
    if not lists_overlap(gate1.qubits, gate2.qubits):
        return True

    if type(gate1) in [S, T]:

        if type(gate2) in [S, T]:
            return True

        elif type(gate2) == H:
            return False

        elif type(gate2) == CX:

            if gate1.target_qubit == gate2.control_qubit:
                return True
            else:
                return False

        else:
            raise NotImplementedError(
                f"No implementation found for gate type {type(gate2)}")

    elif type(gate1) == H:

        if type(gate2) == H:
            return True

        elif type(gate2) in [S, T]:
            return False

        elif type(gate2) == CX:
            return False

        else:
            raise NotImplementedError(
                f"No implementation found for gate type {type(gate2)}")

    elif type(gate1) == CX:
        if type(gate2) in [S, T]:
            if gate2.target_qubit == gate1.control_qubit:
                return True
            else:
                return False

        elif type(gate2) == H:
            return False

        elif type(gate2) == CX:

            if gate1.control_qubit == gate2.target_qubit or gate1.target_qubit == gate2.control_qubit:
                return False
            else:
                return True

        else:
            raise NotImplementedError(
                f"No implementation found for gate type {type(gate2)}")

    else:
        raise NotImplementedError(
            f"No implementation found for gate type {type(gate1)}")
