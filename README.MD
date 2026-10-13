# Cross-Plattform-Benchmarking

This repository contains experiment code for benchmarking quantum-state generation across multiple hardware backends and cloud platforms.

## Overview

The repository is structured as a benchmark suite, with each maintained platform in a dedicated folder.

## Repository layout

- [GHZ-State Generation](./GHZ-State_Generation) – main benchmark suite for GHZ-state generation experiments.
- [CV_and_BiRB](./CV_and_BiRB) – additional benchmarking work that is still being organized.

## Quick start

1. Read the project-level documentation under [GHZ-State Generation](./GHZ-State%20Generation/README.MD).
2. Choose the target backend you want to benchmark:
   - [AWS](./GHZ-State_Generation/AWS/README.md)
   - [CESGA](./GHZ-State_Generation/CESGA/README.MD)
   - [IBM](./GHZ-State_Generation/IBM/README.MD)
3. Review the backend-specific experiment definition files in each platform folder before running jobs.
