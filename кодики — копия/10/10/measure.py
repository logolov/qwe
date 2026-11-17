import subprocess, time, statistics, sys, csv, os

def run(exe, args, repeats=3, timeout=120):
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
        ratio = t / prev if (t and prev) else ""
        print(f"{v:>12} {t if t is None else round(t, 4):>10} {ratio if ratio == '' else round(ratio, 2)}")
        rows.append((v, t, ratio))
        prev = t
        if t is None:
            break
    with open(out_csv, "w", newline="") as f:
        csv.writer(f).writerows([("x", "time", "ratio")] + rows)

if __name__ == "__main__":
    # task1: один аргумент, удваиваем n
    sweep("task1.exe", lambda n: [n], [8_000_000, 16_000_000, 32_000_000, 64_000_000, 128_000_000], "t1.csv")