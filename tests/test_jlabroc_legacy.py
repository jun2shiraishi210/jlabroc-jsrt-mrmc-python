from pathlib import Path

from jlabroc_jsrt_mrmc import fit_jlabroc, read_legacy_jlabroc_input

DATA = Path(__file__).parent / "data"


def test_r1_matches_legacy_output():
    neg, pos = read_legacy_jlabroc_input(DATA / "Test_R1A_In.txt")
    result = fit_jlabroc(neg, pos)
    assert abs(result.a - 1.5174053) < 1e-7
    assert abs(result.b - 0.8524432) < 1e-7
    assert abs(result.auc - 0.8759092) < 1e-7


def test_r2_matches_legacy_output():
    neg, pos = read_legacy_jlabroc_input(DATA / "Test_R2A_In.txt")
    result = fit_jlabroc(neg, pos)
    assert round(result.auc, 6) == 0.862522
