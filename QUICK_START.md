# JLABROC/JSRT-MRMC Python - Quick Start

This page is for first-time users who want to confirm that JLABROC/JSRT-MRMC Python is installed and working correctly.

## 1. Requirements

- Python 3.10 or later
- Internet access during installation if NumPy or SciPy are not already installed

Check Python:

```bash
python --version
```

On macOS/Linux, use `python3 --version` if `python` is not available.

## 2. Install from the repository folder

Open a terminal in the folder containing `pyproject.toml`, then run:

```bash
python -m pip install .
```

On macOS/Linux, use `python3 -m pip install .` if needed.

## 3. JLABROC: run the included example

```bash
python -m jlabroc_jsrt_mrmc jlabroc examples/jlabroc/TestSample1.txt
```

A successful run should end with:

```text
Negative N : 50
Positive N : 50
Fit points : 69
a          : 1.517405
b          : 0.852443
AUC        : 0.875909
```

The complete expected output is in `examples/expected_outputs/TestSample1_expected.txt`.

## 4. JSRT-MRMC: run the matrix-format example

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample2.txt --readers 5 --negative 50 --positive 50
```

A successful run should include:

```text
Mean AUC System 1 : 0.8647
Mean AUC System 2 : 0.8058
Difference        : 0.0589
95% CI            : (0.0371, 0.0807)
F                 : 13.2157
df                : (1, 9)
p                 : 0.005440
```

The complete expected output is in `examples/expected_outputs/TestSample2_expected.txt`.

## 5. Optional: test the original JSRT-MRMC reader-block format

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample3.txt --readers 5 --negative 50 --positive 50
```

This should produce the same numerical results as the matrix-format example.

## 6. If something does not work

- Confirm that Python is version 3.10 or later.
- Run `python -m pip install .` again from the folder containing `pyproject.toml`.
- Use `python -m jlabroc_jsrt_mrmc ...` rather than the shorter console command if the executable is not found.
- Check that the file path is correct and that you are running the command from the repository root.

For more detail, see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) and [`docs/INPUT_FORMATS.md`](docs/INPUT_FORMATS.md).
