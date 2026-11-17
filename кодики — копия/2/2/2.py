import sys

# Увеличиваем лимит рекурсии для глубокого поиска
sys.setrecursionlimit(2000)

def solve_large_mwis():
    with open("task2.txt", "r") as f:
        input_data = f.read().split()

    if not input_data:
        return

    n = int(input_data[0])
    weights = [int(x) for x in input_data[1:n+1]]
    m = int(input_data[n+1])
    
    # Строим список смежности и считаем степени вершин
    adj = {i: set() for i in range(1, n + 1)}
    idx = n + 2
    for _ in range(m):
        u = int(input_data[idx])
        v = int(input_data[idx+1])
        adj[u].add(v)
        adj[v].add(u)
        idx += 2

    # Сортируем вершины по возрастанию степени (эвристика для ускорения)
    deg = {i: len(adj[i]) for i in range(1, n + 1)}
    vertices = sorted(range(1, n + 1), key=lambda x: deg[x])

    best_weight = 0
    best_vertices = []

    # Предрасчет максимального возможного остаточного веса для отсечений
    suffix_max = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        v = vertices[i]
        suffix_max[i] = suffix_max[i+1] + weights[v-1]

    def branch_and_bound(idx, current_weight, current_set, forbidden_set):
        nonlocal best_weight, best_vertices

        if current_weight > best_weight:
            best_weight = current_weight
            best_vertices = list(current_set)

        if idx >= n:
            return

        # Отсечение ветвей: если даже со всеми оставшимися вершинами мы не побьем рекорд
        if current_weight + suffix_max[idx] <= best_weight:
            return

        v = vertices[idx]

        # Вариант 1: Берем текущую вершину v (если она доступна)
        if v not in forbidden_set:
            new_forbidden = forbidden_set | adj[v]
            current_set.append(v)
            branch_and_bound(idx + 1, current_weight + weights[v - 1], current_set, new_forbidden)
            current_set.pop()

        # Вариант 2: Пропускаем текущую вершину v
        branch_and_bound(idx + 1, current_weight, current_set, forbidden_set)

    branch_and_bound(0, 0, [], set())

    print(best_weight)
    print(sorted(best_vertices))

if __name__ == "__main__":
    solve_large_mwis()
