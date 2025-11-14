from datetime import datetime
from typing import List, Tuple

from quasim import Circuit


def count_list_duplicates(circuits: List[Circuit]) -> Tuple[int, float]:
    """Returns a tuple containing the number of counted list duplicates
    as well as the time required to encode and hash the circuits in 
    seconds.
    """

    start = datetime.now()

    encountered_circuits = set()
    duplicates: int = 0

    for circuit in circuits:
        circuit_hash = circuit.__repr__()

        if circuit_hash in encountered_circuits:
            duplicates += 1
        else:
            encountered_circuits.add(circuit_hash)

    end = datetime.now()

    duration = end - start
    duration = duration.total_seconds()

    return duplicates, duration
