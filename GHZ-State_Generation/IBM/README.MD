# IBM GHZ benchmark

This directory contains the IBM Quantum implementation for GHZ-state benchmarking using Qiskit-based workflows and IBM Runtime-style execution patterns.

## Purpose

The IBM implementation evaluates GHZ-state generation across a range of qubit sizes and supports both real IBM hardware and simulator-based exploration through the defined YAML experiment files.

## Key files

- `main.py` – main experiment runner and CLI entry point.
- `utils/benchmark.py` – execution and result-processing helpers.
- `utils/circuits.py` – GHZ circuit generation and topology-aware circuit selection.
- `utils/compute_PC.py` – helper logic for computing GHZ-related performance metrics.
- `experiment_definitions/` – YAML experiment definitions for simulated and real backends.

## Typical usage

Run a benchmark experiment with one of the provided YAML files:

```bash
cd "GHZ-State_Generation/IBM"
python main.py run experiment_definitions/real_torino_2.yml
```

You can also select other definitions such as:

- `fake_brisbane.yml`
- `fake_fez.yml`
- `real_boston.yml`
- `real_pittsburgh.yml`
- `no_noise.yml`

## Configuration

The YAML files contain parameters such as:

- backend name
- user / instance information
- delta and epsilon
- initial and maximum qubit counts
- simulation flag (`true` or `false`)

## Output

Benchmarks save result JSON files, calibration data, and circuit representations to the configured output directory.
