
import subprocess
import time
import statistics
from pathlib import Path

# Папка, в которой находится этот Python-файл
FOLDER = Path(__file__).resolve().parent

# Сколько раз запускать программу для одного измерения
REPEATS = 7

# Максимальное время одного запуска в секундах
TIMEOUT = 5

# Количество аргументов для каждой программы
ARGUMENTS = {
    1: 1,
    2: 2,
    3: 3
}


def measure(task_number, args):
    exe = FOLDER / f"task{task_number}.exe"
    input_file = FOLDER / "input.txt"

    # Проверяем наличие EXE
    if not exe.exists():
        print(f"Не найден файл {exe.name}")
        return

    # Записываем аргументы в input.txt
    input_file.write_text(
        " ".join(map(str, args)) + "\n",
        encoding="ascii"
    )

    times = []

    print(f"\nПрограмма: {exe.name}")
    print(f"Входные данные: {args}")

    for i in range(REPEATS):
        start = time.perf_counter()

        try:
            result = subprocess.run(
                [str(exe)],
                cwd=str(FOLDER),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=TIMEOUT
            )

        except subprocess.TimeoutExpired:
            print("Превышено время ожидания!")
            break

        except OSError as error:
            print("Ошибка запуска:", error)
            return

        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

        print(f"Запуск {i + 1}: {elapsed:.3f} мс")

        if result.returncode != 0:
            print("Код завершения:", result.returncode)

    if times:
        print("\nМедианное время:", 
              round(statistics.median(times), 3), "мс")
        print("Минимальное время:",
              round(min(times), 3), "мс")
        print("Максимальное время:",
              round(max(times), 3), "мс")


def main():
    print("ИССЛЕДОВАНИЕ НЕИЗВЕСТНОГО АЛГОРИТМА")
    print("------------------------------------")

    while True:
        choice = input(
            "\nВыбери программу (1, 2, 3) или q для выхода: "
        ).strip()

        if choice.lower() == "q":
            break

        if choice not in ("1", "2", "3"):
            print("Нужно выбрать 1, 2 или 3.")
            continue

        task = int(choice)

        raw = input(
            f"Введи {ARGUMENTS[task]} целых чисел через пробел: "
        )
выаьджжжжжжжжжжжжжжжжжжжжжжжжжжжж
        try:
            args = [int(x) for x in raw.split()]
        except ValueError:
            print("Ошибка: вводить нужно только целые числа.")
            continue

        if len(args) != ARGUMENTS[task]:
            print("Неправильное количество чисел!")
            continue

        if any(x <= 0 for x in args):
            print("Для начала используй положительные числа.")
            continue

        measure(task, args)


if __name__ == "__main__":
    main()
