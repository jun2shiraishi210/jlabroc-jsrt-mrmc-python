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

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jlabroc_jsrt_mrmc.io import read_legacy_jlabroc_input, read_mrmc_matrix
from jlabroc_jsrt_mrmc.jlabroc import fit_jlabroc
from jlabroc_jsrt_mrmc.mrmc import analyze_mrmc

J_TOL = {"a": 5e-7, "b": 2e-7, "auc": 2e-9}
M_TOL = {"auc": 2e-9, "mean": 2e-9, "ci": 3e-6, "anova": 2e-6, "f": 2e-7, "p": 1e-7}


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


def _run(csv_path: Path) -> int:
    out = []
    print("JLABROC/JSRT-MRMC Python archived-reference validation")
    print("Python:", sys.version.split()[0])
    print("Python executable:", sys.executable)
    print("Python compiler:", platform.python_compiler())
    print("System:", platform.system())
    print("Release:", platform.release())
    print("Version:", platform.version())
    print("Machine:", platform.machine())
    print("Platform:", platform.platform())
    print("NumPy:", np.__version__)
    print("SciPy:", scipy.__version__)
    print()

    jref = json.loads((ROOT / "validation/reference/jlabroc_cpp_reference.json").read_text())
    for name, ref in jref.items():
        p = ROOT / "validation/data/jlabroc" / name
        neg, pos = read_legacy_jlabroc_input(p)
        if ref.get("legacy_result") == "NaN":
            try:
                fit_jlabroc(neg, pos)
                ok = False
                detail = "expected ValueError but calculation returned"
            except ValueError as e:
                ok = True
                detail = f"controlled error: {e}"
            print(f"JLABROC {name}: {'PASS' if ok else 'FAIL'} ({detail})")
            out.append(["JLABROC", name, "degenerate", detail, "PASS" if ok else "FAIL"])
            continue

        r = fit_jlabroc(neg, pos)
        diffs = {k: abs(getattr(r, k) - ref[k]) for k in ("a", "b", "auc")}
        ok = all(diffs[k] <= J_TOL[k] for k in diffs)
        print(
            f"JLABROC {name}: {'PASS' if ok else 'FAIL'}  "
            f"da={diffs['a']:.3g} db={diffs['b']:.3g} dAUC={diffs['auc']:.3g}"
        )
        out.append(["JLABROC", name, "max_abs_diff", max(diffs.values()), "PASS" if ok else "FAIL"])

    mref = json.loads((ROOT / "validation/reference/mrmc_cpp_reference.json").read_text())
    for label, ref in mref.items():
        p = ROOT / "validation/data/mrmc" / ref["file"]
        data = read_mrmc_matrix(p, ref["readers"])
        r = analyze_mrmc(
            data,
            n_readers=ref["readers"],
            n_negative=ref["negative"],
            n_positive=ref["positive"],
        )
        reader_ref = np.asarray(ref["reader_auc"], dtype=float)
        d_auc = float(np.max(np.abs(r.auc_table - reader_ref)))
        d_mean = max(
            abs(r.mean_auc_system1 - ref["mean1"]),
            abs(r.mean_auc_system2 - ref["mean2"]),
            abs(r.difference - ref["difference"]),
        )
        d_ci = max(abs(r.ci_upper - ref["ci_upper"]), abs(r.ci_lower - ref["ci_lower"]))
        a = ref["anova"]
        d_anova = max(
            abs(r.anova.ss_t - a["ss_t"]),
            abs(r.anova.ss_tr - a["ss_tr"]),
            abs(r.anova.ss_tc - a["ss_tc"]),
            abs(r.anova.ss_trc - a["ss_trc"]),
            abs(r.anova.ms_t - a["ms_t"]),
            abs(r.anova.ms_tr - a["ms_tr"]),
            abs(r.anova.ms_tc - a["ms_tc"]),
            abs(r.anova.ms_trc - a["ms_trc"]),
        )
        d_f = abs(r.anova.f_value - a["f"])
        d_p = abs(r.anova.p_value - a["p"])
        df_ok = r.anova.df1 == a["df1"] and r.anova.df2 == a["df2"]
        ok = (
            d_auc <= M_TOL["auc"]
            and d_mean <= M_TOL["mean"]
            and d_ci <= M_TOL["ci"]
            and d_anova <= M_TOL["anova"]
            and d_f <= M_TOL["f"]
            and d_p <= M_TOL["p"]
            and df_ok
        )
        print(
            f"MRMC {label}: {'PASS' if ok else 'FAIL'}  maxdAUC={d_auc:.3g} "
            f"maxdmean={d_mean:.3g} maxdCI={d_ci:.3g} maxdANOVA={d_anova:.3g} "
            f"dF={d_f:.3g} dp={d_p:.3g} df={r.anova.df1},{r.anova.df2}"
        )
        out.append(
            ["MRMC", label, "max_abs_diff", max(d_auc, d_mean, d_ci, d_anova, d_f, d_p), "PASS" if ok else "FAIL"]
        )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module", "dataset", "metric", "value_or_note", "status"])
        w.writerows(out)

    failed = [x for x in out if x[-1] != "PASS"]
    print()
    print("Overall:", "PASS" if not failed else f"FAIL ({len(failed)} failed)")
    print("CSV:", csv_path)
    return 0 if not failed else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "validation" / "validation_results.csv"))
    ap.add_argument(
        "--log",
        default=None,
        help="Optional text log file. Output is still shown on screen.",
    )
    args = ap.parse_args()
    csv_path = Path(args.csv)

    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log_file:
            with redirect_stdout(_Tee(sys.stdout, log_file)):
                return _run(csv_path)
    return _run(csv_path)


if __name__ == "__main__":
    raise SystemExit(main())
