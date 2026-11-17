import itertools

def solve(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    n = int(lines[0])
    C = [list(map(int, lines[i].split())) for i in range(1, n+1)]
    F = [list(map(int, lines[i].split())) for i in range(n+1, 2*n+1)]
    D = [list(map(int, lines[i].split())) for i in range(2*n+1, 3*n+1)]
    
    best_perm = None
    best_cost = float('inf')
    
    for perm in itertools.permutations(range(1, n+1)):
        cost = sum(C[perm[i]-1][i] for i in range(n))
        cost += sum(F[perm[i]-1][perm[j]-1] * D[i][j] 
                   for i in range(n) for j in range(n) if i != j)
        
        if cost < best_cost:
            best_cost = cost
            best_perm = perm
    
    return ' '.join(map(str, best_perm))

# Решаем только первую задачу
result = solve('task1.txt')
print(result)