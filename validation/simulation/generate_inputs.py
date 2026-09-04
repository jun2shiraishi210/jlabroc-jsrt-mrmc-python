from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "validation" / "simulation"
JDIR = SIM / "data" / "jlabroc"
MDIR = SIM / "data" / "mrmc"


def _ab_to_positive_distribution(target_auc: float, b: float) -> tuple[float, float, float]:
    a = math.sqrt(1.0 + b * b) * float(norm.ppf(target_auc))
    sigma_pos = 1.0 / b
    mu_pos = a * sigma_pos
    return a, mu_pos, sigma_pos


def _write_jlabroc(path: Path, neg: np.ndarray, pos: np.ndarray) -> None:
    lines = ["SIM", "KIT", '"Continuous"', "CLL"]
    lines.extend(f"{x:.12g}" for x in neg)
    lines.append("*")
    lines.extend(f"{x:.12g}" for x in pos)
    lines.append("*")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _write_mrmc(path: Path, matrix: np.ndarray) -> None:
    np.savetxt(path, matrix, fmt="%.12g", delimiter="\t")


def generate_jlabroc() -> list[dict]:
    JDIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    base_seed = 2026090400
    case_configs = [(25,25), (50,50), (100,100), (100,25)]
    aucs = [0.60, 0.70, 0.80, 0.90]
    bs = [0.75, 1.00, 1.25]
    idx = 0
    for nneg, npos in case_configs:
        for auc in aucs:
            for b in bs:
                seed = base_seed + idx
                rng = np.random.default_rng(seed)
                a_target, mu_pos, sigma_pos = _ab_to_positive_distribution(auc, b)
                neg = rng.normal(0.0, 1.0, nneg)
                pos = rng.normal(mu_pos, sigma_pos, npos)
                name = f"J_grid_N{nneg:03d}_P{npos:03d}_A{int(round(auc*100)):03d}_B{int(round(b*100)):03d}.txt"
                _write_jlabroc(JDIR / name, neg, pos)
                manifest.append({
                    "id": name[:-4], "file": name, "kind": "grid", "seed": seed,
                    "negative": nneg, "positive": npos, "target_auc": auc, "target_b": b,
                    "target_a": a_target, "transform": "none",
                })
                idx += 1

    stress_specs = [
        ("J_stress_ties_1dp", 50, 50, 0.75, 1.0, 2026090501, "round_1dp"),
        ("J_stress_ties_integer", 50, 50, 0.75, 1.0, 2026090502, "round_integer"),
        ("J_stress_small_5_5", 5, 5, 0.75, 1.0, 2026090503, "none"),
        ("J_stress_small_10_10", 10, 10, 0.75, 1.0, 2026090504, "none"),
        ("J_stress_unequal_N020_P080", 20, 80, 0.75, 1.0, 2026090505, "none"),
        ("J_stress_unequal_N080_P020", 80, 20, 0.75, 1.0, 2026090506, "none"),
        ("J_stress_auc055", 50, 50, 0.55, 1.0, 2026090507, "none"),
        ("J_stress_auc098", 50, 50, 0.98, 1.0, 2026090508, "none"),
        ("J_stress_reverse_auc040", 50, 50, 0.40, 1.0, 2026090509, "none"),
    ]
    for sid, nneg, npos, auc, b, seed, transform in stress_specs:
        rng = np.random.default_rng(seed)
        a_target, mu_pos, sigma_pos = _ab_to_positive_distribution(auc, b)
        neg = rng.normal(0.0, 1.0, nneg)
        pos = rng.normal(mu_pos, sigma_pos, npos)
        if transform == "round_1dp":
            neg = np.round(neg, 1); pos = np.round(pos, 1)
        elif transform == "round_integer":
            neg = np.round(neg, 0); pos = np.round(pos, 0)
        name = sid + ".txt"
        _write_jlabroc(JDIR / name, neg, pos)
        manifest.append({
            "id": sid, "file": name, "kind": "stress", "seed": seed,
            "negative": nneg, "positive": npos, "target_auc": auc, "target_b": b,
            "target_a": a_target, "transform": transform,
        })

    # Explicit degenerate conditions: expected to be non-fittable.
    degens = [
        ("J_degenerate_all_tied", np.zeros(20), np.zeros(20), "all ratings identical"),
        ("J_degenerate_perfect_separation", np.linspace(-2,-1,20), np.linspace(1,2,20), "perfect separation"),
    ]
    for sid, neg, pos, note in degens:
        name = sid + ".txt"
        _write_jlabroc(JDIR / name, neg, pos)
        manifest.append({
            "id": sid, "file": name, "kind": "degenerate", "seed": None,
            "negative": int(len(neg)), "positive": int(len(pos)), "target_auc": None,
            "target_b": None, "target_a": None, "transform": note,
        })
    return manifest


