from pathlib import Path
import csv
import statistics
import subprocess
import time

FOLDER = Path(__file__).resolve().parent
EXE = FOLDER / "task1.exe"

VALUES = [
    1_000_000,
    2_000_000,
    4_000_000,
    8_000_000,
    12_000_000,
    16_000_000,
    24_000_000,
    32_000_000,
    48_000_000,
    64_000_000,
    80_000_000,
    96_000_000,
]

REPEATS = 3
TIMEOUT = 20


def run_once(n):
    (FOLDER / "input.txt").write_text(
        f"{n}\n",
        encoding="ascii",
    )

    start = time.perf_counter()

    try:
        result = subprocess.run(
            [str(EXE)],
            cwd=FOLDER,
            capture_output=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"

    elapsed = time.perf_counter() - start
    stdout = result.stdout.decode(
        "cp866",
        errors="replace",
    ).strip()
    stderr = result.stderr.decode(
        "cp866",
        errors="replace",
    ).strip()

    if result.returncode != 0:
        raise RuntimeError(
            f"n={n}: код завершения {result.returncode}\n"
            f"stdout: {stdout}\n"
            f"stderr: {stderr}"
        )

    if "incorrect" in stdout.lower():
        raise ValueError(
            f"n={n}: программа отклонила аргумент:\n{stdout}"
        )

    return elapsed, stdout


def main():
    if not EXE.is_file():
        raise FileNotFoundError(
            f"Не найдена программа: {EXE}\n"
            "Проверь имя: program1.exe или task1.exe."
        )

    rows = []
    csv_path = FOLDER / "task1_validation.csv"

    print("task1: проверка времени работы")
    print(f"Повторов на каждое число: {REPEATS}")
    print("Сначала выполняется один прогревочный запуск.\n", flush=True)

    warmup_time, warmup_output = run_once(1_000_000)
    if warmup_time is None:
        print("Прогревочный запуск превысил лимит времени.")
        return

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "n",
            "median_seconds",
            "min_seconds",
            "max_seconds",
            "stdout",
        ])

        print(
            f"{'n':>12} {'медиана':>10} "
            f"{'минимум':>10} {'максимум':>10}  вывод",
            flush=True,
        )

        for n in VALUES:
            times = []
            outputs = []

            for _ in range(REPEATS):
                elapsed, output = run_once(n)

                if elapsed is None:
                    print(
                        f"{n:>12}  превышен лимит {TIMEOUT} с",
                        flush=True,
                    )
                    break

                times.append(elapsed)
                outputs.append(output)

            if len(times) != REPEATS:
                break

            median = statistics.median(times)
            minimum = min(times)
            maximum = max(times)
            output = " | ".join(dict.fromkeys(outputs))
            output = output.replace("\r", " ").replace("\n", " ")

            row = (n, median, minimum, maximum, output)
            rows.append(row)
            writer.writerow(row)
            file.flush()

            print(
                f"{n:>12} {median:>10.6f} "
                f"{minimum:>10.6f} {maximum:>10.6f}  {output}",
                flush=True,
            )

    print(f"\nСохранено строк: {len(rows)}")
    print(f"Результаты записаны в {csv_path.name}")


if __name__ == "__main__":
    main()