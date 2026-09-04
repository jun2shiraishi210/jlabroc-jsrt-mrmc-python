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

The JSRT-MRMC command accepts a whitespace-delimited numeric matrix for two
systems.

- Rows are cases.
- Actually negative cases must appear first, followed by actually positive cases.
- With `R` readers, the matrix must contain `2R` columns.
- Columns 1 through `R` are ratings for system 1.
- Columns `R+1` through `2R` are ratings from the same readers for system 2.
- The numbers of readers, negative cases, and positive cases are supplied as command-line arguments.

For three readers, the column order is:

```text
S1_R1 S1_R2 S1_R3 S2_R1 S2_R2 S2_R3
```

All ratings must be finite numeric values.
