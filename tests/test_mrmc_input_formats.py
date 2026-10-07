from pathlib import Path

import numpy as np

from jlabroc_jsrt_mrmc import (
    read_legacy_mrmc_input,
    read_mrmc_input,
    read_mrmc_matrix,
)

DATA = Path(__file__).parent / "data"


def test_legacy_mrmc_reader_blocks_match_matrix_fixture():
    legacy = read_legacy_mrmc_input(
        DATA / "Test_In_forMRMC_R5_P50_N50_legacy.txt",
        n_readers=5,
        n_negative=50,
        n_positive=50,
    )
    matrix = read_mrmc_matrix(
        DATA / "RateData_Level2_R5_ver050_50_50_00001.txt",
        n_readers=5,
    )
    np.testing.assert_array_equal(legacy, matrix)


def test_mrmc_autodetect_reads_both_supported_formats():
    legacy = read_mrmc_input(
        DATA / "Test_In_forMRMC_R5_P50_N50_legacy.txt",
        n_readers=5,
        n_negative=50,
        n_positive=50,
    )
    matrix = read_mrmc_input(
        DATA / "RateData_Level2_R5_ver050_50_50_00001.txt",
        n_readers=5,
        n_negative=50,
        n_positive=50,
    )
    np.testing.assert_array_equal(legacy, matrix)


def test_legacy_mrmc_tolerates_historical_single_star_separator(tmp_path):
    source = (DATA / "Test_In_forMRMC_R5_P50_N50_legacy.txt").read_text()
    malformed = source.replace("* *", "*")
    path = tmp_path / "historical_single_star.txt"
    path.write_text(malformed)

    recovered = read_legacy_mrmc_input(
        path,
        n_readers=5,
        n_negative=50,
        n_positive=50,
    )
    expected = read_mrmc_matrix(
        DATA / "RateData_Level2_R5_ver050_50_50_00001.txt",
        n_readers=5,
    )
    np.testing.assert_array_equal(recovered, expected)
