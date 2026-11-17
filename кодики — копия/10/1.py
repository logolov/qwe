from pathlib import Path
import mpmath as mp

# Высокая точность внутренних вычислений.
mp.mp.dps = 120
HERE = Path(__file__).resolve().parent
OUTPUT_PLACES = 60


def find_input(base_name: str) -> Path:
    """Принимает как task1.txt, так и task1(1).txt."""
    candidates = [HERE / base_name]
    stem = base_name[:-4] if base_name.lower().endswith(".txt") else base_name
    candidates.append(HERE / f"{stem}(1).txt")
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        f"Не найден {base_name} или {stem}(1).txt в папке {HERE}"
    )


def read_rows(base_name: str, count: int):
    path = find_input(base_name)
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != count:
                raise ValueError(
                    f"{path.name}, строка {line_no}: ожидалось {count} чисел, найдено {len(parts)}"
                )
            try:
                rows.append([int(part) for part in parts])
            except ValueError as exc:
                raise ValueError(
                    f"{path.name}, строка {line_no}: аргументы должны быть целыми числами"
                ) from exc
    if len(rows) != 10:
        raise ValueError(f"{path.name}: ожидалось 10 наборов, найдено {len(rows)}")
    return rows


def f1(n: int):
    # n * log2(log2(n))
    return mp.mpf(n) * mp.log(mp.log(n, 2), 2)


def f2(x: int, y: int):
    # x*y*log2(x) + y^3
    return mp.mpf(x) * y * mp.log(x, 2) + mp.mpf(y) ** 3


def f3(a: int, b: int, c: int):
    # a^(3/2)*c + c^2; b в циклах не используется.
    return mp.mpf(a) * mp.sqrt(a) * c + mp.mpf(c) ** 2


def as_text(value, places: int = OUTPUT_PLACES) -> str:
    whole = int(mp.floor(value))
    fraction = value - whole
    scale = mp.mpf(10) ** places
    rounded = int(mp.floor(fraction * scale + mp.mpf("0.5")))
    if rounded >= 10 ** places:
        whole += 1
        rounded = 0
    return f"{whole},{rounded:0{places}d}"


def save(input_name: str, output_name: str, count: int, function):
    rows = read_rows(input_name, count)
    values = [function(*row) for row in rows]
    out_path = HERE / output_name
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(as_text(value) for value in values) + "\n")
    print(f"Создан {output_name}: {len(values)} значений")


def main():
    save("task1.txt", "ans1.txt", 1, f1)
    save("task2.txt", "ans2.txt", 2, f2)
    save("task3.txt", "ans3.txt", 3, f3)
    print("Готово. Все три файла записаны рядом со скриптом.")


if __name__ == "__main__":
    main()
