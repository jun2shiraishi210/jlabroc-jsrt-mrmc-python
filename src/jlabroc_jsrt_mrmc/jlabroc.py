"""JLABROC-compatible binormal ROC fitting core.

This module implements the published JLABROC method while preserving
selected legacy behaviors that are required for numerical compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class JLabrocResult:
    a: float
    b: float
    auc: float
    n_negative: int
    n_positive: int
    n_fit_points: int


def _legacy_descending_pairs(ratings: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Reproduce the ordering behavior of legacy SortData(..., LorS=1).

    This is deliberately not replaced by a stable modern sort because the
    legacy in-place selection-like algorithm can change the order of tied
    ratings, and that order affects the sequence of ROC operating points.

    Python lists are used for the swap loop rather than repeated NumPy row
    indexing.  The swap sequence is identical to the legacy algorithm, but
    this is substantially faster during MRMC jackknife calculations.
    """
    r = [float(x) for x in ratings]
    lab = [float(x) for x in labels]
    n = len(r)
    for m in range(n - 1):
        for l in range(m, n):
            if r[m] < r[l]:
                r[m], r[l] = r[l], r[m]
                lab[m], lab[l] = lab[l], lab[m]
    return np.column_stack((r, lab))


def fit_jlabroc(
    negative: Iterable[float],
    positive: Iterable[float],
    *,
    legacy_tie_order: bool = True,
) -> JLabrocResult:
    """Fit the JLABROC binormal model to continuous ratings.

    The implementation follows the categorization-free JLABROC procedure:
    construct sequential empirical ROC points, omit boundary points containing
    0 or 1, transform FPF/TPF to normal-deviate coordinates, fit y=a+b*x by
    least squares, and compute AUC = Phi(a/sqrt(1+b^2)).

    Parameters
    ----------
    negative, positive:
        Continuous rating values for actually negative and positive cases.
    legacy_tie_order:
        If True (default), reproduce the legacy SortData tie behavior
        for numerical compatibility with the legacy implementation.
    """
    neg = np.asarray(list(negative), dtype=float)
    pos = np.asarray(list(positive), dtype=float)

    if neg.ndim != 1 or pos.ndim != 1:
        raise ValueError("negative and positive must be one-dimensional")
    if neg.size < 2 or pos.size < 2:
        raise ValueError("at least two negative and two positive cases are required")
    if not np.all(np.isfinite(neg)) or not np.all(np.isfinite(pos)):
        raise ValueError("ratings must be finite numeric values")

    ratings = np.concatenate((neg, pos))
    labels = np.concatenate((np.ones(neg.size), np.full(pos.size, 2.0)))

    if legacy_tie_order:
        ordered = _legacy_descending_pairs(ratings, labels)
    else:
        # Modern deterministic ordering. This is intentionally separate from
        # the compatibility path and is not yet the default research method.
        idx = np.argsort(-ratings, kind="stable")
        ordered = np.column_stack((ratings[idx], labels[idx]))

    false_positives = np.cumsum(ordered[:, 1] == 1.0)
    true_positives = np.cumsum(ordered[:, 1] != 1.0)
    fpf = false_positives / float(neg.size)
    tpf = true_positives / float(pos.size)

    keep = (fpf > 0.0) & (fpf < 1.0) & (tpf > 0.0) & (tpf < 1.0)
    x = norm.ppf(fpf[keep])
    y = norm.ppf(tpf[keep])
    n = x.size
    if n < 2:
        raise ValueError("insufficient non-boundary ROC points for binormal fitting")

    a00 = float(n)
    a01 = float(np.sum(x))
    a02 = float(np.sum(y))
    a11 = float(np.dot(x, x))
    a12 = float(np.dot(x, y))
    denominator = a00 * a11 - a01 * a01
    if abs(denominator) <= np.finfo(float).eps:
        raise ValueError("degenerate ROC points: least-squares fit is undefined")

    a = (a02 * a11 - a01 * a12) / denominator
    b = (a00 * a12 - a01 * a02) / denominator
    auc = float(norm.cdf(a / math.sqrt(1.0 + b * b)))

    return JLabrocResult(
        a=float(a),
        b=float(b),
        auc=auc,
        n_negative=int(neg.size),
        n_positive=int(pos.size),
        n_fit_points=int(n),
    )
