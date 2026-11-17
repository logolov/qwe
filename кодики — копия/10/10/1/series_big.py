import csv
import math
import random
import statistics
import subprocess
import time
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
EXE = FOLDER / "task1.exe"
VALUES = [100, 150, 200, 250, 300, 350, 400]
REPEATS = 5
TIMEOUT = 60


def run_once(n):
    (FOLDER / "input.txt").write_text(f"{n}\n", encoding="ascii")
    start = time.perf_counter()
    r = subprocess.run([str(EXE)], cwd=FOLDER, capture_output=True, timeout=TIMEOUT)
    elapsed = time.perf_counter() - start
    out = r.stdout.decode("cp866", errors="replace").strip()
    if r.returncode != 0 or "incorrect" in out.lower():
        raise RuntimeError(f"n={n}: {out!r}, код {r.returncode}")
    return elapsed


def main():
    random.seed(1)
    times = {v: [] for v in VALUES}
    run_once(100_000_000)

    for rep in range(REPEATS):
        order = VALUES[:]
        random.shuffle(order)
        for v in order:
            times[v].append(run_once(v * 1_000_000))
        print(f"повтор {rep + 1}/{REPEATS} завершён", flush=True)

    print(f"\n{'n, млн':>7} {'медиана':>9} {'минимум':>9} {'макс':>9} "
          f"{'мин/n, нс':>10} {'мин/(n·log2 n), нс':>19}")
    rows = []
    for v in VALUES:
        n = v * 1_000_000
        ts = times[v]
        mn, md, mx = min(ts), statistics.median(ts), max(ts)
        a = mn / n * 1e9
        b = mn / (n * math.log2(n)) * 1e9
        print(f"{v:>7} {md:>9.4f} {mn:>9.4f} {mx:>9.4f} {a:>10.3f} {b:>19.4f}")
        rows.append([v, md, mn, mx, a, b] + ts)

    with (FOLDER / "task1_big_series.csv").open("w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(
            [["n_million", "median", "min", "max", "min_per_n_ns", "min_per_nlogn_ns"]]
            + rows
        )


if __name__ == "__main__":
    main()