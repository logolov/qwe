import sys
import random

sys.setrecursionlimit(10000)

def read_graph(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    n, m = map(int, lines[0].split())
    adj = [set() for _ in range(n + 1)]
    
    for line in lines[1:]:
        u, v = map(int, line.split())
        adj[u].add(v)
        adj[v].add(u)
        
    return n, adj

def rlf_coloring(n, adj):
    """Recursive Largest First"""
    colors = [0] * (n + 1)
    uncolored = set(range(1, n + 1))
    color_count = 0
    
    while uncolored:
        color_count += 1
        # Выбираем вершину с макс. степенью в оставшемся подграфе
        u = max(uncolored, key=lambda x: len(adj[x] & uncolored))
        colors[u] = color_count
        uncolored.remove(u)
        
        # Вершины, которые можно покрасить в этот же цвет
        candidates = uncolored - adj[u]
        
        while candidates:
            # Выбираем вершину, у которой больше всего соседей вне candidates
            v = max(candidates, key=lambda x: len(adj[x] - candidates))
            colors[v] = color_count
            uncolored.remove(v)
            candidates -= (adj[v] | {v})
            
    return color_count, colors

def greedy_coloring(n, adj, order):
    colors = [0] * (n + 1)
    for v in order:
        used = set(colors[nb] for nb in adj[v] if colors[nb] != 0)
        c = 1
        while c in used:
            c += 1
        colors[v] = c
    return max(colors), colors

def solve():
    filename = "task3.txt"
    n, adj = read_graph(filename)
    
    # 1. RLF
    k1, cols1 = rlf_coloring(n, adj)
    
    # 2. Жадный (по убыванию степени)
    order_deg = sorted(range(1, n + 1), key=lambda x: len(adj[x]), reverse=True)
    k2, cols2 = greedy_coloring(n, adj, order_deg)
    
    # 3. Жадный (случайный порядок, несколько попыток)
    best_k = min(k1, k2)
    best_colors = cols1 if k1 < k2 else cols2
    
    for _ in range(10): # 10 попыток случайного порядка
        order_rand = list(range(1, n + 1))
        random.shuffle(order_rand)
        k_rand, cols_rand = greedy_coloring(n, adj, order_rand)
        if k_rand < best_k:
            best_k = k_rand
            best_colors = cols_rand
            
    # 4. Попытка улучшения (Local Search)
    # Пробуем перекрасить вершины в меньшие цвета
    improved = True
    while improved:
        improved = False
        # Проходим по вершинам в случайном порядке
        vertices = list(range(1, n + 1))
        random.shuffle(vertices)
        
        for v in vertices:
            current_color = best_colors[v]
            # Пробуем цвета от 1 до current_color - 1
            for c in range(1, current_color):
                # Проверяем, можно ли покрасить в c
                can_use = True
                for nb in adj[v]:
                    if best_colors[nb] == c:
                        can_use = False
                        break
                
                if can_use:
                    best_colors[v] = c
                    improved = True
                    # Обновляем best_k если нужно (хотя мы только уменьшаем цвета)
                    break
    
    # Пересчитываем реальное количество цветов
    final_k = max(best_colors)
    
    print(final_k)
    print(*best_colors[1:])

if __name__ == "__main__":
    solve()