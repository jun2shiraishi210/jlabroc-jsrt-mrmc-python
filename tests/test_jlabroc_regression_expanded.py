import json
from pathlib import Path
import pytest
from jlabroc_jsrt_mrmc.io import read_legacy_jlabroc_input
from jlabroc_jsrt_mrmc.jlabroc import fit_jlabroc

ROOT=Path(__file__).resolve().parents[1]
REF=json.loads((ROOT/'validation/reference/jlabroc_cpp_reference.json').read_text())
@pytest.mark.parametrize('name',[n for n,v in REF.items() if 'a' in v])
def test_jlabroc_against_cpp_full_precision(name):
    ref=REF[name]
    neg,pos=read_legacy_jlabroc_input(ROOT/'validation/data/jlabroc'/name)
    r=fit_jlabroc(neg,pos)
    assert abs(r.a-ref['a']) <= 5e-7
    assert abs(r.b-ref['b']) <= 2e-7
    assert abs(r.auc-ref['auc']) <= 2e-9

def test_degenerate_legacy_nan_is_controlled_error():
    neg,pos=read_legacy_jlabroc_input(ROOT/'validation/data/jlabroc/L1_vs_L4_In.txt')
    with pytest.raises(ValueError, match='insufficient non-boundary ROC points'):
        fit_jlabroc(neg,pos)
