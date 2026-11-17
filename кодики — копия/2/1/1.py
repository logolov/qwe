def solve_mwis():
    with open("task1.txt", "r") as f:
        input_data = f.read().split()

    n = int(input_data[0])
    weights = [int(x) for x in input_data[1:n+1]]
    m = int(input_data[n+1])
    
    adj = {i: set() for i in range(1, n + 1)}
    idx = n + 2
    for _ in range(m):
        u = int(input_data[idx])
        v = int(input_data[idx+1])
        adj[u].add(v)
        adj[v].add(u)
        idx += 2

    best_weight = 0
    best_vertices = []

    def backtrack(v, current_weight, current_set, forbidden_set):
        nonlocal best_weight, best_vertices
        if v > n:
            if current_weight > best_weight:
                best_weight = current_weight
                best_vertices = list(current_set)
            return

        backtrack(v + 1, current_weight, current_set, forbidden_set)

        if v not in forbidden_set:
            backtrack(v + 1, current_weight + weights[v - 1], current_set + [v], forbidden_set | adj[v])

    backtrack(1, 0, [], set())

    print(best_weight)
    print(best_vertices)

if __name__ == "__main__":
    solve_mwis()
