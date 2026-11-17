import ctypes
import math
import random
import statistics
import subprocess
from ctypes import wintypes
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
EXE = FOLDER / "task1.exe"
VALUES = [250_000, 500_000, 1_000_000, 2_000_000, 4_000_000, 8_000_000, 16_000_000]
REPEATS = 15

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.QueryProcessCycleTime.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_ulonglong)]
k32.QueryProcessCycleTime.restype = wintypes.BOOL


def cycles(n):
    (FOLDER / "input.txt").write_text(f"{n}\n", encoding="ascii")
    p = subprocess.Popen([str(EXE)], cwd=FOLDER,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate(timeout=60)
    if "incorrect" in out.decode("cp866", errors="replace").lower():
        raise RuntimeError(f"n={n}: аргумент отклонён")
    c = ctypes.c_ulonglong(0)
    if not k32.QueryProcessCycleTime(wintypes.HANDLE(int(p._handle)), ctypes.byref(c)):
        raise OSError(ctypes.get_last_error())
    return c.value


def main():
    data = {1: []}
    for v in VALUES:
        data[v] = []
    cycles(1_000_000)

    for rep in range(REPEATS):
        order = list(data)
        random.shuffle(order)
        for v in order:
            data[v].append(cycles(v))
        print(f"повтор {rep + 1}/{REPEATS}", flush=True)

    base = statistics.median(data[1])
    print(f"\nбаза (n=1): {base / 1e6:.2f} Мтакт\n")
    print(f"{'n':>10} {'чистые Мтакт':>13} {'разброс %':>10} {'такт/n':>8} {'такт/(n·log2 n)':>16}")
    for v in VALUES:
        net = [c - base for c in data[v]]
        med = statistics.median(net)
        spread = (max(net) - min(net)) / med * 100
        print(f"{v:>10} {med / 1e6:>13.2f} {spread:>10.1f} "
              f"{med / v:>8.2f} {med / (v * math.log2(v)):>16.3f}")


if __name__ == "__main__":
    main()