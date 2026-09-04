from pathlib import Path
import numpy as np

from jlabroc_jsrt_mrmc import analyze_mrmc, read_mrmc_matrix

DATA = Path(__file__).parent / "data"


def test_mrmc_matches_legacy_saved_output():
    ratings = read_mrmc_matrix(
        DATA / "RateData_Level2_R5_ver050_50_50_00001.txt", n_readers=5
    )
    result = analyze_mrmc(
        ratings, n_readers=5, n_negative=50, n_positive=50
    )

    expected_auc = np.array([
        [0.8759, 0.8154],
        [0.8625, 0.7817],
        [0.8344, 0.7988],
        [0.8797, 0.8107],
        [0.8710, 0.8223],
    ])
    np.testing.assert_allclose(result.auc_table, expected_auc, atol=5e-5)
    assert abs(result.mean_auc_system1 - 0.8647) < 5e-5
    assert abs(result.mean_auc_system2 - 0.8058) < 5e-5
    assert abs(result.difference - 0.0589) < 5e-5
    assert abs(result.ci_lower - 0.0371) < 5e-5
    assert abs(result.ci_upper - 0.0807) < 5e-5

    a = result.anova
    np.testing.assert_allclose(
        [a.ss_t, a.ss_tr, a.ss_tc, a.ss_trc],
        [4.4664, 0.8803, 14.1627, 9.9692],
        atol=5e-5,
    )
    assert abs(a.f_value - 13.216) < 5e-4
    assert a.df1 == 1
    assert a.df2 == 9
    assert abs(a.p_value - 0.00544) < 5e-5
