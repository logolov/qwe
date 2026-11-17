from pathlib import Path
import math
import statistics
import subprocess
import time

folder = Path(__file__).resolve().parent
exe = folder / "task2.exe"
BG = 0.012
K1 = 8.3e-9
K2 = 0.9e-9


def model(n, m):
    return BG + K1 * n * m * math.log2(n) + K2 * m ** 3


def run_once(n, m, timeout):
    (folder / "input.txt").write_text(f"{n} {m}\n", encoding="ascii")
    start = time.perf_counter()
    try:
        r = subprocess.run([str(exe)], cwd=folder, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    elapsed = time.perf_counter() - start
    return elapsed, r.stdout.decode("cp866", errors="replace").strip()


print("Проверка границ (лимит 20 с; timeout = аргументы приняты):", flush=True)
for n, m in [(10**6, 10), (10**7, 10), (10**8, 10), (10, 5000), (10, 10**5), (10**6, 10**4)]:
    t, out = run_once(n, m, 20)
    shown = "timeout" if t is None else f"{t:.4f} с"
    print(f"{n:>10} {m:>8}  {shown:>10}  {out}", flush=True)

cases = [
    (2, 1000), (1, 1000), (1000, 1500), (200000, 100), (300000, 150),
    (5, 2500), (20000, 800), (100, 2000), (40000, 500), (900000, 10),
    (50, 50), (5000, 300),
]

print(f"\n{'n':>8} {'m':>6} {'измер.':>9} {'модель':>9} {'отн.':>6}  вывод", flush=True)
for n, m in cases:
    ts = []
    out = ""
    for _ in range(2):
        t, out = run_once(n, m, 60)
        if t is None:
            break
        ts.append(t)
    if not ts:
        print(f"{n:>8} {m:>6}   лимит времени", flush=True)
        continue
    t = statistics.median(ts)
    p = model(n, m) if n > 1 else BG + K2 * m ** 3
    print(f"{n:>8} {m:>6} {t:>9.4f} {p:>9.4f} {t/p:>6.2f}  {out}", flush=True)