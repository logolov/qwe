import ctypes
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
EXE = FOLDER / "task1.exe"
VALUES = [1_000_000, 8_000_000, 16_000_000, 24_000_000,
          32_000_000, 48_000_000, 64_000_000, 96_000_000]


class PMC(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


psapi = ctypes.WinDLL("psapi", use_last_error=True)
psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
psapi.GetProcessMemoryInfo.restype = wintypes.BOOL


def peak_mb(proc):
    pmc = PMC()
    pmc.cb = ctypes.sizeof(PMC)
    ok = psapi.GetProcessMemoryInfo(
        wintypes.HANDLE(int(proc._handle)), ctypes.byref(pmc), pmc.cb
    )
    if not ok:
        return None
    return pmc.PeakWorkingSetSize / 1024 / 1024, pmc.PeakPagefileUsage / 1024 / 1024


def run(n):
    (FOLDER / "input.txt").write_text(f"{n}\n", encoding="ascii")
    start = time.perf_counter()
    p = subprocess.Popen([str(EXE)], cwd=FOLDER,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate(timeout=60)
    elapsed = time.perf_counter() - start
    mem = peak_mb(p)
    return elapsed, mem, out.decode("cp866", errors="replace").strip()


print(f"{'n':>12} {'время, с':>9} {'пик RAM, МиБ':>13} {'пик commit, МиБ':>16}  вывод")
for n in VALUES:
    t, mem, out = run(n)
    ws, pf = mem if mem else (float("nan"), float("nan"))
    print(f"{n:>12} {t:>9.4f} {ws:>13.1f} {pf:>16.1f}  {out}", flush=True)