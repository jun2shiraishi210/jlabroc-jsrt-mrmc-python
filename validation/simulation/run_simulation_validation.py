from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jlabroc_jsrt_mrmc.io import read_legacy_jlabroc_input, read_mrmc_matrix
from jlabroc_jsrt_mrmc.jlabroc import fit_jlabroc
from jlabroc_jsrt_mrmc.mrmc import analyze_mrmc

SIM = ROOT / "validation" / "simulation"

J_TOL = {"a": 5e-8, "b": 5e-8, "auc": 2e-9}
M_TOL = {
    "auc": 2e-9,
    "mean": 2e-9,
    "difference": 2e-9,
    "ci": 5e-6,
    "anova": 2e-6,
    "f": 5e-6,
    "p": 1e-7,
    "pseudo": 3e-7,
}


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text: str) -> int:
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def _env_lines() -> list[str]:
    return [
        f"Python: {sys.version.split()[0]}",
        f"Python executable: {sys.executable}",
        f"Python compiler: {platform.python_compiler()}",
        f"System: {platform.system()}",
        f"Release: {platform.release()}",
        f"Version: {platform.version()}",
        f"Machine: {platform.machine()}",
        f"Platform: {platform.platform()}",
        f"NumPy: {np.__version__}",
        f"SciPy: {scipy.__version__}",
    ]


