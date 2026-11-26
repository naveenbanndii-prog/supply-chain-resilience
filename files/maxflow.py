"""Edmonds-Karp max-flow (stdlib only)."""
from collections import defaultdict, deque


def max_flow(capacities, source, sink):
    """capacities: dict[(u, v)] -> capacity. Returns the max flow value."""
    graph = defaultdict(set)
    residual = defaultdict(float)
    for (u, v), c in capacities.items():
        graph[u].add(v)
        graph[v].add(u)
        residual[(u, v)] += c

    total = 0.0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in graph[u]:
                if v not in parent and residual[(u, v)] > 1e-9:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            return total

        bottleneck, v = float("inf"), sink
        while parent[v] is not None:
            bottleneck = min(bottleneck, residual[(parent[v], v)])
            v = parent[v]
        v = sink
        while parent[v] is not None:
            u = parent[v]
            residual[(u, v)] -= bottleneck
            residual[(v, u)] += bottleneck
            v = u
        total += bottleneck
