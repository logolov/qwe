#!/usr/bin/env python3
"""
Задача 9. 3-разбиение (MAX-3-SAT).  Итоговый балл = 6250*S1 + 500*S2 + S3.

Запуск:   python3 solve.py [папка_с_task-файлами] [секунды_для_задачи_3]
Читает:   task1.txt/task2.txt/task3.txt (или task1_3.txt ... task3_3.txt)
Пишет:    ans1.txt, ans2.txt, ans3.txt (значения 0/1 через пробел, одна строка)

Задача 1 (20 переменных)  - точный перебор всех 2^20 наборов (numpy) -> оптимум.
Задача 2 (100 переменных) - WalkSAT на чистом Python, много перезапусков.
Задача 3 (36616 переменных, 444235 дизъюнктов) - векторизованный локальный поиск
                            на numpy (параллельный жадный спуск + боковые ходы + шум).
                            gcc и любые компиляторы НЕ нужны: только python и numpy.
Если ans*.txt уже есть, лучший ответ не портится: новый записывается только если он лучше.
"""
import os, sys, random, time
import numpy as np

# ---------- чтение / проверка ----------
def find_task(d, i):
    for name in (f"task{i}.txt", f"task{i}_3.txt"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"нет файла task{i}.txt в {d}")

def read_task(path):
    with open(path) as f:
        n, m = map(int, f.readline().split())
        d = np.array(f.read().split(), dtype=np.int64).reshape(m, 3)
    return n, m, d

def score(d, assign):
    """число выполнимых дизъюнктов для массива assign (0/1, длина n)"""
    a = np.asarray(assign, dtype=bool)
    v = a[np.abs(d) - 1]
    return int(np.where(d > 0, v, ~v).any(axis=1).sum())

def read_ans(path, n):
    if not os.path.exists(path):
        return None
    t = open(path).read().split()
    if len(t) != n or any(x not in ("0", "1") for x in t):
        return None
    return np.array(t, dtype=np.int8)

def write_ans(path, assign):
    with open(path, "w") as f:
        f.write(" ".join(str(int(x)) for x in assign) + "\n")

def save_if_better(path, d, n, assign):
    old = read_ans(path, n)
    new_s = score(d, assign)
    if old is None or score(d, old) < new_s:
        write_ans(path, assign)
        return new_s
    return score(d, old)

# ---------- задача 1: точный перебор ----------
def solve_bruteforce(n, d):
    N = 1 << n
    idx = np.arange(N, dtype=np.uint32)
    cnt = np.zeros(N, dtype=np.uint8)
    for row in d:
        sat = np.zeros(N, dtype=bool)
        for l in row:
            bit = ((idx >> (abs(int(l)) - 1)) & 1).astype(bool)
            sat |= bit if l > 0 else ~bit
        cnt += sat
    best = int(cnt.argmax())
    return np.array([(best >> i) & 1 for i in range(n)], dtype=np.int8)

# ---------- задача 2: WalkSAT на чистом Python ----------
def walksat(n, d, seconds, p=0.05, seed=0, init=None):
    rng = random.Random(seed)
    clauses = []
    for row in d:
        lits = list(dict.fromkeys(int(x) for x in row))
        if any(-l in lits for l in lits):
            continue                       # тавтология: всегда истинна
        clauses.append(lits)
    taut = len(d) - len(clauses)
    occ = [[] for _ in range(n + 1)]
    for ci, c in enumerate(clauses):
        for l in c:
            occ[abs(l)].append(ci)
    val = [0] + ([int(x) for x in init] if init is not None else [rng.randint(0, 1) for _ in range(n)])
    lt = lambda l: val[l] if l > 0 else 1 - val[-l]
    nt = [sum(lt(l) for l in c) for c in clauses]
    unsat = [ci for ci, k in enumerate(nt) if k == 0]
    pos = {ci: i for i, ci in enumerate(unsat)}
    best, bestv = len(unsat), val[:]
    end = time.time() + seconds
    it = 0
    def brk(v):
        b = 0
        for ci in occ[v]:
            if nt[ci] == 1:
                for l in clauses[ci]:
                    if abs(l) == v and lt(l):
                        b += 1
        return b
    while unsat and (it & 1023 or time.time() < end):
        it += 1
        ci = unsat[rng.randrange(len(unsat))]
        c = clauses[ci]
        if rng.random() < p:
            v = abs(rng.choice(c))
        else:
            bb, cand = 10**9, []
            for l in c:
                b = brk(abs(l))
                if b < bb: bb, cand = b, [abs(l)]
                elif b == bb: cand.append(abs(l))
            v = rng.choice(cand)
        for cj in occ[v]:                  # переворот v
            for l in clauses[cj]:
                if abs(l) == v:
                    if lt(l):
                        nt[cj] -= 1
                        if nt[cj] == 0:
                            pos[cj] = len(unsat); unsat.append(cj)
                    else:
                        if nt[cj] == 0:
                            i = pos.pop(cj); last = unsat.pop()
                            if last != cj: unsat[i] = last; pos[last] = i
                        nt[cj] += 1
        val[v] = 1 - val[v]
        if len(unsat) < best:
            best, bestv = len(unsat), val[:]
    return np.array(bestv[1:], dtype=np.int8), len(d) - best

