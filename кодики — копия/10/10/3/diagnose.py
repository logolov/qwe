from pathlib import Path
import statistics
import subprocess
import time

folder = Path(__file__).resolve().parent
exe = folder / "task3.exe"


def measure(a, b, c, repeats=2, timeout=40):
    (folder / "input.txt").write_text(f"{a} {b} {c}\n", encoding="ascii")
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                [str(exe)], cwd=folder, capture_output=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return None, "timeout"
        times.append(time.perf_counter() - start)
    text = result.stdout.decode("cp866", errors="replace").strip()
    return statistics.median(times), text


def table(title, cases):
    print(f"\n{title}", flush=True)
    for a, b, c in cases:
        t, out = measure(a, b, c)
        if t is None:
            print(f"{a:>6} {b:>4} {c:>6}   лимит времени", flush=True)
            continue
        flag = "  <-- ошибка аргумента!" if "Incorrect" in out else ""
        print(f"{a:>6} {b:>4} {c:>6} {t:>9.4f}  {out}{flag}", flush=True)


table("b меняется, a=10, c=10000",
      [(10, b, 10000) for b in (1, 25, 50, 75, 100)])

table("b меняется, a=10000, c=10",
      [(10000, b, 10) for b in (1, 25, 50, 75, 100)])

table("b меняется, a=2000, c=2000",
      [(2000, b, 2000) for b in (1, 25, 50, 75, 100)])