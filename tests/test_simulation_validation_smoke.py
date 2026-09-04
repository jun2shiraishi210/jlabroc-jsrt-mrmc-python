import json
from pathlib import Path

import numpy as np

from jlabroc_jsrt_mrmc.io import read_legacy_jlabroc_input, read_mrmc_matrix
from jlabroc_jsrt_mrmc.jlabroc import fit_jlabroc
from jlabroc_jsrt_mrmc.mrmc import analyze_mrmc

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "validation" / "simulation"


def test_jlabroc_simulation_reference_smoke():
    refs = json.loads((SIM / "reference" / "jlabroc_sim_cpp_reference.json").read_text())
    ref = refs["J_grid_N050_P050_A080_B100"]
    neg, pos = read_legacy_jlabroc_input(SIM / "data" / "jlabroc" / ref["file"])
    r = fit_jlabroc(neg, pos)
    assert abs(r.a - ref["a"]) <= 5e-8
    assert abs(r.b - ref["b"]) <= 5e-8
    assert abs(r.auc - ref["auc"]) <= 2e-9


def test_mrmc_simulation_reference_smoke():
    refs = json.loads((SIM / "reference" / "mrmc_sim_cpp_reference.json").read_text())
    ref = refs["MFG14_R5_N50_P50_A080_A076_C50_R20_TR20"]
    data = read_mrmc_matrix(SIM / "data" / "mrmc" / ref["file"], ref["readers"])
    r = analyze_mrmc(data, n_readers=ref["readers"], n_negative=ref["negative"], n_positive=ref["positive"])
    assert np.max(np.abs(r.auc_table - np.asarray(ref["reader_auc"]))) <= 2e-9
    assert np.max(np.abs(r.pseudo_values - np.asarray(ref["pseudo_values"]))) <= 3e-7
    assert abs(r.anova.f_value - ref["f"]) <= 5e-6
    assert abs(r.anova.p_value - ref["p"]) <= 1e-7
