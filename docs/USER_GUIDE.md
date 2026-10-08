# JLABROC/JSRT-MRMC Python - Beginner User Guide

This guide is for first-time users of JLABROC/JSRT-MRMC Python version 1.0.1. It explains how to install the package, run known examples, interpret the main outputs, and prepare your own input files.

> **Recommended first step:** Run `TestSample1`, `TestSample2`, and `TestSample3` before using your own data. Compare the displayed results with the files in `examples/expected_outputs/`.

## 1. What the software does

- **JLABROC** performs single-reader binormal ROC fitting from actually negative and actually positive rating data.
- **JSRT-MRMC** compares two systems in a multi-reader multi-case study. Reader-system AUCs are estimated with JLABROC, followed by the validated JSRT-MRMC jackknife/ANOVA procedure.
- Version 1.0.1 accepts both the numeric matrix format and the original JSRT-MRMC reader-block format.

## 2. Requirements and installation

Requirements: Python 3.10 or later, NumPy 1.24 or later, and SciPy 1.10 or later.

```bash
python --version
python -m pip install .
python -m jlabroc_jsrt_mrmc --help
```

The help message should list the `jlabroc` and `mrmc` subcommands.

## 3. JLABROC example: TestSample1

```bash
python -m jlabroc_jsrt_mrmc jlabroc examples/jlabroc/TestSample1.txt
```

Expected final values:

```text
Negative N : 50
Positive N : 50
Fit points : 69
a          : 1.517405
b          : 0.852443
AUC        : 0.875909
```

## 4. JSRT-MRMC matrix example: TestSample2

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample2.txt --readers 5 --negative 50 --positive 50
```

Expected key values:

```text
Mean AUC System 1 : 0.8647
Mean AUC System 2 : 0.8058
Difference        : 0.0589
95% CI            : (0.0371, 0.0807)
F                 : 13.2157
df                : (1, 9)
p                 : 0.005440
```

Rows are cases. Negative cases come first, followed by positive cases. For `R` readers, each row contains `2R` columns: all system-1 reader ratings followed by all system-2 reader ratings.

## 5. JSRT-MRMC legacy example: TestSample3

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample3.txt --readers 5 --negative 50 --positive 50
```

`TestSample3.txt` contains the same 5-reader data as `TestSample2.txt`, but in the original JSRT-MRMC reader-block format. It should produce the same numerical MRMC results.

The canonical two-system separator is `* *`; version 1.0.1 also accepts a single `*` separator for robustness with historical sample files.

## 6. Using your own data

For JLABROC, place actually negative ratings before the first `*` separator and actually positive ratings between the first and second separators.

For JSRT-MRMC matrix input, use exactly `2R` columns for `R` readers, with negative cases first and positive cases second. Keep the same reader order for both systems.

## 7. Troubleshooting

| Problem | What to check |
|---|---|
| `python` is not recognized | Try `py` on Windows or `python3` on macOS/Linux. Confirm Python 3.10+ is installed. |
| `No module named jlabroc_jsrt_mrmc` | Run `python -m pip install .` from the repository root. |
| Input file not found | Check the current folder and path; quote paths containing spaces. |
| MRMC row/column error | Confirm `--readers`, `--negative`, `--positive`, and that a matrix has `2R` columns. |
| Legacy MRMC parse error | Confirm each `ReaderN` block has two numeric columns and the expected row counts. |
| JLABROC non-analyzable | Check for insufficient non-boundary ROC points or non-finite values. |

## 8. Optional full software checks

```bash
python -m pip install pytest
python -m pytest -q
python validation/run_validation.py --log validation/logs/validation_local.txt
python validation/simulation/run_simulation_validation.py --log validation/simulation/logs/simulation_validation_local.txt
```

The validation tolerances are numerical-equivalence criteria, not statistical significance thresholds.

## 9. Documentation and provenance

- [`QUICK_START.md`](../QUICK_START.md)
- [`QUICK_START_JA.md`](../QUICK_START_JA.md)
- [`docs/INPUT_FORMATS.md`](INPUT_FORMATS.md)
- [`examples/README.md`](../examples/README.md)
- [`examples/PROVENANCE.md`](../examples/PROVENANCE.md)

The beginner examples are copies of files already present in the validated v1.0.1 repository. The original files remain unchanged.
