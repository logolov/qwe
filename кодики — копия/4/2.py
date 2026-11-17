import random
import math

def read_task(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    n = int(lines[0])
    C = [list(map(int, lines[i].split())) for i in range(1, n+1)]
    F = [list(map(int, lines[i].split())) for i in range(n+1, 2*n+1)]
    D = [list(map(int, lines[i].split())) for i in range(2*n+1, 3*n+1)]
    
    return n, C, F, D

def calculate_cost(perm, C, F, D, n):
    placement_cost = sum(C[perm[i]-1][i] for i in range(n))
    transport_cost = sum(F[perm[i]-1][perm[j]-1] * D[i][j] 
                        for i in range(n) for j in range(n) if i != j)
    return placement_cost + transport_cost

def simulated_annealing(n, C, F, D, initial_temp=10000, cooling_rate=0.9995, min_temp=0.01):
    current_perm = list(range(1, n+1))
    random.shuffle(current_perm)
    current_cost = calculate_cost(current_perm, C, F, D, n)
    
    best_perm = current_perm[:]
    best_cost = current_cost
    
    temp = initial_temp
    
    while temp > min_temp:
        new_perm = current_perm[:]
        i, j = random.sample(range(n), 2)
        new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
        
        new_cost = calculate_cost(new_perm, C, F, D, n)
        delta = new_cost - current_cost
        
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_perm = new_perm
            current_cost = new_cost
            
            if current_cost < best_cost:
                best_perm = current_perm[:]
                best_cost = current_cost
        
        temp *= cooling_rate
    
    return best_perm, best_cost

def solve_task(filename):
    n, C, F, D = read_task(filename)
    
    best_overall_perm = None
    best_overall_cost = float('inf')
    
    for run in range(5):
        random.seed(run)
        perm, cost = simulated_annealing(n, C, F, D)
        
        if cost < best_overall_cost:
            best_overall_cost = cost
            best_overall_perm = perm
    
    return ' '.join(map(str, best_overall_perm))

if __name__ == "__main__":
    result = solve_task('task2.txt')
    print(result)