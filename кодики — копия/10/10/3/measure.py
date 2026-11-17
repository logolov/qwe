import subprocess
import time
import statistics
import csv
import os
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
os.chdir(FOLDER)
EXE = str(FOLDER / "task3.exe")


def run(args, repeats=2, timeout=30):
    (FOLDER / "input.txt").write_text(" ".join(map(str, args)) + "\n", encoding="ascii")
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        try:
            subprocess.run(
                [EXE],
                cwd=FOLDER,
                timeout=timeout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return None
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def sweep(make_args, values, out_csv):
    rows = []
    prev = None
    for v in values:
        t = run(make_args(v))
        if t is None:
            print(f"{v:>12}  превышен лимит времени", flush=True)
            rows.append((v, "", ""))
            break
        ratio = t / prev if prev else ""
        r = round(ratio, 2) if ratio != "" else ""
        print(f"{v:>12} {t:>10.4f} {r}", flush=True)
        rows.append((v, t, ratio))
        prev = t
    with open(out_csv, "w", newline="") as f:
        csv.writer(f).writerows([("x", "time", "ratio")] + rows)


if __name__ == "__main__":
    vals = [10, 100, 1000, 10000, 100000]

    print("\nпервый меняется, остальные 10 10:", flush=True)
    sweep(lambda x: [x, 10, 10], vals, "t3_a.csv")

    print("\nвторой меняется, остальные 10 10:", flush=True)
    sweep(lambda x: [10, x, 10], vals, "t3_b.csv")

    print("\nтретий меняется, остальные 10 10:", flush=True)
    sweep(lambda x: [10, 10, x], vals, "t3_c.csv")