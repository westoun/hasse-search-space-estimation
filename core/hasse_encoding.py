
from datetime import datetime
import networkx as nx
import numpy as np
from typing import List, Tuple

from quasim import Circuit
from quasim.gates import (
    IGate,
    Swap,
)

# from core.commutativity import commutes
from core.clifford_commutativity import commutes


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
