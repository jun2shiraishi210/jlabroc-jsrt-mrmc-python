"""JLABROC/JSRT-MRMC compatible ROC and MRMC analysis tools."""

from .jlabroc import JLabrocResult, fit_jlabroc
from .mrmc import AnovaResult, MrmcResult, analyze_mrmc
from .io import (
    read_legacy_jlabroc_input,
    read_legacy_mrmc_input,
    read_mrmc_input,
    read_mrmc_matrix,
)

__version__ = "1.0.1"

__all__ = [
    "JLabrocResult",
    "fit_jlabroc",
    "AnovaResult",
    "MrmcResult",
    "analyze_mrmc",
    "read_legacy_jlabroc_input",
    "read_legacy_mrmc_input",
    "read_mrmc_input",
    "read_mrmc_matrix",
]
