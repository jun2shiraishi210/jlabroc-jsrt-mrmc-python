"""Input helpers for legacy JLABROC/JSRT-MRMC text formats."""

from __future__ import annotations

from pathlib import Path
import numpy as np


def read_legacy_jlabroc_input(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Read the legacy ROCKIT/JLABROC single-reader input format.

    The first four tokens are treated as legacy header fields. Negative ratings
    follow until '*', then positive ratings follow until the second '*'.
    """
    tokens = Path(path).read_text(errors="replace").split()
    if len(tokens) < 7:
        raise ValueError("input file is too short")
    values = tokens[4:]
    try:
        first = values.index("*")
        second = values.index("*", first + 1)
    except ValueError as exc:
        raise ValueError("legacy input must contain two '*' separators") from exc

    negative = np.asarray([float(x) for x in values[:first]], dtype=float)
    positive = np.asarray([float(x) for x in values[first + 1 : second]], dtype=float)
    return negative, positive


def read_mrmc_matrix(path: str | Path, n_readers: int) -> np.ndarray:
    """Read a two-system MRMC rating matrix.

    Expected column order is system 1 readers followed by system 2 readers,
    matching the legacy JSRT-MRMC implementation.
    """
    data = np.loadtxt(path, dtype=float)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    expected = 2 * int(n_readers)
    if data.shape[1] != expected:
        raise ValueError(f"expected {expected} columns, found {data.shape[1]}")
    return data
