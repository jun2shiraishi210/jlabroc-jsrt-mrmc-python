# Validation

The validation suite evaluates numerical equivalence between the Python
implementation and frozen full-precision reference results from archived legacy
analyses.

## Archived-reference validation

Run locally:

```bash
python validation/run_validation.py --log validation/logs/validation_local.txt
```

The validator compares JLABROC and JSRT-MRMC output metrics with their frozen
references using predefined tolerances and records the execution environment.

## Systematic simulation validation

Run locally:

```bash
python validation/simulation/run_simulation_validation.py --log validation/simulation/logs/simulation_validation_local.txt
```

The systematic suite covers 59 JLABROC simulation/stress datasets and 35 MRMC
simulation/stress datasets. See `simulation/SIMULATION_DESIGN.md`.

## Cross-platform workflow

`.github/workflows/cross-platform.yml` executes ordinary tests on Windows,
macOS, and Linux with Python 3.10-3.12 and executes both numerical-validation
suites on all three operating systems with Python 3.11. Logs and CSV summaries
are stored as GitHub Actions artifacts.

For a stable public release, all workflow jobs must pass on the exact release
commit.
