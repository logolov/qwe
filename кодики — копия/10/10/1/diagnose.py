from pathlib import Path
import subprocess
import time

folder = Path(__file__).resolve().parent
exe = folder / "task1.exe"

values = [256_000_000, 320_000_000, 400_000_000, 512_000_000]

for n in values:
    (folder / "input.txt").write_text(f"{n}\n", encoding="ascii")

    print(f"\nПроверка n = {n}", flush=True)
    start = time.perf_counter()

    try:
        result = subprocess.run(
            [str(exe)],
            cwd=folder,
            capture_output=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("Превышен лимит 30 секунд. Проверку останавливаем.")
        break

    elapsed = time.perf_counter() - start

    print(f"Время: {elapsed:.6f} с")
    print(f"Код завершения: {result.returncode}")
    print(f"stdout: {result.stdout[:2000]!r}")
    print(f"stderr: {result.stderr[:2000]!r}")

    if result.returncode != 0:
        print("Ненулевой код завершения. Проверку останавливаем.")
        break