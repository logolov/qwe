"""
Пятнашки: получить расстановку с максимальной оценкой.

Идея:
  1. Пока свободная область больше 3x3, "очищаем" верхнюю строку, затем левый
     столбец (и так по кругу). Каждая плитка ставится на место поиском в ширину
     по состояниям (пустая клетка, плитка); две последние плитки строки/столбца
     ставятся вместе поиском по (пустая, плитка A, плитка B).
     Уже поставленные плитки больше не трогаем.
  2. Остаток 3x3 (181440 достижимых состояний) разбираем полным BFS и берём
     достижимое состояние с максимальной оценкой (если паритет не позволяет
     собрать всё, получим n^2-3 правильных клеток, что является максимумом).

Запуск:  python solve.py            (читает task1..3.txt, пишет ans1..3.txt)
"""
import sys
from collections import deque

DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def read_task(path):
    with open(path) as f:
        data = list(map(int, f.read().split()))
    n = data[0]
    grid = [data[1 + i * n: 1 + (i + 1) * n] for i in range(n)]
    return n, grid


def score(grid, n):
    """Число плиток, стоящих на своих местах (пустая клетка не считается)."""
    s = 0
    for i in range(n):
        for j in range(n):
            v = grid[i][j]
            if v and v == i * n + j + 1:
                s += 1
    return s


class Puzzle:
    def __init__(self, n, grid):
        self.n = n
        self.g = [row[:] for row in grid]
        self.moves = []  # (row, col), 1-индексация: клетка, которую двигаем
        for i in range(n):
            for j in range(n):
                if self.g[i][j] == 0:
                    self.blank = (i, j)

    def move_blank_to(self, ni, nj):
        bi, bj = self.blank
        assert abs(bi - ni) + abs(bj - nj) == 1
        self.moves.append((ni + 1, nj + 1))
        self.g[bi][bj] = self.g[ni][nj]
        self.g[ni][nj] = 0
        self.blank = (ni, nj)

    def apply_blank_path(self, path):
        for p in path:
            self.move_blank_to(*p)

    def find(self, v):
        for i in range(self.n):
            for j in range(self.n):
                if self.g[i][j] == v:
                    return (i, j)


def bfs_objects(puz, tiles, targets, fixed):
    """
    BFS по состояниям (пустая, позиции отслеживаемых плиток).
    Возвращает список позиций, куда последовательно переходит пустая клетка.
    """
    n = puz.n
    start = (puz.blank,) + tuple(puz.find(t) for t in tiles)
    goal = tuple(targets)
    if start[1:] == goal:
        return []
    prev = {start: None}
    q = deque([start])
    while q:
        st = q.popleft()
        bi, bj = st[0]
        for di, dj in DIRS:
            ni, nj = bi + di, bj + dj
            if not (0 <= ni < n and 0 <= nj < n) or (ni, nj) in fixed:
                continue
            npos = (ni, nj)
            # если на клетку встаёт отслеживаемая плитка - она переезжает на место пустой
            new_t = tuple((bi, bj) if p == npos else p for p in st[1:])
            ns = (npos,) + new_t
            if ns in prev:
                continue
            prev[ns] = st
            if new_t == goal:
                path = []
                cur = ns
                while prev[cur] is not None:
                    path.append(cur[0])
                    cur = prev[cur]
                return path[::-1]
            q.append(ns)
    raise RuntimeError("нет пути")


def place_line(puz, cells, fixed):
    """cells - упорядоченные клетки линии (строки или столбца), куда ставим плитки."""
    n = puz.n
    tiles = [i * n + j + 1 for i, j in cells]
    # все, кроме двух последних - по одной
    for k in range(len(cells) - 2):
        path = bfs_objects(puz, [tiles[k]], [cells[k]], fixed)
        puz.apply_blank_path(path)
        fixed.add(cells[k])
    # две последние - вместе
    path = bfs_objects(puz, tiles[-2:], cells[-2:], fixed)
    puz.apply_blank_path(path)
    fixed.add(cells[-2])
    fixed.add(cells[-1])


def solve_3x3_region(puz, r0, c0):
    """Полный BFS по области 3x3 с левым верхним углом (r0, c0)."""
    n = puz.n
    cells = [(r0 + i, c0 + j) for i in range(3) for j in range(3)]
    target = [(i * n + j + 1) if (i, j) != (n - 1, n - 1) else 0 for i, j in cells]

    def key(state):
        # (плиток на месте, пустая на месте)
        t = sum(1 for a, b in zip(state, target) if a and a == b)
        return (t, state[8] == 0 and target[8] == 0)

    start = tuple(puz.g[i][j] for i, j in cells)
    prev = {start: None}
    q = deque([start])
    best, best_key = start, key(start)
    while q:
        st = q.popleft()
        z = st.index(0)
        zi, zj = divmod(z, 3)
        for di, dj in DIRS:
            ni, nj = zi + di, zj + dj
            if 0 <= ni < 3 and 0 <= nj < 3:
                nz = ni * 3 + nj
                l = list(st)
                l[z], l[nz] = l[nz], 0
                ns = tuple(l)
                if ns in prev:
                    continue
                prev[ns] = (st, nz)
                k = key(ns)
                if k > best_key:
                    best, best_key = ns, k
                q.append(ns)
    # восстановление пути
    path = []
    cur = best
    while prev[cur] is not None:
        p, nz = prev[cur]
        path.append(cells[nz])
        cur = p
    puz.apply_blank_path(path[::-1])


def solve(n, grid):
    puz = Puzzle(n, grid)
    r0 = c0 = 0
    fixed = set()
    while n - r0 > 3 or n - c0 > 3:
        if n - r0 > 3 and (n - r0 >= n - c0):
            place_line(puz, [(r0, j) for j in range(c0, n)], fixed)
            r0 += 1
        else:
            place_line(puz, [(i, c0) for i in range(r0, n)], fixed)
            c0 += 1
    solve_3x3_region(puz, r0, c0)
    return puz


def verify(n, grid, moves):
    """Независимая проверка: проигрываем ходы по условию задачи."""
    g = [row[:] for row in grid]
    for i in range(n):
        for j in range(n):
            if g[i][j] == 0:
                bi, bj = i, j
    for r, c in moves:
        r -= 1
        c -= 1
        assert abs(r - bi) + abs(c - bj) == 1, "некорректный ход"
        g[bi][bj], g[r][c] = g[r][c], 0
        bi, bj = r, c
    return score(g, n)


def main():
    for t in (1, 2, 3):
        n, grid = read_task(f"task{t}.txt")
        puz = solve(n, grid)
        s = verify(n, grid, puz.moves)
        with open(f"ans{t}.txt", "w") as f:
            f.write(f"{len(puz.moves)}\n")
            for r, c in puz.moves:
                f.write(f"{r} {c}\n")
        print(f"task{t}: n={n}, ходов={len(puz.moves)}, оценка={s} из {n * n - 1}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
