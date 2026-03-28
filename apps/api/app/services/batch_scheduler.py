from __future__ import annotations

from collections import defaultdict, deque


class BatchScheduler:
    def build_batches(self, nodes: list[dict], edges: list[tuple[str, str]]) -> list[list[str]]:
        indegree: dict[str, int] = {node["id"]: 0 for node in nodes}
        outgoing: dict[str, list[str]] = defaultdict(list)
        batch_index: dict[str, int] = {node["id"]: 0 for node in nodes}

        for source, target in edges:
            outgoing[source].append(target)
            indegree[target] += 1

        queue = deque([node_id for node_id, degree in indegree.items() if degree == 0])
        ordered: list[str] = []

        while queue:
            current = queue.popleft()
            ordered.append(current)
            for neighbor in outgoing[current]:
                batch_index[neighbor] = max(batch_index[neighbor], batch_index[current] + 1)
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        grouped: dict[int, list[str]] = defaultdict(list)
        for node_id in ordered:
            grouped[batch_index[node_id]].append(node_id)
        return [grouped[index] for index in sorted(grouped)]
