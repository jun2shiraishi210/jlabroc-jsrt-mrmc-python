"""Command-line interface for JLABROC/JSRT-MRMC Python."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .io import read_legacy_jlabroc_input, read_mrmc_matrix
from .jlabroc import fit_jlabroc
from .mrmc import analyze_mrmc


def _fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def _run_jlabroc(args: argparse.Namespace) -> int:
    path = Path(args.input)
    negative, positive = read_legacy_jlabroc_input(path)
    result = fit_jlabroc(negative, positive)

    print("JLABROC-compatible analysis (Python)")
    print(f"Input file : {path}")
    print(f"Negative N : {result.n_negative}")
    print(f"Positive N : {result.n_positive}")
    print(f"Fit points : {result.n_fit_points}")
    print(f"a          : {_fmt(result.a)}")
    print(f"b          : {_fmt(result.b)}")
    print(f"AUC        : {_fmt(result.auc)}")
    return 0


def _run_mrmc(args: argparse.Namespace) -> int:
    path = Path(args.input)
    ratings = read_mrmc_matrix(path, n_readers=args.readers)
    result = analyze_mrmc(
        ratings,
        n_readers=args.readers,
        n_negative=args.negative,
        n_positive=args.positive,
    )

    print("JSRT-MRMC-compatible analysis (Python)")
    print(f"Input file : {path}")
    print(f"Readers    : {args.readers}")
    print(f"Negative N : {args.negative}")
    print(f"Positive N : {args.positive}")
    print()
    print("Reader AUCs")
    print("Reader   System 1   System 2   Difference")
    for i, row in enumerate(result.auc_table, start=1):
        diff = row[0] - row[1]
        print(f"{i:>6}   {row[0]:>8.4f}   {row[1]:>8.4f}   {diff:>10.4f}")
    print()
    print(f"Mean AUC System 1 : {result.mean_auc_system1:.4f}")
    print(f"Mean AUC System 2 : {result.mean_auc_system2:.4f}")
    print(f"Difference        : {result.difference:.4f}")
    print(f"95% CI            : ({result.ci_lower:.4f}, {result.ci_upper:.4f})")
    print()
    print("ANOVA")
    print(f"F                 : {result.anova.f_value:.4f}")
    print(f"df                : ({result.anova.df1}, {result.anova.df2})")
    print(f"p                 : {result.anova.p_value:.6f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jlabroc-jsrt-mrmc",
        description="JLABROC/JSRT-MRMC-compatible ROC and MRMC analyses.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_j = sub.add_parser("jlabroc", help="Run single-reader JLABROC-compatible ROC analysis")
    p_j.add_argument("input", help="Legacy ROCKIT/JLABROC input text file")
    p_j.set_defaults(func=_run_jlabroc)

    p_m = sub.add_parser("mrmc", help="Run two-system JSRT-MRMC-compatible analysis")
    p_m.add_argument("input", help="MRMC rating matrix text file")
    p_m.add_argument("--readers", type=int, required=True, help="Number of readers")
    p_m.add_argument("--negative", type=int, required=True, help="Number of negative cases")
    p_m.add_argument("--positive", type=int, required=True, help="Number of positive cases")
    p_m.set_defaults(func=_run_mrmc)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
