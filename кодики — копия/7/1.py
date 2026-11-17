import os
import sys
import numpy as np

def solve(path):
    """Максимальная по площади подматрица из одних 0 или одних 1.
    Возвращает (top, left, bottom, right, area), 0-нумерация."""
    best = (0, 0, 0, 0, 0)
    with open(path) as f:
        n, m = map(int, f.readline().split())
        h = [np.zeros(m, dtype=np.int32), np.zeros(m, dtype=np.int32)]
        for i in range(n):
            row = np.frombuffer(f.readline().strip().encode(), dtype=np.uint8) - 48
            for c in (0, 1):
                # высоты столбцов из подряд идущих значений c, оканчивающихся в строке i
                h[c] = np.where(row == c, h[c] + 1, 0).astype(np.int32)
                H = h[c].tolist() + [0]
                # быстрый отсев: больше текущего лучшего в этой строке не получить
                if max(H) * m <= best[4]:
                    continue
                stack = []  # индексы столбцов с возрастающими высотами
                for j, cur in enumerate(H):
                    while stack and H[stack[-1]] >= cur:
                        hh = H[stack.pop()]
                        left = stack[-1] + 1 if stack else 0
                        area = hh * (j - left)
                        if area > best[4]:
                            best = (i - hh + 1, left, i, j - 1, area)
                    stack.append(j)
    return best

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    pattern = sys.argv[1] if len(sys.argv) > 1 else "task_{}.txt"
    for k in (1, 2, 3):
        t, l, b, r, area = solve(os.path.join(folder, pattern.format(k)))
        with open(os.path.join(folder, f"ans{k}.txt"), "w") as out:
            out.write(f"{t} {l} {b} {r}\n")
        print(k, t, l, b, r, "площадь =", area, flush=True)