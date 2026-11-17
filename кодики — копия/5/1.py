from collections import defaultdict

def read_graph(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    n, m = map(int, lines[0].split())
    adj = defaultdict(set)

    for line in lines[1:]:
        u, v = map(int, line.split())
        adj[u].add(v)
        adj[v].add(u)

    return n, adj


def dsatur_coloring(n, adj):
    colors = [0] * (n + 1)
    saturation = [set() for _ in range(n + 1)]
    degrees = [len(adj[v]) for v in range(n + 1)]
    uncolored = set(range(1, n + 1))
    max_color = 0

    while uncolored:
        v = max(
            uncolored,
            key=lambda x: (len(saturation[x]), degrees[x], -x)
        )

        used_colors = saturation[v]
        color = 1

        while color in used_colors:
            color += 1

        colors[v] = color
        max_color = max(max_color, color)
        uncolored.remove(v)

        for neighbor in adj[v]:
            if colors[neighbor] == 0:
                saturation[neighbor].add(color)

    return max_color, colors


def is_correct(n, adj, colors):
    for v in range(1, n + 1):
        for u in adj[v]:
            if colors[v] == colors[u]:
                return False
    return True


def main():
    n, adj = read_graph("task1.txt")

    color_count, colors = dsatur_coloring(n, adj)

    if not is_correct(n, adj, colors):
        print("Ошибка: раскраска некорректна")

    print(color_count)
    print(*colors[1:])


if __name__ == "__main__":
    main()