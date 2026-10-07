"""Input helpers for legacy JLABROC/JSRT-MRMC text formats."""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np


_READER_RE = re.compile(r"^\s*Reader\s*0*(\d+)\s*$", re.IGNORECASE)


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
    matching the validated JSRT-MRMC calculation core.
    """
    data = np.loadtxt(path, dtype=float)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    expected = 2 * int(n_readers)
    if data.shape[1] != expected:
        raise ValueError(f"expected {expected} columns, found {data.shape[1]}")
    return data


def _is_star_separator(line: str) -> bool:
    """Return True for a line consisting only of one or more '*' tokens."""
    fields = line.strip().split()
    return bool(fields) and all(field == "*" for field in fields)


def _numeric_pair(line: str) -> tuple[float, float] | None:
    """Parse exactly two finite numeric values, or return None."""
    fields = line.strip().split()
    if len(fields) != 2:
        return None
    try:
        first, second = float(fields[0]), float(fields[1])
    except ValueError:
        return None
    if not (np.isfinite(first) and np.isfinite(second)):
        raise ValueError("MRMC ratings must contain finite numeric values")
    return first, second


def _pairs_from_region(
    lines: list[str],
    *,
    reader_number: int,
    region_name: str,
    allow_leading_metadata: bool,
) -> list[tuple[float, float]]:
    """Extract two-column numeric rows from one legacy reader region."""
    pairs: list[tuple[float, float]] = []
    started = False
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pair = _numeric_pair(raw)
        if pair is not None:
            pairs.append(pair)
            started = True
            continue
        if allow_leading_metadata and not started:
            # Reader 1 in the original format may contain lines such as
            # '"High" "Low"' and 'L L' before its first numeric rating row.
            continue
        raise ValueError(
            f"unexpected non-numeric line in Reader{reader_number} {region_name} ratings: {stripped!r}"
        )
    return pairs


def read_legacy_mrmc_input(
    path: str | Path,
    *,
    n_readers: int,
    n_negative: int,
    n_positive: int,
) -> np.ndarray:
    """Read the original two-system JSRT-MRMC reader-block text format.

    Each reader block contains two rating columns (system 1, system 2), an
    actually-negative section, a star separator line, an actually-positive
    section, and a second star separator line.  The canonical legacy program
    writes ``* *`` for a two-system separator.  For robustness, a line
    containing a single ``*`` is also accepted; this recovers the intended
    two-column block structure from historical sample files that used a single
    star even though the original executable could misparse those files.

    The returned matrix has rows ordered as negative cases followed by positive
    cases, and columns ordered as all system-1 readers followed by all system-2
    readers, which is the layout consumed by :func:`analyze_mrmc`.
    """
    if n_readers < 1:
        raise ValueError("n_readers must be positive")
    if n_negative < 1 or n_positive < 1:
        raise ValueError("n_negative and n_positive must be positive")

    lines = Path(path).read_text(errors="replace").splitlines()
    reader_headers: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        match = _READER_RE.match(line)
        if match:
            reader_headers.append((index, int(match.group(1))))

    if len(reader_headers) != n_readers:
        raise ValueError(
            f"expected {n_readers} Reader blocks, found {len(reader_headers)}"
        )

    expected_numbers = list(range(1, n_readers + 1))
    actual_numbers = [number for _, number in reader_headers]
    if actual_numbers != expected_numbers:
        raise ValueError(
            f"Reader blocks must be numbered 1..{n_readers}; found {actual_numbers}"
        )

    n_cases = n_negative + n_positive
    ratings = np.empty((n_cases, 2 * n_readers), dtype=float)

    for reader_index, (start, reader_number) in enumerate(reader_headers):
        end = (
            reader_headers[reader_index + 1][0]
            if reader_index + 1 < len(reader_headers)
            else len(lines)
        )
        block = lines[start + 1 : end]
        separators = [i for i, line in enumerate(block) if _is_star_separator(line)]
        if len(separators) != 2:
            raise ValueError(
                f"Reader{reader_number} must contain two star separator lines; found {len(separators)}"
            )

        first_sep, second_sep = separators
        negative_pairs = _pairs_from_region(
            block[:first_sep],
            reader_number=reader_number,
            region_name="negative",
            allow_leading_metadata=True,
        )
        positive_pairs = _pairs_from_region(
            block[first_sep + 1 : second_sep],
            reader_number=reader_number,
            region_name="positive",
            allow_leading_metadata=False,
        )

        trailing = [
            line.strip()
            for line in block[second_sep + 1 :]
            if line.strip() and not line.strip().startswith("#")
        ]
        if trailing:
            raise ValueError(
                f"unexpected content after Reader{reader_number} second separator: {trailing[0]!r}"
            )

        if len(negative_pairs) != n_negative:
            raise ValueError(
                f"Reader{reader_number}: expected {n_negative} negative rows, found {len(negative_pairs)}"
            )
        if len(positive_pairs) != n_positive:
            raise ValueError(
                f"Reader{reader_number}: expected {n_positive} positive rows, found {len(positive_pairs)}"
            )

        negative = np.asarray(negative_pairs, dtype=float)
        positive = np.asarray(positive_pairs, dtype=float)
        ratings[:n_negative, reader_index] = negative[:, 0]
        ratings[:n_negative, n_readers + reader_index] = negative[:, 1]
        ratings[n_negative:, reader_index] = positive[:, 0]
        ratings[n_negative:, n_readers + reader_index] = positive[:, 1]

    return ratings


def read_mrmc_input(
    path: str | Path,
    *,
    n_readers: int,
    n_negative: int,
    n_positive: int,
) -> np.ndarray:
    """Read either supported JSRT-MRMC input layout.

    Files containing ``ReaderN`` block headers are interpreted as the original
    JSRT-MRMC reader-block format.  Other files are interpreted as the numeric
    matrix format used by earlier Python releases.
    """
    text = Path(path).read_text(errors="replace")
    if any(_READER_RE.match(line) for line in text.splitlines()):
        return read_legacy_mrmc_input(
            path,
            n_readers=n_readers,
            n_negative=n_negative,
            n_positive=n_positive,
        )

    data = read_mrmc_matrix(path, n_readers=n_readers)
    expected_rows = int(n_negative) + int(n_positive)
    if data.shape[0] != expected_rows:
        raise ValueError(f"expected {expected_rows} rows, found {data.shape[0]}")
    return data