# ---------- задача 3: numpy ----------
def solve_numpy(n, d, seconds, init=None, seed=1, sp=0.5, nz=2000, qmin=0.9, log=True):
    rng = np.random.default_rng(seed)
    var = np.abs(d) - 1; pos = d > 0
    valid = np.ones(d.shape, bool); taut = np.zeros(len(d), bool)
    for a, b in ((0, 1), (0, 2), (1, 2)):        # повторы и тавтологии внутри дизъюнкта
        same = var[:, a] == var[:, b]
        taut |= same & (pos[:, a] != pos[:, b])
        valid[:, b] &= ~(same & (pos[:, a] == pos[:, b]))
    keep = ~taut
    var, pos, valid = var[keep], pos[keep], valid[keep]
    if init is not None:
        val = np.asarray(init, dtype=bool).copy()
    else:   # старт: значение, которое чаще встречается в дизъюнктах
        bal = np.bincount(var[valid & pos], minlength=n) - np.bincount(var[valid & ~pos], minlength=n)
        val = np.where(bal > 0, True, np.where(bal < 0, False, rng.random(n) < .5))
    best, bestv, q, it = 10**9, val.copy(), 0.5, 0
    t0 = time.time()
    while time.time() - t0 < seconds:
        lt = (val[var] == pos) & valid
        nt = lt.sum(1)
        uns = int((nt == 0).sum())
        if uns < best:
            best, bestv = uns, val.copy()
        if log and it % 100 == 0:
            print(f"  задача 3: {time.time()-t0:5.0f} c, невыполнено сейчас {uns}, лучшее {best}", flush=True)
        make = np.bincount(var[valid & (nt == 0)[:, None]], minlength=n)
        brk = np.bincount(var[lt & (nt == 1)[:, None]], minlength=n)
        gain = make - brk
        good = gain > 0
        if good.any():                              # спуск: часть улучшающих переменных сразу
            flip = good & (rng.random(n) < q)
        else:                                       # плато: боковые ходы + шум
            flip = (gain == 0) & (rng.random(n) < sp)
            uc = np.nonzero(nt == 0)[0]
            if len(uc):
                pick = rng.choice(uc, size=min(len(uc), nz), replace=False)
                flip[var[pick, rng.integers(0, 3, len(pick))]] ^= True
        val = val ^ flip
        it += 1
        q = max(qmin, q * 0.995)
    return bestv.astype(np.int8)

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    t3 = float(sys.argv[2]) if len(sys.argv) > 2 else 500
    total = 0
    weights = {1: 6250, 2: 500, 3: 1}
    scores = {}
    # --- задача 1
    p1 = find_task(folder, 1); n, m, d = read_task(p1)
    a = solve_bruteforce(n, d)
    scores[1] = save_if_better("ans1.txt", d, n, a)
    print(f"Задача 1: {scores[1]}/{m} (точный оптимум)")
    # --- задача 2
    p2 = find_task(folder, 2); n, m, d = read_task(p2)
    old = read_ans("ans2.txt", n)
    t0 = time.time(); best = score(d, old) if old is not None else 0
    seed = 0
    while time.time() - t0 < 60:
        seed += 1
        a, s = walksat(n, d, 5, p=random.choice([0.03, 0.06, 0.1]), seed=seed)
        if s > best:
            best = s; save_if_better("ans2.txt", d, n, a)
            print(f"  задача 2: нашли {s}/{m}")
    scores[2] = score(d, read_ans("ans2.txt", n))
    print(f"Задача 2: {scores[2]}/{m}")
    # --- задача 3
    p3 = find_task(folder, 3); n, m, d = read_task(p3)
    old = read_ans("ans3.txt", n)
    a = solve_numpy(n, d, t3, init=old)
    scores[3] = save_if_better("ans3.txt", d, n, a)
    print(f"Задача 3: {scores[3]}/{m}")
    total = sum(weights[i] * scores[i] for i in scores)
    print("Итоговый балл =", total)

if __name__ == "__main__":
    main()