# Beginner example datasets

These files are copied from validation/test materials already included in JLABROC/JSRT-MRMC Python v1.0.1 and are provided here to make first-time testing easier. The beginner-facing copies have been renamed `TestSample1`, `TestSample2`, and `TestSample3`; the original validation/test filenames remain unchanged.

## JLABROC

- `jlabroc/TestSample1.txt`
  - Source in v1.0.1: `validation/data/jlabroc/Test_R1A_In.txt`
  - 50 actually negative and 50 actually positive ratings
  - Expected AUC: 0.875909 at CLI display precision

## JSRT-MRMC

- `mrmc/TestSample2.txt`
  - Source in v1.0.1: `validation/data/mrmc/RateData_Level2_R5_ver050_50_50_00001.txt`
  - Numeric matrix format
  - 5 readers, 50 negative cases, 50 positive cases, 2 systems

- `mrmc/TestSample3.txt`
  - Source in v1.0.1: `tests/data/Test_In_forMRMC_R5_P50_N50_legacy.txt`
  - Original JSRT-MRMC reader-block format
  - Represents the same 5-reader example as the matrix-format file and should produce the same numerical MRMC results

Complete expected CLI outputs are stored under `expected_outputs/`.
