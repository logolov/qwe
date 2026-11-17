import numpy as np
import random
import math
import sys

def solve_task(filename):
    # 1. Чтение данных
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    n = int(lines[0])
    
    # Парсинг матриц
    C = np.array([list(map(int, lines[i].split())) for i in range(1, n+1)], dtype=np.int64)
    F = np.array([list(map(int, lines[i].split())) for i in range(n+1, 2*n+1)], dtype=np.int64)
    D = np.array([list(map(int, lines[i].split())) for i in range(2*n+1, 3*n+1)], dtype=np.int64)
    
    # Предвычисление симметричной части потока для ускорения
    # В задаче QAP часто F и D симметричны, но здесь читаем как есть.
    # Оптимизация: precompute interaction costs
    
    def calc_cost(perm):
        """Полный расчет стоимости (используется редко)"""
        p = perm - 1  # 0-based indices
        cost = np.sum(C[p, np.arange(n)])
        # Transport: sum(F[p[i], p[j]] * D[i, j])
        # Vectorized calculation
        flow_matrix = F[np.ix_(p, p)]
        cost += np.sum(flow_matrix * D)
        return cost

    def get_delta(perm, r, s, current_cost=None):
        """
        Точный расчет изменения стоимости при обмене позиций r и s.
        Сложность O(N) вместо O(N^2).
        """
        u = perm[r] - 1  # предприятие на позиции r
        v = perm[s] - 1  # предприятие на позиции s
        
        # 1. Изменение стоимости размещения
        delta = (C[v, r] + C[u, s]) - (C[u, r] + C[v, s])
        
        # 2. Изменение стоимости перевозок
        # Взаимодействие между самими позициями r и s
        delta += (F[v, u] - F[u, v]) * D[r, s]
        delta += (F[u, v] - F[v, u]) * D[s, r]
        
        # Взаимодействие с остальными позициями k
        # Используем векторизацию для цикла по k
        mask = np.ones(n, dtype=bool)
        mask[r] = False
        mask[s] = False
        
        k_indices = np.where(mask)[0]
        w = perm[k_indices] - 1  # предприятия на остальных позициях
        
        # Потоки, связанные с позицией r (было u, стало v)
        # От/к другим предприятиям w через расстояния D[k, r] и D[r, k]
        dr_k = D[r, k_indices]  # D[r][k]
        dk_r = D[k_indices, r]  # D[k][r]
        
        delta += np.sum((F[v, w] - F[u, w]) * dr_k)
        delta += np.sum((F[w, v] - F[w, u]) * dk_r)
        
        # Потоки, связанные с позицией s (было v, стало u)
        ds_k = D[s, k_indices]  # D[s][k]
        dk_s = D[k_indices, s]  # D[k][s]
        
        delta += np.sum((F[u, w] - F[v, w]) * ds_k)
        delta += np.sum((F[w, u] - F[w, v]) * dk_s)
        
        return delta

    # 2. Алгоритм решения
    best_global_perm = None
    best_global_cost = float('inf')
    
    NUM_RUNS = 5
    
    for run in range(NUM_RUNS):
        random.seed(run * 997 + 42)
        np.random.seed(run * 997 + 42)
        
        # Инициализация: случайная перестановка
        perm = np.arange(1, n + 1)
        np.random.shuffle(perm)
        
        cur_cost = calc_cost(perm)
        best_perm = perm.copy()
        best_cost = cur_cost
        
        # Фаза 1: Локальный спуск (First Improvement) для быстрого выхода в "яму"
        improved = True
        while improved:
            improved = False
            indices = list(range(n))
            random.shuffle(indices)
            for i in indices:
                found_better = False
                js = list(range(i+1, n))
                random.shuffle(js)
                for j in js:
                    delta = get_delta(perm, i, j)
                    if delta < 0:
                        perm[i], perm[j] = perm[j], perm[i]
                        cur_cost += delta
                        if cur_cost < best_cost:
                            best_cost = cur_cost
                            best_perm = perm.copy()
                        improved = True
                        found_better = True
                        break
                if found_better:
                    break
        
        # Фаза 2: Имитационный отжиг для выхода из локального минимума
        temp = best_cost * 0.002 / max(1, math.log(n)) 
        cooling = 0.9999
        min_temp = 1e-8
        
        t = temp
        no_improve_count = 0
        max_no_improve = n * 10
        
        while t > min_temp and no_improve_count < max_no_improve:
            i, j = random.sample(range(n), 2)
            delta = get_delta(perm, i, j)
            
            if delta < 0 or random.random() < math.exp(-delta / t):
                perm[i], perm[j] = perm[j], perm[i]
                cur_cost += delta
                
                if cur_cost < best_cost:
                    best_cost = cur_cost
                    best_perm = perm.copy()
                    no_improve_count = 0
                else:
                    pass # accepted worse solution
            else:
                no_improve_count += 1
                
            t *= cooling
            
        if best_cost < best_global_cost:
            best_global_cost = best_cost
            best_global_perm = best_perm.copy()

    return ' '.join(map(str, best_global_perm))

if __name__ == "__main__":
    # Решаем только task3.txt как запрошено
    print(solve_task('task3.txt'))