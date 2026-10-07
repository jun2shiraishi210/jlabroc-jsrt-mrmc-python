from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).parent / "data"


def _run(*args: str) -> str:
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run(
        [sys.executable, "-m", "jlabroc_jsrt_mrmc", *args],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return proc.stdout


def test_cli_jlabroc():
    out = _run("jlabroc", str(DATA / "Test_R1A_In.txt"))
    assert "a          : 1.517405" in out
    assert "b          : 0.852443" in out
    assert "AUC        : 0.875909" in out


def test_cli_mrmc():
    out = _run(
        "mrmc",
        str(DATA / "RateData_Level2_R5_ver050_50_50_00001.txt"),
        "--readers", "5",
        "--negative", "50",
        "--positive", "50",
    )
    assert "Mean AUC System 1 : 0.8647" in out
    assert "Mean AUC System 2 : 0.8058" in out
    assert "Difference        : 0.0589" in out
    assert "p                 : 0.005440" in out


def test_cli_mrmc_legacy_reader_block_format():
    out = _run(
        "mrmc",
        str(DATA / "Test_In_forMRMC_R5_P50_N50_legacy.txt"),
        "--readers", "5",
        "--negative", "50",
        "--positive", "50",
    )
    assert "Mean AUC System 1 : 0.8647" in out
    assert "Mean AUC System 2 : 0.8058" in out
    assert "Difference        : 0.0589" in out
    assert "p                 : 0.005440" in out
