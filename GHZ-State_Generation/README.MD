# GHZ-State Generation

This folder contains the benchmarking code used to generate and evaluate GHZ states across multiple quantum platforms.

## Purpose

The benchmark estimates the fidelity of Greenberger–Horne–Zeilinger (GHZ) states by direct fidelity estimation and searches for the largest GHZ state whose fidelity is compatible, within the statistical error, with the genuine multipartite entanglement threshold F = 1/2. The project compares GHZ-state generation and performance metrics across different cloud and academic quantum environments.

## Included platforms

- [AWS](./AWS/README.md) – Amazon Braket implementation and benchmarking workflow.
- [CESGA](./CESGA/README.MD) – CESGA / QMIO-oriented execution path.
- [IBM](./IBM/README.MD) – IBM Quantum / Qiskit runtime and fake-real backend experiments.

## Typical workflow

1. Select a platform directory.
2. Review or adapt the YAML experiment definition file in that folder.
3. Run the backend-specific script.
4. Collect the output JSON and calibration artifacts written to an experiment-results directory.
5. Compare fidelity, counts, and calibration data across platforms.

## Common data produced

Depending on the backend, the benchmark may generate:

- GHZ circuit definitions
- transpiled circuit artifacts
- calibration metadata
- result JSON files with fidelities and measurement counts
- per-qubit diagnostic information
