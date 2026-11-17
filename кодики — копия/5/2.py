import random
import sys

# Увеличиваем лимит рекурсии на всякий случай
sys.setrecursionlimit(2000)

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

def count_conflicts(n, adj, colors):
    conflicts = 0
    for u in range(1, n + 1):
        for v in adj[u]:
            if u < v and colors[u] == colors[v]:
                conflicts += 1
    return conflicts

def get_conflict_vertices(n, adj, colors):
    conflict_verts = set()
    for u in range(1, n + 1):
        for v in adj[u]:
            if u < v and colors[u] == colors[v]:
                conflict_verts.add(u)
                conflict_verts.add(v)
    return list(conflict_verts)

def rlf_coloring(n, adj):
    """Recursive Largest First - быстрая эвристика для плотных графов"""
    colors = [0] * (n + 1)
    uncolored = set(range(1, n + 1))
    color_count = 0
    
    while uncolored:
        color_count += 1
        # Выбираем вершину с макс. степенью в оставшемся подграфе
        u = max(uncolored, key=lambda x: len(adj[x] & uncolored))
        colors[u] = color_count
        uncolored.remove(u)
        
        # Вершины, которые можно покрасить в этот же цвет (не смежные с u)
        candidates = uncolored - adj[u]
        
        while candidates:
            # Выбираем вершину, у которой больше всего соседей, которые НЕ могут быть покрашены в этот цвет
            v = max(candidates, key=lambda x: len(adj[x] - candidates))
            colors[v] = color_count
            uncolored.remove(v)
            # Исключаем v и его соседей из кандидатов
            candidates -= (adj[v] | {v})
            
    return color_count, colors

def tabu_search(n, adj, target_k, initial_colors, max_iter=15000):
    """
    Локальный поиск с запретами для минимизации конфликтов при фиксированном количестве цветов target_k.
    """
    # Нормализуем цвета, чтобы они были в диапазоне [1, target_k]
    current_colors = [max(1, min(target_k, c)) for c in initial_colors]
    
    best_colors = current_colors[:]
    best_conflicts = count_conflicts(n, adj, current_colors)
    
    if best_conflicts == 0:
        return True, best_colors
        
    tabu_tenure = 10
    tabu_list = {} # (vertex, color) -> iteration_until_tabu
    
    iterations_without_improvement = 0
    
    for i in range(max_iter):
        if best_conflicts == 0:
            return True, best_colors
            
        conflict_verts = get_conflict_vertices(n, adj, current_colors)
        if not conflict_verts:
            break
            
        # Выбираем случайную конфликтующую вершину
        v = random.choice(conflict_verts)
        
        best_move_color = current_colors[v]
        min_delta = float('inf')
        
        # Оцениваем все возможные цвета для вершины v
        for c in range(1, target_k + 1):
            if c == current_colors[v]:
                continue
                
            old_color = current_colors[v]
            
            # Считаем изменение конфликтов
            delta = 0
            for nb in adj[v]:
                if current_colors[nb] == c:
                    delta += 1
                if current_colors[nb] == old_color:
                    delta -= 1
                    
            # Добавляем небольшой рандом, чтобы избежать плато
            score = delta + random.uniform(-0.1, 0.1)
            
            if score < min_delta:
                # Если не табу или аспирация
                if (v, c) not in tabu_list or tabu_list[(v, c)] <= i or (count_conflicts(n, adj, current_colors) + delta < best_conflicts):
                    min_delta = score
                    best_move_color = c
        
        # Делаем ход
        old_color = current_colors[v]
        current_colors[v] = best_move_color
        tabu_list[(v, old_color)] = i + tabu_tenure
        
        current_conflicts = count_conflicts(n, adj, current_colors)
        
        if current_conflicts < best_conflicts:
            best_conflicts = current_conflicts
            best_colors = current_colors[:]
            iterations_without_improvement = 0
        else:
            iterations_without_improvement += 1
            
        if iterations_without_improvement > 2000:
            # Перезапуск из лучшего найденного, если застряли
            current_colors = best_colors[:]
            iterations_without_improvement = 0
            tabu_list.clear()
            
    return best_conflicts == 0, best_colors

def solve():
    filename = "task2.txt"
    n, adj = read_graph(filename)
    
    # 1. Получаем начальную оценку
    initial_k, initial_colors = rlf_coloring(n, adj)
    
    best_valid_k = initial_k
    best_valid_colors = initial_colors[:]
    
    # Мы хотим попробовать уменьшить количество цветов до 14
    # Начинаем с текущего лучшего и идем вниз
    start_target = min(initial_k, 16) # Ограничиваем сверху для скорости
    
    # Пробуем K от start_target вниз до 14
    for k in range(start_target, 13, -1):
        success = False
        
        # Для каждого K делаем несколько попыток с разным рандомом
        attempts = 15 if k >= 15 else 25
        
        for attempt in range(attempts):
            # Небольшая модификация начального решения для разнообразия
            start_cols = initial_colors[:]
            if attempt > 0:
                for _ in range(n // 10):
                    vv = random.randint(1, n)
                    start_cols[vv] = random.randint(1, k)
            
            is_valid, final_cols = tabu_search(n, adj, k, start_cols, max_iter=20000)
            
            if is_valid:
                # Проверяем корректность (на всякий случай)
                if count_conflicts(n, adj, final_cols) == 0:
                    best_valid_k = k
                    best_valid_colors = final_cols[:]
                    success = True
                    break
        
        if success:
            # Если нашли для K, пробуем дальше уменьшить (K-1)
            initial_colors = best_valid_colors[:] # Используем успешное решение как старт для следующего
            continue
        else:
            # Если не смогли найти для K, останавливаемся, так как меньшие K будут ещё сложнее
            break

    # Вывод результата
    print(best_valid_k)
    print(*best_valid_colors[1:])

if __name__ == "__main__":
    solve()