from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).parent / "data"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run(
        [sys.executable, "-m", "jlabroc_jsrt_mrmc", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_jlabroc_absolute_path_with_spaces(tmp_path: Path):
    folder = tmp_path / "folder with spaces"
    folder.mkdir()
    target = folder / "JLABROC input.txt"
    shutil.copy2(DATA / "Test_R1A_In.txt", target)
    proc = _run("jlabroc", str(target.resolve()))
    assert proc.returncode == 0, proc.stderr
    assert "AUC        : 0.875909" in proc.stdout


def test_mrmc_absolute_path_with_spaces(tmp_path: Path):
    from jlabroc_jsrt_mrmc.io import read_mrmc_matrix

    folder = tmp_path / "folder with spaces"
    folder.mkdir()
    target = folder / "MRMC input.txt"
    shutil.copy2(DATA / "RateData_Level2_R5_ver050_50_50_00001.txt", target)
    data = read_mrmc_matrix(target.resolve(), n_readers=5)
    assert data.shape == (100, 10)
