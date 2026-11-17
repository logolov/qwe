import subprocess, time, statistics, sys, csv, os

def run(exe, args, repeats=1, timeout=60):
    with open("input.txt", "w") as f:
        f.write(" ".join(map(str, args)))
    times = []
    for _ in range(repeats):
        t = time.perf_counter()
        try:
            subprocess.run(
                [exe],
                timeout=timeout,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return None
        times.append(time.perf_counter() - t)
    return statistics.median(times)

def sweep(exe, make_args, values, out_csv):
    rows = []
    prev = None
    for v in values:
        t = run(exe, make_args(v))
        if t is None:
            print(f"{v:>12}  превышен лимит времени")
            rows.append((v, "", ""))
            break
        ratio = t / prev if prev else ""
        r = round(ratio, 2) if ratio != "" else ""
        print(f"{v:>12} {t:>10.4f} {r}")
        rows.append((v, t, ratio))
        prev = t
    with open(out_csv, "w", newline="") as f:
        csv.writer(f).writerows([("x", "time", "ratio")] + rows)

if __name__ == "__main__":
    from pathlib import Path
    import os

    folder = Path(__file__).resolve().parent
    os.chdir(folder)
    exe = str(folder / "task2.exe")

    print("\nn = 10, меняем m:", flush=True)
    sweep(exe, lambda m: [10, m], [500, 1000, 1500, 2000, 3000], "t2_m_wide.csv")

    print("\nпроверка соседних m, n = 10:", flush=True)
    sweep(exe, lambda m: [10, m], [1000, 1001, 1024, 1025], "t2_m_neighbors.csv")