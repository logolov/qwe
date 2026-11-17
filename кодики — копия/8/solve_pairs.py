#!/usr/bin/env python3
"""Разбиение на пары: максимизируем сумму lg(gcd) непересекающихся пар."""

from __future__ import annotations

import math
import sys
import time
from collections import defaultdict
from math import gcd
from pathlib import Path

import numpy as np


def log10_int(n: int) -> float:
    if n <= 1:
        return 0.0
    bits = n.bit_length()
    shift = bits - 53
    if shift > 0:
        return math.log10(n >> shift) + shift * math.log10(2.0)
    return math.log10(n)


def load_task(path: Path) -> list[int]:
    data = path.read_text().split()
    n = int(data[0])
    nums = list(map(int, data[1:]))
    if len(nums) != n:
        raise ValueError(f"{path}: declared {n} numbers, got {len(nums)}")
    if len(set(nums)) != n:
        raise ValueError(f"{path}: numbers are not unique")
    return nums


def pair_weight(nums: list[int], pairs: list[tuple[int, int]]) -> float:
    return sum(log10_int(gcd(nums[i], nums[j])) for i, j in pairs)


def write_answer(path: Path, nums: list[int], pairs: list[tuple[int, int]]) -> None:
    lines = [str(len(pairs))]
    for i, j in pairs:
        lines.append(f"{nums[i]} {nums[j]}")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def build_raw_basis(nums: list[int]) -> list[int]:
    basis: list[int] = []
    for raw in nums:
        x = raw
        i = 0
        while i < len(basis) and x > 1:
            f = basis[i]
            g = gcd(f, x)
            if g == 1:
                i += 1
                continue
            if g == f:
                x //= f
                i += 1
                continue
            rest = f // g
            basis[i] = g
            x //= g
            if rest > 1:
                basis.append(rest)
            i += 1
        if x > 1:
            basis.append(x)
    return [b for b in basis if b > 1]


