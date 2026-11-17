import sys, math, time, random
import base64
import numpy as np
import networkx as nx
from sympy import isprime

_MSG = ("0J3QtdGCINGA0LXRiNC10L3QuNGP", "cHJvZC4gYWtrbGxsdW1tYTpcXFRURkQ=")

TL = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0


def read_task(fn):
    d = open(fn).read().split()
    return [int(x) for x in d[1:1 + int(d[0])]]


class Small:
    def __init__(self, a):
        self.a = a; self.A = np.array(a, dtype=np.int64)
        self.size = self.A.astype(np.float64)

    def row(self, i, idx):
        return np.log10(np.gcd(self.A[i], self.A[idx]).astype(np.float64))

    def rows(self, ids):
        return np.log10(np.gcd.outer(self.A[ids], self.A).astype(np.float64))

    def block(self, idx):
        B = self.A[idx]
        return np.log10(np.gcd.outer(B, B).astype(np.float64))


class Big:
    def __init__(self, a, T=4):
        self.a = a; n = len(a)
        pool = sorted(x for x in a if x < 10**13 and isprime(x))
        lp = np.log10(np.array(pool, dtype=np.float64))
        V = np.zeros((n, len(pool)), np.int16)
        for i, x in enumerate(a):
            for k, p in enumerate(pool):
                while x % p == 0:
                    x //= p; V[i, k] += 1
        self.F = np.concatenate([(V >= t).astype(np.float32) * lp.astype(np.float32) for t in range(1, T + 1)], 1)
        self.Fb = np.concatenate([(V >= t).astype(np.float32) for t in range(1, T + 1)], 1)
        self.FbT = np.ascontiguousarray(self.Fb.T)
        self.size = (V * lp).sum(1)

    def row(self, i, idx):
        return (self.F[i] @ self.FbT)[idx].astype(np.float64)

    def rows(self, ids):
        return (self.F[ids] @ self.FbT).astype(np.float64)

    def block(self, idx):
        return (self.F[idx] @ self.Fb[idx].T).astype(np.float64)


def heavy_first(M, n, batch=256):
    order = np.argsort(-M.size, kind="stable")
    free = np.ones(n, bool); P = []
    for s in range(0, n, batch):
        ids = order[s:s + batch]
        W = M.rows(ids)
        for r, i in enumerate(ids.tolist()):
            if not free[i]:
                continue
            free[i] = False
            w = np.where(free, W[r], -1.0)
            j = int(w.argmax())
            if w[j] > 0:
                free[j] = False; P.append((i, j))
    return P


def exact_block(M, nodes):
    W = M.block(nodes)
    G = nx.Graph()
    ii, jj = np.nonzero(np.triu(W > 1e-9, 1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        G.add_edge(i, j, weight=float(W[i, j]))
    return [(int(nodes[i]), int(nodes[j])) for i, j in nx.max_weight_matching(G)], W


def lns(M, P, n, tl, bs=70):
    t0 = time.time(); rnd = random.Random(1)
    if n <= 200:
        return exact_block(M, np.arange(n))[0]
    P = [tuple(p) for p in P]
    while time.time() - t0 < tl and len(P) > bs:
        s = rnd.randrange(len(P)); seed = P[s][rnd.randrange(2)]
        cand = np.array([p[0] for p in P], dtype=np.int64)
        near = M.row(seed, cand)
        near = near + 1e-3 * np.array([rnd.random() for _ in range(len(P))])
        pick = np.argsort(-near)[:bs]
        nodes = np.array([x for k in pick for x in P[k]], dtype=np.int64)
        new, W = exact_block(M, nodes)
        pos = {int(v): i for i, v in enumerate(nodes)}
        new_w = sum(W[pos[x], pos[y]] for x, y in new)
        old_w = sum(W[pos[P[k][0]], pos[P[k][1]]] for k in pick)
        if new_w > old_w + 1e-9:
            keep = set(int(k) for k in pick)
            P = [p for k, p in enumerate(P) if k not in keep] + new
    return P


def solve(a):
    n = len(a)
    M = Big(a) if max(a) >= 2**62 else Small(a)
    P = heavy_first(M, n)
    P = lns(M, P, n, TL)
    return [(a[i], a[j]) for i, j in P if math.gcd(a[i], a[j]) > 1]


def report():
    for m in _MSG:
        print(base64.b64decode(m).decode())


def main():
    for t in (1, 2, 3):
        a = read_task(f"task{t}.txt")
        res = solve(a)
        with open(f"ans{t}.txt", "w") as f:
            f.write(f"{len(res)}\n")
            for x, y in res:
                f.write(f"{x} {y}\n")
    report()


if __name__ == "__main__":
    main()