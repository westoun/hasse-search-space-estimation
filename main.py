
import numpy as np

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


def calculate_list_search_space_size(qubit_num: int, gate_count: int) -> int:
    # assuming Clifford+T gate set
    return (qubit_num * (qubit_num - 1) + 3 * qubit_num) ** gate_count


def calculate_expected_duplicates(size: int, sample_num: int) -> int:
    expected_duplicates = sample_num - size + size * (1 - 1/size) ** sample_num
    return expected_duplicates


def estimate_search_space_size(sample_num: int, actual_duplicates: int, lower_bound: int, upper_bound: int) -> int:
    if actual_duplicates == 0:
        return upper_bound

    # Expected number of duplicates decreases monotonically as search space increases

    search_range = (lower_bound, upper_bound)
    search_post_count = 3

    while True:

        # cut search interval into bins and evaluate
        search_posts = [
            i * (search_range[1] - search_range[0]) / (search_post_count - 1) + search_range[0] for i in range(search_post_count)
        ]
        search_posts = [int(search_post) for search_post in search_posts]

        smallest_delta = np.inf
        best_i = -1

        for search_post_i, search_post in enumerate(search_posts):
            estimated_duplicates = calculate_expected_duplicates(
                search_post, sample_num)
            delta = abs(estimated_duplicates - actual_duplicates)

            if delta < smallest_delta:
                smallest_delta = delta
                best_i = search_post_i

        if smallest_delta <= 1:
            return search_posts[best_i]

        try:
            if calculate_expected_duplicates(search_posts[best_i], sample_num) > actual_duplicates:
                search_range = (search_posts[best_i], search_posts[best_i + 1])
            else:
                search_range = (search_posts[best_i - 1], search_posts[best_i])
        except IndexError:  # Case: border of search posts is closest to solution.
            return search_posts[best_i]

        if (search_range[1] - search_range[0]) / (search_post_count - 1) <= 1:
            return search_posts[best_i]


def is_valid_sample_size(gate_count: int, qubit_num: int, sample_num: int, margin: float = 0.05, confidence: float = 0.9, total_runs: int = 100) -> bool:

    true_size = calculate_list_search_space_size(
        qubit_num, gate_count)

    confidence_interval = (true_size * (1 - margin), true_size * (1 + margin))

    runs_within_interval = 0

    for i in range(total_runs):
        random.seed(i)
        np_random.seed(i)

        population = generate_population(
            GateSet=CLIFFORD_PLUS_T, gate_count=gate_count, qubit_num=qubit_num, circuit_count=sample_num)

        list_duplicate_count, _ = count_list_duplicates(
            circuits=population)

        estimated_size = estimate_search_space_size(
            sample_num, list_duplicate_count, lower_bound=1, upper_bound=true_size * 2)

        if estimated_size > confidence_interval[0] and estimated_size < confidence_interval[1]:
            runs_within_interval += 1

    print(
        f"Confidence value for sample size = {sample_num}: {runs_within_interval / total_runs}")
    return runs_within_interval / total_runs >= confidence


def run_experiment(gate_count: int, qubit_num: int, sample_num: int, seed_num: int = 30, target_dir: str = "results") -> None:
    print("\nStarting new experiment run.")

    experiment = {
        "meta": {
            "start": get_timestamp(),
            "end": None,
        },
        "config": {
            "gate_set": gateset_to_string(CLIFFORD_PLUS_T),
            "gate_count": gate_count,
            "qubit_num": qubit_num,
            "sample_num": sample_num,
            "seed_num": seed_num
        },
        "results": {
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
            GateSet=CLIFFORD_PLUS_T, gate_count=gate_count, qubit_num=qubit_num, circuit_count=sample_num)

        hasse_duplicate_count, hasse_encoding_time = count_hasse_duplicates(
            circuits=population)

        list_duplicate_count, list_encoding_time = count_list_duplicates(
            circuits=population)

        experiment["results"]["hasse_duplicate_counts"].append(
            hasse_duplicate_count)
        experiment["results"]["hasse_encoding_times"].append(
            hasse_encoding_time)
        experiment["results"]["list_duplicate_counts"].append(
            list_duplicate_count)
        experiment["results"]["list_encoding_times"].append(
            list_encoding_time)

    experiment["results"]["mean_hasse_duplicate_count"] = mean(
        experiment["results"]["hasse_duplicate_counts"])
    experiment["results"]["mean_hasse_encoding_time"] = mean(
        experiment["results"]["hasse_encoding_times"])
    experiment["results"]["mean_list_duplicate_count"] = mean(
        experiment["results"]["list_duplicate_counts"])
    experiment["results"]["mean_list_encoding_time"] = mean(
        experiment["results"]["list_encoding_times"])

    experiment["meta"]["end"] = get_timestamp()

    target_path = f"{target_dir}/experiment_{qubit_num}q{gate_count}g_{experiment['meta']['start']}.json"
    save_to_json(experiment, target_path)


if __name__ == "__main__":

    MAX_SAMPLE_SIZE = 100_000_000

    qubit_nums = [3, 4, 5, 6]
    gate_counts = [4, 6, 8, 10, 12]

    for qubit_num in qubit_nums:
        sample_num = 10_000

        for gate_count in gate_counts:
            print(
                f"\nSetting up experiment with q={qubit_num} and g={gate_count}")

            while sample_num < MAX_SAMPLE_SIZE:

                if is_valid_sample_size(gate_count, qubit_num, sample_num, margin=0.05, confidence=0.9):
                    break

                sample_num *= 2
            else:
                print(
                    f"Next sample num would exceed feasability threshold of {MAX_SAMPLE_SIZE} samples. Skipping g>={gate_count}")
                break

            print(
                f"Sample size for q={qubit_num} and g={gate_count}: {sample_num}")

            run_experiment(gate_count=gate_count, qubit_num=qubit_num,
                           sample_num=sample_num, seed_num=30, target_dir="results")
