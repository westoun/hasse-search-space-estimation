from datetime import datetime
from quasim import Circuit, QuaSim
from typing import List


def run_simulation(circuits: List[Circuit]) -> float:
    """Returns the total simulation time in seconds.
    """

    simulator = QuaSim()

    start = datetime.now()

    simulator.evaluate(circuits)

    end = datetime.now()

    duration = end - start
    return duration.total_seconds()
