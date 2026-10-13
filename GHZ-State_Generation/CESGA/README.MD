# CESGA / QMIO GHZ benchmark

This directory contains the GHZ-state benchmarking workflow designed for the CESGA / QMIO environment.

## Purpose

The CESGA implementation focuses on loading backend information, selecting good GHZ circuit structures, and running benchmarking experiments in a cluster-oriented environment.

## Key files

- `main.py` – main orchestration script.
- `submit.sh` – Slurm-style launcher for batch execution on the cluster.
- `utils/benchmark.py` – benchmarking helpers.
- `utils/circuits.py` – GHZ circuit generation and selection logic.
- `experiment_definitions/real_qmio.yml` – example configuration for a real QMIO benchmark.

## Typical usage

### With the cluster launcher

```bash
cd "GHZ-State Generation/CESGA"
chmod +x submit.sh
sbatch submit.sh
```

## Configuration

The YAML files under `experiment_definitions/` define the backend, hardware parameters, and benchmark endpoints. These are the main inputs for controlling the experiment range and noise settings.

## Output

The execution writes result files and calibration metadata to the configured `output_path`, typically an `experiment_results` directory.
