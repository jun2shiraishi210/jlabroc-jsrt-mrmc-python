"""JSRT-MRMC-compatible two-system MRMC analysis core."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.stats import f as f_dist
from scipy.stats import t as t_dist

from .jlabroc import fit_jlabroc


@dataclass(frozen=True)
class AnovaResult:
    ss_t: float
    ss_tr: float
    ss_tc: float
    ss_trc: float
    ms_t: float
    ms_tr: float
    ms_tc: float
    ms_trc: float
    f_value: float
    df1: int
    df2: int
    p_value: float


@dataclass(frozen=True)
class MrmcResult:
    auc_table: np.ndarray
    mean_auc_system1: float
    mean_auc_system2: float
    difference: float
    ci_lower: float
    ci_upper: float
    pseudo_values: np.ndarray
    anova: AnovaResult


def _pseudo_values(
    ratings: np.ndarray,
    n_readers: int,
    n_negative: int,
    n_positive: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_cases = n_negative + n_positive
    if ratings.shape != (n_cases, 2 * n_readers):
        raise ValueError(
            f"ratings must have shape ({n_cases}, {2*n_readers}), got {ratings.shape}"
        )

    pseudo = np.zeros((2, n_readers, n_cases), dtype=float)
    auc_table = np.zeros((n_readers, 2), dtype=float)

    for reader in range(n_readers):
        for treatment in range(2):
            col = treatment * n_readers + reader
            negative = ratings[:n_negative, col]
            positive = ratings[n_negative:, col]
            full_auc = fit_jlabroc(negative, positive).auc
            auc_table[reader, treatment] = full_auc

            for case in range(n_cases):
                if case < n_negative:
                    leave_negative = np.delete(negative, case)
                    leave_positive = positive
                else:
                    leave_negative = negative
                    leave_positive = np.delete(positive, case - n_negative)

                leave_auc = fit_jlabroc(leave_negative, leave_positive).auc
                pseudo[treatment, reader, case] = (
                    full_auc * n_cases - leave_auc * (n_cases - 1)
                )

    return pseudo, auc_table


def _anova_f(pseudo: np.ndarray) -> AnovaResult:
    if pseudo.ndim != 3 or pseudo.shape[0] != 2:
        raise ValueError("pseudo must have shape (2, readers, cases)")
    _, n_readers, n_cases = pseudo.shape
    if n_readers < 2 or n_cases < 2:
        raise ValueError("MRMC ANOVA requires at least two readers and two cases")

    szjk = pseudo.sum(axis=0)        # reader x case
    sizk = pseudo.sum(axis=1)        # treatment x case
    sijz = pseudo.sum(axis=2)        # treatment x reader
    sizz_v = pseudo.sum(axis=(1, 2)) # treatment
    szjz = pseudo.sum(axis=(0, 2))   # reader
    szzk = pseudo.sum(axis=(0, 1))   # case
    total = float(pseudo.sum())

    sizz = float(np.dot(sizz_v, sizz_v) / (n_readers * n_cases))
    s = total * total / (2.0 * n_readers * n_cases)
    ss_t = sizz - s

    sijz_q = float(np.sum(sijz * sijz) / n_cases)
    szjz_q = float(np.sum(szjz * szjz) / (2.0 * n_cases))
    ss_tr = sijz_q - szjz_q - sizz + s

    sizk_q = float(np.sum(sizk * sizk) / n_readers)
    szzk_q = float(np.sum(szzk * szzk) / (2.0 * n_readers))
    ss_tc = sizk_q - szzk_q - sizz + s

    total_q = float(np.sum(pseudo * pseudo))
    szjk_q = float(np.sum(szjk * szjk) / 2.0)
    ss_trc = total_q - szjk_q - sizk_q - sijz_q + szzk_q + szjz_q + sizz - s

    ms_t = ss_t
    ms_tr = ss_tr / (n_readers - 1)
    ms_tc = ss_tc / (n_cases - 1)
    ms_trc = ss_trc / ((n_cases - 1) * (n_readers - 1))

    if ms_trc == 0.0:
        raise ValueError("degenerate MRMC ANOVA: residual mean square is zero")

    if (ms_tr / ms_trc) <= 1.0 and (ms_tc / ms_trc) <= 1.0:
        f_value = ms_t / ms_trc
        df2 = (n_readers - 1) * (n_cases - 1)
    else:
        denominator = ms_tr + ms_tc - ms_trc
        if denominator <= 0.0:
            raise ValueError("degenerate MRMC ANOVA denominator")
        f_value = ms_t / denominator
        df_float = denominator**2 / (
            (ms_tc**2) / (n_cases - 1)
            + (ms_tr**2) / (n_readers - 1)
            - (ms_trc**2) / ((n_readers - 1) * (n_cases - 1))
        )
        # Legacy JSRT-MRMC behavior. This integerization rule is retained
        # intentionally for numerical compatibility with the validated method.
        df2 = int(df_float + 0.4444)
        if df2 < 1:
            raise ValueError("computed denominator degrees of freedom < 1")

    p_value = float(f_dist.sf(f_value, 1, df2))

    return AnovaResult(
        ss_t=float(ss_t), ss_tr=float(ss_tr), ss_tc=float(ss_tc), ss_trc=float(ss_trc),
        ms_t=float(ms_t), ms_tr=float(ms_tr), ms_tc=float(ms_tc), ms_trc=float(ms_trc),
        f_value=float(f_value), df1=1, df2=int(df2), p_value=p_value,
    )


def analyze_mrmc(
    ratings: np.ndarray,
    *,
    n_readers: int,
    n_negative: int,
    n_positive: int,
    alpha: float = 0.05,
) -> MrmcResult:
    """Analyze two systems using the legacy JSRT-MRMC workflow.

    Rows are cases (negative rows first, then positive rows). Columns are the
    readers for system 1 followed by the same readers for system 2.
    """
    data = np.asarray(ratings, dtype=float)
    if not np.all(np.isfinite(data)):
        raise ValueError("ratings must contain finite numeric values")
    if n_readers < 2:
        raise ValueError("at least two readers are required")
    if n_negative < 2 or n_positive < 2:
        raise ValueError("at least two negative and two positive cases are required")

    pseudo, auc_table = _pseudo_values(data, n_readers, n_negative, n_positive)
    differences = auc_table[:, 0] - auc_table[:, 1]
    mean_difference = float(np.mean(differences))
    sd = float(np.std(differences, ddof=1))
    tcrit = float(t_dist.ppf(1.0 - alpha / 2.0, n_readers - 1))
    half_width = tcrit * sd / math.sqrt(n_readers)
    ci_lower = mean_difference - half_width
    ci_upper = mean_difference + half_width

    anova = _anova_f(pseudo)
    means = np.mean(auc_table, axis=0)

    return MrmcResult(
        auc_table=auc_table,
        mean_auc_system1=float(means[0]),
        mean_auc_system2=float(means[1]),
        difference=mean_difference,
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        pseudo_values=pseudo,
        anova=anova,
    )
