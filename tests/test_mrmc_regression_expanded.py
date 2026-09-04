import json
from pathlib import Path
import numpy as np
import pytest
from jlabroc_jsrt_mrmc.io import read_mrmc_matrix
from jlabroc_jsrt_mrmc.mrmc import analyze_mrmc

ROOT=Path(__file__).resolve().parents[1]
REF=json.loads((ROOT/'validation/reference/mrmc_cpp_reference.json').read_text())
@pytest.mark.parametrize('label',['R5','R6'])
def test_mrmc_against_cpp_full_precision(label):
    ref=REF[label]
    data=read_mrmc_matrix(ROOT/'validation/data/mrmc'/ref['file'], ref['readers'])
    r=analyze_mrmc(data,n_readers=ref['readers'],n_negative=ref['negative'],n_positive=ref['positive'])
    assert np.max(np.abs(r.auc_table-np.asarray(ref['reader_auc']))) <= 2e-9
    assert abs(r.mean_auc_system1-ref['mean1']) <= 2e-9
    assert abs(r.mean_auc_system2-ref['mean2']) <= 2e-9
    assert abs(r.difference-ref['difference']) <= 2e-9
    assert abs(r.ci_lower-ref['ci_lower']) <= 3e-6
    assert abs(r.ci_upper-ref['ci_upper']) <= 3e-6
    a=ref['anova']
    for got,key in [(r.anova.ss_t,'ss_t'),(r.anova.ss_tr,'ss_tr'),(r.anova.ss_tc,'ss_tc'),(r.anova.ss_trc,'ss_trc'),(r.anova.ms_t,'ms_t'),(r.anova.ms_tr,'ms_tr'),(r.anova.ms_tc,'ms_tc'),(r.anova.ms_trc,'ms_trc')]:
        assert abs(got-a[key]) <= 2e-6
    assert abs(r.anova.f_value-a['f']) <= 2e-7
    assert r.anova.df1 == a['df1'] and r.anova.df2 == a['df2']
    assert abs(r.anova.p_value-a['p']) <= 1e-7
