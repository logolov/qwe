from pathlib import Path
import math
import statistics
import subprocess
import time

folder = Path(__file__).resolve().parent
exe = folder / "task3.exe"
K = 3.9e-9
BG = 0.012

cases = [
    (3000, 50, 7000),
    (500, 5, 9000),
    (9000, 90, 500),
    (7000, 30, 3000),
    (1500, 70, 1500),
    (100, 100, 10000),
    (10000, 1, 5000),
    (300, 20, 300),
    (6000, 60, 9000),
]


def measure(a, b, c, repeats=2, timeout=60):
    (folder / "input.txt").write_text(f"{a} {b} {c}\n", encoding="ascii")
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        try:
            r = subprocess.run([str(exe)], cwd=folder, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        times.append(time.perf_counter() - start)
    return statistics.median(times)


print(f"{'a':>6} {'b':>4} {'c':>6} {'измер.':>9} {'модель':>9} {'отн.':>6}", flush=True)
for a, b, c in cases:
    t = measure(a, b, c)
    pred = BG + K * (a * math.sqrt(a) * c + c * c)
    if t is None:
        print(f"{a:>6} {b:>4} {c:>6}   лимит времени", flush=True)
        continue
    print(f"{a:>6} {b:>4} {c:>6} {t:>9.4f} {pred:>9.4f} {t/pred:>6.2f}", flush=True)