def _run(detail_csv: Path, summary_csv: Path) -> int:
    print("JLABROC/JSRT-MRMC Python systematic simulation validation")
    for line in _env_lines():
        print(line)
    print()

    detail_rows: list[list[object]] = []
    summary_rows: list[list[object]] = []
    failed = 0

    jref = json.loads((SIM / "reference" / "jlabroc_sim_cpp_reference.json").read_text(encoding="utf-8"))
    j_max = {"a": (0.0, ""), "b": (0.0, ""), "auc": (0.0, "")}
    j_pass = 0
    j_controlled = 0
    for sid, ref in jref.items():
        p = SIM / "data" / "jlabroc" / ref["file"]
        neg, pos = read_legacy_jlabroc_input(p)
        if ref["status"] != "ok":
            try:
                fit_jlabroc(neg, pos)
                ok = False
                note = "expected controlled ValueError but calculation returned"
            except ValueError as exc:
                ok = True
                note = f"controlled error: {exc}"
            print(f"JLABROC {sid}: {'PASS' if ok else 'FAIL'} ({note})")
            detail_rows.append(["JLABROC", sid, ref["kind"], "controlled_error", "", "", note, "PASS" if ok else "FAIL"])
            if ok:
                j_controlled += 1
            else:
                failed += 1
            continue

        r = fit_jlabroc(neg, pos)
        da = abs(r.a - ref["a"])
        db = abs(r.b - ref["b"])
        dauc = abs(r.auc - ref["auc"])
        diffs = {"a": da, "b": db, "auc": dauc}
        for k, d in diffs.items():
            if d > j_max[k][0]:
                j_max[k] = (d, sid)
        ok = da <= J_TOL["a"] and db <= J_TOL["b"] and dauc <= J_TOL["auc"]
        print(f"JLABROC {sid}: {'PASS' if ok else 'FAIL'}  da={da:.3g} db={db:.3g} dAUC={dauc:.3g}")
        for metric, value, tol in (("a", da, J_TOL["a"]), ("b", db, J_TOL["b"]), ("auc", dauc, J_TOL["auc"])):
            detail_rows.append(["JLABROC", sid, ref["kind"], metric, value, tol, "", "PASS" if value <= tol else "FAIL"])
        if ok:
            j_pass += 1
        else:
            failed += 1

    print()
    print(
        "JLABROC summary: "
        f"regular/stress PASS={j_pass}, controlled-degenerate PASS={j_controlled}, "
        f"max da={j_max['a'][0]:.3g} ({j_max['a'][1]}), "
        f"max db={j_max['b'][0]:.3g} ({j_max['b'][1]}), "
        f"max dAUC={j_max['auc'][0]:.3g} ({j_max['auc'][1]})"
    )
    summary_rows.extend([
        ["JLABROC", "a", j_max["a"][0], J_TOL["a"], j_max["a"][1], "PASS" if j_max["a"][0] <= J_TOL["a"] else "FAIL"],
        ["JLABROC", "b", j_max["b"][0], J_TOL["b"], j_max["b"][1], "PASS" if j_max["b"][0] <= J_TOL["b"] else "FAIL"],
        ["JLABROC", "auc", j_max["auc"][0], J_TOL["auc"], j_max["auc"][1], "PASS" if j_max["auc"][0] <= J_TOL["auc"] else "FAIL"],
    ])

    mref = json.loads((SIM / "reference" / "mrmc_sim_cpp_reference.json").read_text(encoding="utf-8"))
    m_max = {k: (0.0, "") for k in ("auc", "mean", "difference", "ci", "anova", "f", "p", "pseudo")}
    m_pass = 0
    for sid, ref in mref.items():
        p = SIM / "data" / "mrmc" / ref["file"]
        data = read_mrmc_matrix(p, ref["readers"])
        r = analyze_mrmc(data, n_readers=ref["readers"], n_negative=ref["negative"], n_positive=ref["positive"])
        d_auc = float(np.max(np.abs(r.auc_table - np.asarray(ref["reader_auc"], dtype=float))))
        d_mean = max(abs(r.mean_auc_system1 - ref["mean1"]), abs(r.mean_auc_system2 - ref["mean2"]))
        d_difference = abs(r.difference - ref["difference"])
        d_ci = max(abs(r.ci_lower - ref["ci_lower"]), abs(r.ci_upper - ref["ci_upper"]))
        anova_diffs = []
        mapping = {
            "t": ("ss_t", "ms_t"), "tr": ("ss_tr", "ms_tr"),
            "tc": ("ss_tc", "ms_tc"), "trc": ("ss_trc", "ms_trc"),
        }
        for q, attrs in mapping.items():
            anova_diffs.append(abs(getattr(r.anova, attrs[0]) - ref["anova"][q]["ss"]))
            anova_diffs.append(abs(getattr(r.anova, attrs[1]) - ref["anova"][q]["ms"]))
        d_anova = max(anova_diffs)
        d_f = abs(r.anova.f_value - ref["f"])
        d_p = abs(r.anova.p_value - ref["p"])
        d_pseudo = float(np.max(np.abs(r.pseudo_values - np.asarray(ref["pseudo_values"], dtype=float))))
        df_ok = r.anova.df1 == int(ref["df1"]) and r.anova.df2 == int(ref["df2"])
        diffs = {
            "auc": d_auc, "mean": d_mean, "difference": d_difference, "ci": d_ci,
            "anova": d_anova, "f": d_f, "p": d_p, "pseudo": d_pseudo,
        }
        for k, d in diffs.items():
            if d > m_max[k][0]:
                m_max[k] = (d, sid)
        ok = df_ok and all(diffs[k] <= M_TOL[k] for k in diffs)
        print(
            f"MRMC {sid}: {'PASS' if ok else 'FAIL'}  maxdAUC={d_auc:.3g} maxdMean={d_mean:.3g} "
            f"dDiff={d_difference:.3g} maxdCI={d_ci:.3g} maxdANOVA={d_anova:.3g} "
            f"dF={d_f:.3g} dP={d_p:.3g} maxdPseudo={d_pseudo:.3g} df={r.anova.df1},{r.anova.df2}"
        )
        for metric, value in diffs.items():
            detail_rows.append(["MRMC", sid, "synthetic", metric, value, M_TOL[metric], "", "PASS" if value <= M_TOL[metric] else "FAIL"])
        detail_rows.append(["MRMC", sid, "synthetic", "df", f"{r.anova.df1},{r.anova.df2}", f"{int(ref['df1'])},{int(ref['df2'])}", "", "PASS" if df_ok else "FAIL"])
        if ok:
            m_pass += 1
        else:
            failed += 1

    print()
    print(f"MRMC summary: datasets PASS={m_pass}/{len(mref)}")
    for metric in ("auc", "mean", "difference", "ci", "anova", "f", "p", "pseudo"):
        value, sid = m_max[metric]
        print(f"  max {metric} diff={value:.3g} ({sid}), tolerance={M_TOL[metric]:.3g}")
        summary_rows.append(["MRMC", metric, value, M_TOL[metric], sid, "PASS" if value <= M_TOL[metric] else "FAIL"])

    detail_csv.parent.mkdir(parents=True, exist_ok=True)
    with detail_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module", "dataset", "dataset_kind", "metric", "abs_diff_or_value", "tolerance_or_reference", "note", "status"])
        w.writerows(detail_rows)
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module", "metric", "max_abs_diff", "tolerance", "dataset_at_max", "status"])
        w.writerows(summary_rows)

    print()
    print("Overall:", "PASS" if failed == 0 else f"FAIL ({failed} datasets failed)")
    print("Detail CSV:", detail_csv)
    print("Summary CSV:", summary_csv)
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail-csv", default=str(SIM / "simulation_validation_details.csv"))
    ap.add_argument("--summary-csv", default=str(SIM / "simulation_validation_summary.csv"))
    ap.add_argument("--log", default=None, help="Optional UTF-8 text log file; output is also shown on screen.")
    args = ap.parse_args()
    detail_csv = Path(args.detail_csv)
    summary_csv = Path(args.summary_csv)
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log_file:
            with redirect_stdout(_Tee(sys.stdout, log_file)):
                return _run(detail_csv, summary_csv)
    return _run(detail_csv, summary_csv)


if __name__ == "__main__":
    raise SystemExit(main())
