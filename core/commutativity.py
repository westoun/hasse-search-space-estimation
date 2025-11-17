
import numpy as np
from quasim.gates import (
    IGate,
    Swap,
)


PROJECTOR_0 = np.array([[1, 0], [0, 0]], dtype=np.complex128)
PROJECTOR_1 = np.array([[0, 0], [0, 1]], dtype=np.complex128)


def commutes_with_projectors(matrix: np.ndarray) -> bool:
    return commutes_with_matrix(matrix, PROJECTOR_0) and commutes_with_matrix(matrix, PROJECTOR_1)


def commutes_with_matrix(matrix1: np.ndarray, matrix2: np.ndarray) -> bool:
    product1 = np.matmul(matrix1, matrix2)
    product2 = np.matmul(matrix2, matrix1)
    return np.array_equal(product1, product2)


def commutes_on_qubit(gate1: IGate, gate2: IGate, qubit: int) -> bool:
    # TODO: handle swap gates
    assert type(gate1) != Swap
    assert type(gate2) != Swap

    # Case: Gates act on separate qubits
    if qubit not in gate2.qubits:
        return True

    # Case: qubit is target qubit of gate1
    if gate1.target_qubit == qubit:

        # Case: qubit is target qubit of gate 2
        if gate2.target_qubit == qubit:
            return commutes_with_matrix(gate1.matrix, gate2.matrix)

        # Case: qubit is one of the controll qubits of gate 2
        else:
            return commutes_with_projectors(gate1.matrix)

    # Case: qubit is one of the controll qubits of gate1
    else:

        # Case: qubit is target qubit of gate 2
        if gate2.target_qubit == qubit:
            return commutes_with_projectors(gate2.matrix)

        # Case: qubit is one of the controll qubits of gate 2
        else:
            return True



def commutes(gate1: IGate, gate2: IGate) -> bool:
    for qubit in gate1.qubits:
        if not commutes_on_qubit(gate1, gate2, qubit):
            return False

    return True