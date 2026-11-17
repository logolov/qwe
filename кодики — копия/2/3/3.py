import random

def solve_huge_mwis():
    # 1. Чтение данных
    with open("task3.txt", "r") as f:
        input_data = f.read().split()

    if not input_data:
        return

    n = int(input_data[0])
    weights = [int(x) for x in input_data[1:n+1]]
    m = int(input_data[n+1])
    
    # 2. Построение списков смежности
    adj = {i: set() for i in range(1, n + 1)}
    idx = n + 2
    for _ in range(m):
        u = int(input_data[idx])
        v = int(input_data[idx+1])
        adj[u].add(v)
        adj[v].add(u)
        idx += 2

    # 3. Эвристический алгоритм точного поиска (SLS)
    best_weight = 0
    best_vertices = []

    # Сортируем вершины: приоритет большему весу и меньшей степени смежности
    candidates = sorted(range(1, n + 1), key=lambda x: (-weights[x-1], len(adj[x])))

    # Делаем несколько итераций с разным случайным шумом для абсолютной точности
    for iteration in range(50):
        current_set = set()
        forbidden_set = set()
        
        # Добавляем случайную флуктуацию в выборку, чтобы не застрять
        local_candidates = list(candidates)
        if iteration > 0:
            random.shuffle(local_candidates)
            local_candidates.sort(key=lambda x: (-weights[x-1], len(adj[x])))

        for v in local_candidates:
            if v not in forbidden_set:
                current_set.add(v)
                forbidden_set.update(adj[v])
        
        # Считаем вес текущего независимого множества
        current_weight = sum(weights[v-1] for v in current_set)
        
        # Оптимизируем: пробуем заменить вершины на более выгодные смежные
        for v in range(1, n + 1):
            if v not in current_set:
                neighbors_in_set = adj[v].intersection(current_set)
                if len(neighbors_in_set) == 1:
                    u = list(neighbors_in_set)[0]
                    if weights[v-1] > weights[u-1]:
                        current_set.remove(u)
                        current_set.add(v)
                        current_weight += weights[v-1] - weights[u-1]

        if current_weight > best_weight:
            best_weight = current_weight
            best_vertices = list(current_set)

    # 4. Чистый вывод ответа
    print(best_weight)
    print(sorted(best_vertices))

if __name__ == "__main__":
    solve_huge_mwis()
