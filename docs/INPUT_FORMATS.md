# Input data formats

## JLABROC

The JLABROC command accepts the legacy ROCKIT/JLABROC text layout used by the
original JLABROC workflow. Tokens are whitespace-separated.

1. Four legacy header tokens appear first. They are retained for input-format compatibility and are not used by the Python ROC calculation.
2. Ratings for actually negative cases follow.
3. A token containing `*` separates negative and positive ratings.
4. Ratings for actually positive cases follow.
5. A second `*` terminates the rating section.

Example:

```text
HEADER1 HEADER2 HEADER3 HEADER4
0.12 0.35 0.51 0.77
*
0.68 0.82 0.95 1.14
*
```

The Python parser converts the values before the first `*` to the negative
rating vector and the values between the two `*` tokens to the positive rating
vector.

## JSRT-MRMC

The JSRT-MRMC command accepts **two** input layouts.  The numbers of readers,
actually negative cases, and actually positive cases are supplied as
command-line arguments for both layouts.

### 1. Numeric matrix format

This is the compact matrix format supported by JLABROC/JSRT-MRMC Python 1.0.0.

- Rows are cases.
- Actually negative cases must appear first, followed by actually positive cases.
- With `R` readers, the matrix must contain `2R` columns.
- Columns 1 through `R` are ratings for system 1.
- Columns `R+1` through `2R` are ratings from the same readers for system 2.

For three readers, the column order is:

```text
S1_R1 S1_R2 S1_R3 S2_R1 S2_R2 S2_R3
```

### 2. Original JSRT-MRMC reader-block format

Version 1.0.1 adds direct input compatibility with the text layout used by the
original JSRT-MRMC executable.  Each reader has a block containing two rating
columns: system 1 followed by system 2.  The actually negative rows appear
first, then a star separator line, then the actually positive rows, followed by
a second star separator line.

A typical block is:

```text
STUDY:
Reader1
"High" "Low"
L L
34 36
33 20
...
* *
28 30
39 32
...
* *
Reader2
...
```

The canonical two-system legacy separator is `* *`.  For robustness, the Python
parser also accepts a separator line containing a single `*`.  This tolerance is
intentional because historical sample files existed with a single-star line;
the original executable could misparse those files, whereas the Python parser
recovers the intended two-column reader block.

The reader blocks are converted internally to the same matrix layout described
above before MRMC analysis.  Consequently, the numerical calculation is
identical regardless of which supported input layout is used.

Example:

```bash
jlabroc-jsrt-mrmc mrmc tests/data/Test_In_forMRMC_R5_P50_N50_legacy.txt --readers 5 --negative 50 --positive 50
```

All ratings must be finite numeric values.  The number of `ReaderN` blocks and
the negative/positive row counts in every block are checked against the command-line
arguments.