def _make_mrmc_matrix(
    *, readers: int, nneg: int, npos: int, auc1: float, auc2: float,
    seed: int, rho_case: float = 0.35, reader_sd: float = 0.12,
    tr_reader_sd: float = 0.06,
) -> np.ndarray:
    """Create deterministic paired synthetic MRMC ratings.

    This is an implementation-validation generator, not a reproduction of the
    Roe-Metz simulator. Shared case latent variables induce correlation across
    readers and systems, and reader / treatment-reader effects diversify AUCs.
    """
    rng = np.random.default_rng(seed)
    shared_neg = rng.normal(size=nneg)
    shared_pos = rng.normal(size=npos)
    reader_skill = rng.normal(0.0, reader_sd, size=readers)
    tr_reader = rng.normal(0.0, tr_reader_sd, size=(2, readers))
    mu = [math.sqrt(2.0) * float(norm.ppf(auc1)), math.sqrt(2.0) * float(norm.ppf(auc2))]
    sr = math.sqrt(rho_case)
    si = math.sqrt(1.0 - rho_case)
    systems = []
    for s in range(2):
        cols = []
        for r in range(readers):
            neg = sr * shared_neg + si * rng.normal(size=nneg)
            pos = mu[s] + reader_skill[r] + tr_reader[s, r] + sr * shared_pos + si * rng.normal(size=npos)
            cols.append(np.concatenate([neg, pos]))
        systems.append(np.column_stack(cols))
    return np.column_stack(systems)


def _mean_same_reader_cross_system_corr(matrix: np.ndarray, readers: int, nneg: int, npos: int) -> tuple[float, float]:
    """Mean Pearson correlation between systems for the same reader.

    Correlations are computed separately within negative and positive cases.
    These empirical values document the realized paired-case dependence in
    each finite synthetic dataset; they are not used by the analysis itself.
    """
    neg_corrs: list[float] = []
    pos_corrs: list[float] = []
    for r in range(readers):
        s1 = matrix[:, r]
        s2 = matrix[:, readers + r]
        neg_corrs.append(float(np.corrcoef(s1[:nneg], s2[:nneg])[0, 1]))
        pos_corrs.append(float(np.corrcoef(s1[nneg:nneg+npos], s2[nneg:nneg+npos])[0, 1]))
    return float(np.mean(neg_corrs)), float(np.mean(pos_corrs))


