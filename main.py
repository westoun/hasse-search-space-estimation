
from core.utils import get_timestamp, save_to_json
from core.list_encoding import count_list_duplicates
from core.hasse_encoding import count_hasse_duplicates
from core.gate_sets import CLIFFORD_PLUS_T, gateset_to_string
from core.circuit_simulation import run_simulation
from core.circuit_generation import generate_population
from numpy import random as np_random
import random
from statistics import mean
from typing import List, Type
import warnings

# Ignore numpy matmul warning on macos
warnings.filterwarnings("ignore")


def run_experiment(GateSet: List[Type], gate_count: int, qubit_num: int, sample_num: int, seed_num: int = 30, target_dir: str = "results") -> None:
    print("\nStarting new experiment run.")

    experiment = {
        "meta": {
            "start": get_timestamp(),
            "end": None,
        },
        "config": {
            "gate_set": gateset_to_string(GateSet),
            "gate_count": gate_count,
            "qubit_num": qubit_num,
            "sample_num": sample_num,
            "seed_num": seed_num
        },
        "results": {
            "simulation_times": [],
            "mean_simulation_time": None,
            "hasse_duplicate_counts": [],
            "mean_hasse_duplicate_count": None,
            "hasse_encoding_times": [],
            "mean_hasse_encoding_time": None,
            "list_duplicate_counts": [],
            "mean_list_duplicate_count": None,
            "list_encoding_times": [],
            "mean_list_encoding_time": None
        }
    }

    for seed in range(seed_num):
        print(f"\tStarting experiment with seed {seed}.")

        random.seed(seed)
        np_random.seed(seed)

        population = generate_population(
            GateSet=GateSet, gate_count=gate_count, qubit_num=qubit_num, circuit_count=sample_num)

        simulation_time = run_simulation(circuits=population)

        hasse_duplicate_count, hasse_encoding_time = count_hasse_duplicates(
            circuits=population)

        list_duplicate_count, list_encoding_time = count_list_duplicates(
            circuits=population)

        experiment["results"]["simulation_times"].append(simulation_time)
        experiment["results"]["hasse_duplicate_counts"].append(
            hasse_duplicate_count)
        experiment["results"]["hasse_encoding_times"].append(
            hasse_encoding_time)
        experiment["results"]["list_duplicate_counts"].append(
            list_duplicate_count)
        experiment["results"]["list_encoding_times"].append(
            list_encoding_time)

    experiment["results"]["mean_simulation_time"] = mean(
        experiment["results"]["simulation_times"])
    experiment["results"]["mean_hasse_duplicate_count"] = mean(
        experiment["results"]["hasse_duplicate_counts"])
    experiment["results"]["mean_hasse_encoding_time"] = mean(
        experiment["results"]["hasse_encoding_times"])
    experiment["results"]["mean_list_duplicate_count"] = mean(
        experiment["results"]["list_duplicate_counts"])
    experiment["results"]["mean_list_encoding_time"] = mean(
        experiment["results"]["list_encoding_times"])

    experiment["meta"]["end"] = get_timestamp()

    target_path = f"{target_dir}/experiment_{gate_count}g{qubit_num}q_{experiment['meta']['start']}.json"
    save_to_json(experiment, target_path)


if __name__ == "__main__":

    qubit_nums = [3, 4, 5, 6, 7]
    gate_counts = [5, 10, 15, 20]

    for qubit_num in qubit_nums:
        for gate_count in gate_counts:
            run_experiment(GateSet=CLIFFORD_PLUS_T, gate_count=gate_count, qubit_num=qubit_num,
                           sample_num=500_000, seed_num=30)
