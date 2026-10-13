# AWS GHZ benchmark

This directory contains the Amazon Braket implementation for benchmarking GHZ-state generation on AWS-backed quantum hardware.

## Purpose

The AWS workflow focuses on evaluating GHZ circuits using device metadata, calibration-aware circuit selection, and repeated benchmarking runs over a range of qubit sizes.

## Key files

- `main.py` – main experiment entry point for the GHZ benchmark workflow.
- `main_program_set.py` – program-set based variant of the experiment runner.
- `utils/aws_benchmark.py` – benchmark logic and execution helpers.
- `utils/aws_circuits.py` – GHZ circuit construction and backend-aware circuit generation.
- `utils/process_results.py` – post-processing of result artifacts.
- `experiment_definitions/real_cepheus.yml` – example real backend configuration.
- `requirements.txt` – minimal dependency list.

## Quick start

1. Install dependencies:

   ```bash
   cd "GHZ-State_Generation/AWS"
   pip install -r requirements.txt
   ```

2. Review or adjust the experiment definition file:

   ```bash
   nano experiment_definitions/real_cepheus.yml
   ```

3. Run the benchmark:

   ```bash
   python main.py
   ```

   or, if you want the task-program variant:

   ```bash
   python main_program_set.py
   ```

## Output

The workflow writes benchmark data to experiment result files and calibration metadata, depending on the selected configuration. Results are organized around the number of qubits and backend used.