def unique_primes(raw: list[int]) -> list[int]:
    atoms: list[int] = []
    pending = list(set(raw))
    while pending:
        x = pending.pop()
        if x <= 1:
            continue
        i = 0
        while i < len(atoms) and x > 1:
            a = atoms[i]
            g = gcd(a, x)
            if g == 1:
                i += 1
                continue
            if g != a:
                atoms[i] = g
                rest = a // g
                if rest > 1:
                    pending.append(rest)
            x //= g
            if atoms[i] == 1:
                atoms.pop(i)
            else:
                i += 1
        if x > 1:
            atoms.append(x)
    atoms = [a for a in atoms if a > 1]
    atoms.sort()
    # final pairwise split
    changed = True
    while changed:
        changed = False
        n = len(atoms)
        for i in range(n):
            for j in range(i + 1, n):
                g = gcd(atoms[i], atoms[j])
                if g > 1:
                    extra = []
                    if atoms[i] // g > 1:
                        extra.append(atoms[i] // g)
                    if atoms[j] // g > 1:
                        extra.append(atoms[j] // g)
                    atoms[i] = g
                    atoms[j] = extra.pop() if extra else 1
                    atoms.extend(extra)
                    changed = True
                    break
            if changed:
                break
        atoms = [a for a in atoms if a > 1]
    return sorted(set(atoms))


def factor_matrix(nums: list[int], primes: list[int]) -> np.ndarray:
    n, m = len(nums), len(primes)
    exp = np.zeros((n, m), dtype=np.uint8)
    for i, raw in enumerate(nums):
        x = raw
        for a, p in enumerate(primes):
            if x == 1:
                break
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            if e:
                exp[i, a] = e
        if x != 1:
            raise RuntimeError("unfactored remainder: incomplete prime basis")
    return exp


def exp_to_fac(exp: np.ndarray) -> list[dict[int, int]]:
    fac: list[dict[int, int]] = []
    for i in range(exp.shape[0]):
        nz = np.flatnonzero(exp[i])
        fac.append({int(a): int(exp[i, a]) for a in nz})
    return fac


def pair_log_weight_fac(fac: list[dict[int, int]], logs: np.ndarray, i: int, j: int) -> float:
    di, dj = fac[i], fac[j]
    if len(di) > len(dj):
        di, dj = dj, di
    s = 0.0
    for a, e in di.items():
        ej = dj.get(a)
        if ej:
            s += float(logs[a]) * (e if e < ej else ej)
    return s


def collect_topk_edges(
    exp: np.ndarray, logs: np.ndarray, k: int
) -> tuple[list[tuple[float, int, int]], list[list[int]]]:
    n, m = exp.shape
    inv = [np.flatnonzero(exp[:, a]).astype(np.int32) for a in range(m)]
    edges: list[tuple[float, int, int]] = []
    top: list[list[int]] = [[] for _ in range(n)]
    t0 = time.time()
    sc = np.empty(n, dtype=np.float64)
    kk = min(k, n - 1)
    for i in range(n):
        sc.fill(0.0)
        row = exp[i]
        for a in np.flatnonzero(row):
            a = int(a)
            e = int(row[a])
            idx = inv[a]
            if e == 1:
                sc[idx] += logs[a]
            else:
                sc[idx] += logs[a] * np.minimum(exp[idx, a], e)
        sc[i] = -1.0
        js = np.argpartition(sc, -kk)[-kk:]
        partners: list[int] = []
        for j in js:
            j = int(j)
            w = float(sc[j])
            if w <= 0.0:
                continue
            partners.append(j)
            if i < j:
                edges.append((w, i, j))
            else:
                edges.append((w, j, i))
        top[i] = partners
        if (i + 1) % 5000 == 0 or i + 1 == n:
            print(f"    top-k {i + 1}/{n}  {time.time() - t0:.1f}s  edges={len(edges)}", flush=True)
    return edges, top


def greedy_matching(n: int, edges: list[tuple[float, int, int]]) -> list[tuple[int, int]]:
    edges.sort(reverse=True)
    used = np.zeros(n, dtype=np.bool_)
    pairs: list[tuple[int, int]] = []
    for w, i, j in edges:
        if w <= 0:
            continue
        if not used[i] and not used[j]:
            used[i] = used[j] = True
            pairs.append((i, j))
    return pairs


def pair_unused(exp: np.ndarray, logs: np.ndarray, pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    n = exp.shape[0]
    used = np.zeros(n, dtype=np.bool_)
    for i, j in pairs:
        used[i] = used[j] = True
    unused = np.flatnonzero(~used)
    if len(unused) < 2:
        return pairs
    sub = exp[unused]
    m = sub.shape[0]
    extra: list[tuple[int, int]] = []
    taken = np.zeros(m, dtype=np.bool_)
    # exact greedy among leftovers (usually tiny)
    edges: list[tuple[float, int, int]] = []
    for a in range(m):
        for b in range(a + 1, m):
            w = float(np.minimum(sub[a], sub[b]) @ logs)
            if w > 0:
                edges.append((w, a, b))
    edges.sort(reverse=True)
    for _, a, b in edges:
        if taken[a] or taken[b]:
            continue
        taken[a] = taken[b] = True
        extra.append((int(unused[a]), int(unused[b])))
    return pairs + extra


def local_2opt(
    exp: np.ndarray,
    logs: np.ndarray,
    pairs: list[tuple[int, int]],
    top: list[list[int]],
    rounds: int = 12,
) -> list[tuple[int, int]]:
    n = exp.shape[0]
    mate = np.full(n, -1, dtype=np.int32)
    for i, j in pairs:
        mate[i] = j
        mate[j] = i

    def w(i: int, j: int) -> float:
        if i < 0 or j < 0:
            return 0.0
        return float(np.minimum(exp[i], exp[j]) @ logs)

    for rnd in range(rounds):
        improved = 0
        for i in range(n):
            j = int(mate[i])
            if j < 0 or i > j:
                continue
            w_ij = w(i, j)
            for c in top[i]:
                if c == i or c == j:
                    continue
                d = int(mate[c])
                if d < 0:
                    w_ic = w(i, c)
                    if w_ic > w_ij + 1e-12:
                        mate[i] = c
                        mate[c] = i
                        mate[j] = -1
                        j = c
                        w_ij = w_ic
                        improved += 1
                    continue
                if d == i:
                    continue
                w_cd = w(c, d)
                base = w_ij + w_cd
                g1 = w(i, c) + w(j, d)
                g2 = w(i, d) + w(j, c)
                if g1 >= g2 and g1 > base + 1e-12:
                    mate[i] = c
                    mate[c] = i
                    mate[j] = d
                    mate[d] = j
                    j = c
                    w_ij = w(i, c)
                    improved += 1
                elif g2 > base + 1e-12:
                    mate[i] = d
                    mate[d] = i
                    mate[j] = c
                    mate[c] = j
                    j = d
                    w_ij = w(i, d)
                    improved += 1
            # also try top partners of j
            for c in top[j]:
                if c == i or c == j:
                    continue
                d = int(mate[c])
                if d < 0:
                    w_jc = w(j, c)
                    if w_jc > w_ij + 1e-12:
                        mate[j] = c
                        mate[c] = j
                        mate[i] = -1
                        i, j = j, c
                        w_ij = w_jc
                        improved += 1
                    continue
                if d == j:
                    continue
                w_cd = w(c, d)
                base = w_ij + w_cd
                g1 = w(j, c) + w(i, d)
                g2 = w(j, d) + w(i, c)
                if g1 >= g2 and g1 > base + 1e-12:
                    mate[j] = c
                    mate[c] = j
                    mate[i] = d
                    mate[d] = i
                    i, j = (i, j) if i < j else (j, i)
                    j = int(mate[i])
                    w_ij = w(i, j)
                    improved += 1
                elif g2 > base + 1e-12:
                    mate[j] = d
                    mate[d] = j
                    mate[i] = c
                    mate[c] = i
                    j = int(mate[i])
                    w_ij = w(i, j)
                    improved += 1
        print(f"    2-opt round {rnd + 1}: {improved} improvements", flush=True)
        if improved == 0:
            break

    seen = set()
    out: list[tuple[int, int]] = []
    for i in range(n):
        j = int(mate[i])
        if j > i and (i, j) not in seen:
            seen.add((i, j))
            out.append((i, j))
    return out


def solve_small(nums: list[int]) -> list[tuple[int, int]]:
    n = len(nums)
    wmat = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            g = gcd(nums[i], nums[j])
            if g > 1:
                val = log10_int(g)
                wmat[i, j] = wmat[j, i] = val
    edges = [(float(wmat[i, j]), i, j) for i in range(n) for j in range(i + 1, n) if wmat[i, j] > 0]
    best_pairs = greedy_matching(n, edges)
    best_score = sum(wmat[i, j] for i, j in best_pairs)

    rng = np.random.default_rng(123)
    for t in range(40):
        noisy = [(w + float(rng.normal(0, 0.15)), i, j) for w, i, j in edges]
        pairs = greedy_matching(n, noisy)
        # restore true greedy among remaining with original weights
        used = [False] * n
        for i, j in pairs:
            used[i] = used[j] = True
        for w, i, j in sorted(edges, reverse=True):
            if not used[i] and not used[j]:
                used[i] = used[j] = True
                pairs.append((i, j))
        sc = sum(wmat[i, j] for i, j in pairs)
        if sc > best_score:
            best_score = sc
            best_pairs = pairs

    pairs = list(best_pairs)
    unused = [i for i in range(n) if all(i not in p for p in pairs)]
    # dense 2-opt
    for _ in range(30):
        improved = False
        # pair unused
        for a in range(len(unused)):
            for b in range(a + 1, len(unused)):
                u, v = unused[a], unused[b]
                if wmat[u, v] > 0:
                    pairs.append((u, v))
                    unused = [x for x in unused if x not in (u, v)]
                    improved = True
                    break
            if improved:
                break
        for pi, (a, b) in enumerate(pairs):
            wab = wmat[a, b]
            for ui, u in enumerate(unused):
                if wmat[u, a] > wab + 1e-15:
                    pairs[pi] = (u, a)
                    unused[ui] = b
                    a, b = u, a
                    wab = wmat[a, b]
                    improved = True
                elif wmat[u, b] > wab + 1e-15:
                    pairs[pi] = (u, b)
                    unused[ui] = a
                    a, b = u, b
                    wab = wmat[a, b]
                    improved = True
        for p in range(len(pairs)):
            a, b = pairs[p]
            w0ab = wmat[a, b]
            for q in range(p + 1, len(pairs)):
                c, d = pairs[q]
                base = w0ab + wmat[c, d]
                w1 = wmat[a, c] + wmat[b, d]
                w2 = wmat[a, d] + wmat[b, c]
                if w1 >= w2 and w1 > base + 1e-15:
                    pairs[p] = (a, c)
                    pairs[q] = (b, d)
                    a, b = pairs[p]
                    w0ab = wmat[a, b]
                    improved = True
                elif w2 > base + 1e-15:
                    pairs[p] = (a, d)
                    pairs[q] = (b, c)
                    a, b = pairs[p]
                    w0ab = wmat[a, b]
                    improved = True
        if not improved:
            break
    return pairs


def solve_large(nums: list[int], k: int) -> list[tuple[int, int]]:
    print("  building prime basis…", flush=True)
    t0 = time.time()
    primes = unique_primes(build_raw_basis(nums))
    print(f"  primes={len(primes)}  ({time.time() - t0:.1f}s)", flush=True)
    print("  factoring…", flush=True)
    exp = factor_matrix(nums, primes)
    logs = np.array([math.log10(p) for p in primes], dtype=np.float64)
    print(f"  mean omega={exp.astype(bool).sum(axis=1).mean():.2f}", flush=True)
    print(f"  collecting top-{k} candidate edges…", flush=True)
    edges, top = collect_topk_edges(exp, logs, k=k)
    print(f"  greedy matching on {len(edges)} edges…", flush=True)
    pairs = greedy_matching(len(nums), edges)
    print(f"  greedy pairs={len(pairs)}  weight={sum(pair_log_weight(exp, logs, i, j) for i, j in pairs):.6f}", flush=True)
    pairs = local_2opt(exp, logs, pairs, top)
    print(f"  after 2-opt weight={sum(pair_log_weight(exp, logs, i, j) for i, j in pairs):.6f}", flush=True)
    pairs = pair_unused(exp, logs, pairs)
    return pairs


def solve(nums: list[int]) -> list[tuple[int, int]]:
    n = len(nums)
    if n <= 250:
        return solve_small(nums)
    k = 80 if n <= 15000 else 50
    return solve_large(nums, k=k)


def validate(nums: list[int], pairs: list[tuple[int, int]]) -> None:
    seen: set[int] = set()
    values = set(nums)
    for i, j in pairs:
        a, b = nums[i], nums[j]
        if a not in values or b not in values:
            raise ValueError("pair uses a missing value")
        if a == b:
            raise ValueError("pair uses the same element twice")
        if a in seen or b in seen:
            raise ValueError("element reused in another pair")
        seen.add(a)
        seen.add(b)


def main() -> None:
    root = Path(__file__).resolve().parent
    weights: list[float] = []
    for k in (1, 2, 3):
        src = root / f"task{k}.txt"
        dst = root / f"ans{k}.txt"
        print(f"\n=== task{k}.txt ===", flush=True)
        t0 = time.time()
        nums = load_task(src)
        print(f"  n={len(nums)}  max_digits={len(str(max(nums)))}", flush=True)
        pairs = solve(nums)
        validate(nums, pairs)
        s = pair_weight(nums, pairs)
        weights.append(s)
        write_answer(dst, nums, pairs)
        print(
            f"  pairs={len(pairs)}  weight S{k}={s:.9f}  time={time.time() - t0:.1f}s",
            flush=True,
        )
        print(f"  wrote {dst.name}", flush=True)

    s1, s2, s3 = weights
    total = 2 * s1 + 8 * s2 + 20 * s3
    print("\n=== score ===")
    print(f"S1 = {s1:.12f}")
    print(f"S2 = {s2:.12f}")
    print(f"S3 = {s3:.12f}")
    print(f"2*S1 + 8*S2 + 20*S3 = {total:.12f}")


if __name__ == "__main__":
    sys.set_int_max_str_digits(0)
    main()
