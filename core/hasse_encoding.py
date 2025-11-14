
from datetime import datetime
import networkx as nx
import numpy as np
from typing import List, Tuple

from quasim import Circuit
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


def circuit_to_graph(circuit: Circuit) -> nx.DiGraph:
    adjacency_matrix = np.zeros(
        shape=(len(circuit.gates), len(circuit.gates)), dtype=int)

    for j, gate1 in enumerate(circuit.gates):

        for k, gate2 in enumerate(circuit.gates[j+1:]):

            if not commutes(gate1, gate2):
                adjacency_matrix[j][j + 1 + k] = 1

                predecessors_of = [j]
                while len(predecessors_of) > 0:
                    target = predecessors_of.pop(0)

                    # Get predecessors of current gate and remove
                    # any potential connections to the new successor.
                    for r in range(len(adjacency_matrix)):
                        if adjacency_matrix[r][target] == 1:
                            adjacency_matrix[r][j + 1 + k] = 0
                            predecessors_of.append(r)

    dag = nx.from_numpy_array(
        adjacency_matrix, create_using=nx.DiGraph)

    node_attrs = {}
    for node, gate in zip(dag.nodes, circuit.gates):
        node_attrs[node] = gate.__repr__().replace(
            "arget", "").replace("ontrol", "")

    nx.set_node_attributes(dag, node_attrs, "gate_config")
    return dag


def graph_to_hash(graph: nx.DiGraph) -> str:
    return nx.weisfeiler_lehman_graph_hash(graph, node_attr="gate_config")


def count_hasse_duplicates(circuits: List[Circuit]) -> Tuple[int, float]:
    """Returns a tuple containing the number of counted hasse duplicates
    as well as the time required to encode and hash the circuits in 
    seconds.
    """
    start = datetime.now()

    encountered_circuits = set()
    duplicates: int = 0

    for circuit in circuits:
        hasse_graph = circuit_to_graph(circuit)
        circuit_hash = graph_to_hash(hasse_graph)

        if circuit_hash in encountered_circuits:
            duplicates += 1
        else:
            encountered_circuits.add(circuit_hash)

    end = datetime.now()

    duration = end - start
    duration = duration.total_seconds()

    return duplicates, duration
