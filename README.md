# JLABROC/JSRT-MRMC Python

JLABROC/JSRT-MRMC Python is a Python implementation of the computational cores
of JLABROC (single-reader binormal ROC fitting) and JSRT-MRMC (two-system
multi-reader multi-case analysis).

This repository contains the stable public release of JLABROC/JSRT-MRMC Python.
The computational methods preserve the validated behavior of the legacy programs,
including the JLABROC tied-rating ordering used for numerical compatibility and
the JSRT-MRMC denominator-degrees-of-freedom integerization rule.

## Requirements

- Python 3.10 or later
- NumPy
- SciPy

Install from a local clone:

```bash
python -m pip install -e .
```

For the test suite:

```bash
python -m pip install pytest
python -m pytest -q
```

## Command-line use

Single-reader JLABROC-compatible analysis:

```bash
jlabroc-jsrt-mrmc jlabroc tests/data/Test_R1A_In.txt
```

Two-system JSRT-MRMC-compatible analysis using the numeric matrix format:

```bash
jlabroc-jsrt-mrmc mrmc tests/data/RateData_Level2_R5_ver050_50_50_00001.txt --readers 5 --negative 50 --positive 50
```

The original JSRT-MRMC reader-block text format is also accepted directly:

```bash
jlabroc-jsrt-mrmc mrmc tests/data/Test_In_forMRMC_R5_P50_N50_legacy.txt --readers 5 --negative 50 --positive 50
```

Both input layouts are converted to the same internal rating matrix before the
validated MRMC calculation is performed.

The same commands can also be invoked with:

```bash
python -m jlabroc_jsrt_mrmc ...
```

See [`docs/INPUT_FORMATS.md`](docs/INPUT_FORMATS.md) for the input layouts.

## Methods implemented

### JLABROC

The JLABROC implementation constructs sequential empirical ROC operating
points from continuous ratings, removes boundary points for which FPF or TPF is
0 or 1, transforms the remaining points to normal-deviate coordinates, fits
`y = a + b*x` by least squares, and calculates
`AUC = Phi(a / sqrt(1 + b^2))`.

Tied ratings are processed using the same deterministic comparison-and-swap
sequence as the validated legacy implementation. This behavior is retained
because tied negative and positive ratings can otherwise change the sequence of
intermediate ROC operating points and produce small numerical differences.

### JSRT-MRMC

For each reader and system, AUC is estimated with JLABROC. Leave-one-case-out
AUCs are then used to form jackknife pseudo-values, followed by the validated
JSRT-MRMC ANOVA procedure for comparing two mean AUCs. Confidence intervals
are reported in conventional `(lower, upper)` order.

## Validation

Two complementary validation suites are included.

### Archived-reference validation

```bash
python validation/run_validation.py --log validation/logs/validation_local.txt
```

This compares the Python implementation with frozen full-precision numerical
reference values from archived legacy analyses.

### Systematic simulation validation

```bash
python validation/simulation/run_simulation_validation.py --log validation/simulation/logs/simulation_validation_local.txt
```

The systematic suite contains:

- 48 regular JLABROC binormal simulation datasets;
- 9 additional fittable JLABROC stress datasets;
- 2 intentionally non-fittable JLABROC datasets for controlled error handling;
- 27 MRMC factorial variance/dependence stress datasets; and
- 8 additional MRMC design/AUC stress datasets.

The MRMC factorial grid varies shared-case fraction (0.0, 0.5, 0.9), reader-effect
SD (0.0, 0.2, 0.4), and treatment-reader-effect SD (0.0, 0.2, 0.4). The two SD
factors are standardized relative to unit residual noise and are implementation
stress levels rather than clinical variance estimates.

See [`validation/simulation/SIMULATION_DESIGN.md`](validation/simulation/SIMULATION_DESIGN.md)
for the full design.

## Cross-platform continuous integration

The GitHub Actions workflow runs:

1. the ordinary test suite on Windows, macOS, and Linux with Python 3.10, 3.11, and 3.12;
2. archived-reference numerical validation on all three operating systems with Python 3.11; and
3. systematic simulation validation on all three operating systems with Python 3.11.

A public stable release should be tagged only after all jobs pass for the release
commit.

## Reproducibility

Synthetic datasets use fixed random seeds. Generator parameters are recorded in
`validation/simulation/simulation_manifest.json`. Frozen numerical references
used for regression testing are included in the repository; provenance details
are documented in `validation/simulation/REFERENCE_PROVENANCE.md`.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). The software
author is Junji Shiraishi. After publication of the accompanying validation
paper, the `preferred-citation` entry will be updated to point to that article.

The computational methods implemented here build on:

Shiraishi J, Fukuoka D, Iha R, et al. Verification of modified
receiver-operating characteristic software using simulated rating data.
*Radiological Physics and Technology*. 2018;11:406-414.
doi:10.1007/s12194-018-0479-9.

## License

This software is released under the BSD 3-Clause License. See
[`LICENSE`](LICENSE). Copyright (c) 2026 Junji Shiraishi.
