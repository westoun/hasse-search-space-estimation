# Hasse Search Space Estimation

This repository contains the source code to the paper
_"Investigating the Potential of Hasse Diagrams for Search Space Reduction in Quantum Circuit Synthesis"_
by Stein and Wimmer from the [Institute of Business Informatics - Software Engineering](https://se.jku.at/) at the [Johannes Kepler University](https://www.jku.at/en), Linz.

## Experiment Configuration

The entrypoint for the experiments we reported in the paper lies
in the `main.py` file. If you wish to run your own experiments,
make sure to call the `run_experiment()`-function with the
experiment configuration you wish to evaluate.

The most important experiment parameters are

- `qubit_num`: number of qubits per circuit.
- `gate_count`: number of gates per circuit.
- `sample_num`: size of the random sample based on which the size of
  the Hasse search space is going to be estimated.

Make sure your sample size is large enough so that the observed duplicate
counts can be expected to be close to their true expected value. If you
do not have a good idea of which sample size to use, the
`if __name__ == "__main__"`-block contains code for estimating sample
size based on a desired confidence level and margin of error.

## Run and Evaluate

Once you have implemented the experiment configurations you wish to run,
execute

```
docker compose up
```

to build and run the corresponding docker container.
The results of each experiment run are saved in the
`results/`-directory.

To generate figures similar to the ones reported in the paper,
open and run the `evaluation.ipynb` notebook.

Have fun!

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