def generate_mrmc() -> list[dict]:
    """Generate MRMC implementation-equivalence stress datasets.

    The parameters are deliberately varied over broad standardized stress-test
    levels rather than calibrated to a clinical population. The shared-case
    fraction is 0.0, 0.5, or 0.9 (absent, intermediate, or strong paired-case
    dependence). Reader and treatment-reader SDs are 0.0, 0.2, or 0.4 on a
    latent rating scale whose independent residual SD is 1.0 (0%, 20%, or
    40% of residual SD). The full 3 x 3 x 3 grid prevents equivalence claims
    from depending on a single arbitrary variance/correlation setting. The
    """
    MDIR.mkdir(parents=True, exist_ok=True)
    # Remove existing MRMC inputs when regenerating in-place.
    for old in MDIR.glob("*.txt"):
        old.unlink()

    manifest: list[dict] = []
    rho_levels = [0.00, 0.50, 0.90]
    reader_sd_levels = [0.00, 0.20, 0.40]
    tr_sd_levels = [0.00, 0.20, 0.40]

    # Factorial variance/correlation stress grid: 27 datasets.
    idx = 0
    for rho in rho_levels:
        for reader_sd in reader_sd_levels:
            for tr_sd in tr_sd_levels:
                idx += 1
                seed = 2026090700 + idx
                sid = (
                    f"MFG{idx:02d}_R5_N50_P50_A080_A076_"
                    f"C{int(round(rho*100)):02d}_R{int(round(reader_sd*100)):02d}_TR{int(round(tr_sd*100)):02d}"
                )
                mat = _make_mrmc_matrix(
                    readers=5, nneg=50, npos=50, auc1=0.80, auc2=0.76,
                    seed=seed, rho_case=rho, reader_sd=reader_sd,
                    tr_reader_sd=tr_sd,
                )
                neg_corr, pos_corr = _mean_same_reader_cross_system_corr(mat, 5, 50, 50)
                name = sid + ".txt"
                _write_mrmc(MDIR / name, mat)
                manifest.append({
                    "id": sid, "file": name, "kind": "factorial_variance_correlation_grid",
                    "seed": seed, "readers": 5, "negative": 50, "positive": 50,
                    "target_auc_system1": 0.80, "target_auc_system2": 0.76,
                    "rho_case": rho, "reader_sd": reader_sd,
                    "treatment_reader_sd": tr_sd,
                    "empirical_same_reader_corr_negative": neg_corr,
                    "empirical_same_reader_corr_positive": pos_corr,
                    "parameter_basis": "standardized implementation-stress grid; not clinical variance estimates",
                })

    # Additional design/AUC stress cases: 8 datasets.
    stress_specs = [
        # id, R, N, P, AUC1, AUC2, seed, rho, reader_sd, tr_sd
        ("MS01_R3_N20_P20_A070_A066", 3,20,20,0.70,0.66,2026090801,0.00,0.00,0.00),
        ("MS02_R3_N50_P50_A085_A081", 3,50,50,0.85,0.81,2026090802,0.90,0.40,0.40),
        ("MS03_R5_N20_P80_A075_A071", 5,20,80,0.75,0.71,2026090803,0.50,0.20,0.20),
        ("MS04_R5_N80_P20_A075_A071", 5,80,20,0.75,0.71,2026090804,0.50,0.20,0.20),
        ("MS05_R5_N50_P50_A090_A086", 5,50,50,0.90,0.86,2026090805,0.00,0.40,0.00),
        ("MS06_R8_N30_P30_A070_A070", 8,30,30,0.70,0.70,2026090806,0.90,0.00,0.40),
        ("MS07_R8_N50_P50_A095_A091", 8,50,50,0.95,0.91,2026090607,0.35,0.12,0.06),
        ("MS08_R6_N40_P40_A060_A056", 6,40,40,0.60,0.56,2026090808,0.00,0.20,0.20),
    ]
    for sid, readers, nneg, npos, auc1, auc2, seed, rho, reader_sd, tr_sd in stress_specs:
        mat = _make_mrmc_matrix(
            readers=readers, nneg=nneg, npos=npos, auc1=auc1, auc2=auc2,
            seed=seed, rho_case=rho, reader_sd=reader_sd,
            tr_reader_sd=tr_sd,
        )
        neg_corr, pos_corr = _mean_same_reader_cross_system_corr(mat, readers, nneg, npos)
        name = sid + ".txt"
        _write_mrmc(MDIR / name, mat)
        manifest.append({
            "id": sid, "file": name, "kind": "design_auc_stress",
            "seed": seed, "readers": readers, "negative": nneg, "positive": npos,
            "target_auc_system1": auc1, "target_auc_system2": auc2,
            "rho_case": rho, "reader_sd": reader_sd,
            "treatment_reader_sd": tr_sd,
            "empirical_same_reader_corr_negative": neg_corr,
            "empirical_same_reader_corr_positive": pos_corr,
            "parameter_basis": "design/AUC implementation stress; not clinical variance estimates",
        })
    return manifest


def main() -> None:
    j=generate_jlabroc(); m=generate_mrmc()
    manifest={
        "version":"1.0.0",
        "purpose":"Deterministic synthetic datasets for implementation-equivalence and stress validation.",
        "jlabroc":j,"mrmc":m,
    }
    (SIM/'simulation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f"Generated {len(j)} JLABROC datasets and {len(m)} MRMC datasets")


if __name__ == '__main__':
    main()
