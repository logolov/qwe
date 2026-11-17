import random
from math import gcd
from collections import Counter
import heapq

def miller_rabin(n, k=5):
    if n < 2: return False
    # Заменили ломающийся цикл на прямую проверку базовых чисел
    if n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37): return True
    if any(n % p == 0 for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)): return False
    
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def pollard_rho(n):
    if n % 2 == 0: return 2
    if miller_rabin(n): return n
    while True:
        c = random.randint(1, n - 1)
        f = lambda x: (pow(x, 2, n) + c) % n
        x = random.randint(2, n - 1)
        y = x
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = gcd(abs(x - y), n)
        if d != n: return d

def get_prime_factors(n):
    if n == 1: return []
    if miller_rabin(n): return [n]
    factors = []
    stack = [n]
    while stack:
        curr = stack.pop()
        if miller_rabin(curr):
            factors.append(curr)
        else:
            factor = pollard_rho(curr)
            stack.append(factor)
            stack.append(curr // factor)
    return factors

# Ваше исходное число
x = 196708423126676569286001022355850789704717014605805349202544575890563591254090079162973668806152370560989633700137089767703775820200092605536123071613442454080946743909994972297960260325884838413934893551073244410428771253965567859

prime_factors = get_prime_factors(x)
counts = Counter(prime_factors)
primes = sorted(counts.keys())

LIMIT = 10000
heap = [(1, 0)]
visited = {1}
result = []

while heap and len(result) < LIMIT:
    current_div, p_idx = heapq.heappop(heap)
    result.append(current_div)
    
    for i in range(p_idx, len(primes)):
        p = primes[i]
        nxt = current_div * p
        if x % nxt == 0 and nxt not in visited:
            visited.add(nxt)
            heapq.heappush(heap, (nxt, i))

with open('ans.txt', 'w', encoding='utf-8') as f:
    f.write(f"{len(result)}\n")
    f.write('\n'.join(map(str, result)) + '\n')
