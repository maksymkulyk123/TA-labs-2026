"""ЛР5, варіант 7. Prim та Kruskal, неорієнтований граф.

У джерелі на с.14 відсутня вага ребра 2--5. Прийнято 8 за
дозволом примітки до таблиці варіантів. Рівні наявні ваги збережено.
Запуск: python TA_LR5_variant7.py --out results5
"""
import argparse
import json
from pathlib import Path

VERTICES = list(range(1, 9))
EDGES = [(1, 2, 2), (1, 3, 5), (1, 4, 1), (1, 7, 1),
         (2, 4, 3), (2, 5, 8), (3, 5, 2), (3, 6, 4),
         (3, 7, 4), (4, 5, 9), (4, 7, 9), (4, 8, 4),
         (5, 6, 3), (6, 8, 1), (7, 8, 6)]


def representations(vertices, edges):
    index = {v: i for i, v in enumerate(vertices)}
    matrix = [[None] * len(vertices) for _ in vertices]
    for i in range(len(vertices)):
        matrix[i][i] = 0
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        i, j = index[u], index[v]
        if matrix[i][j] is not None or u == v:
            raise ValueError("Повтор або петля")
        matrix[i][j] = matrix[j][i] = w
        adj[u].append((v, w))
        adj[v].append((u, w))
    return matrix, {v: sorted(a) for v, a in adj.items()}


def prim(vertices, edges, start=1):
    """Наочний жадібний вибір з розрізу; O(VE), журнал містить усіх кандидатів."""
    if start not in vertices:
        raise ValueError("Невідома стартова вершина")
    selected, tree, trace = {start}, [], []
    while len(selected) < len(vertices):
        cut = []
        for u, v, w in edges:
            if (u in selected) != (v in selected):
                cut.append((w, min(u, v), max(u, v)))
        if not cut:
            raise ValueError("Граф незв'язний")
        w, u, v = min(cut)
        before = sorted(selected)
        selected.update((u, v))
        tree.append((u, v, w))
        trace.append(dict(step=len(tree), before=before,
                          cut=sorted(cut), edge=(u, v, w),
                          after=sorted(selected),
                          total=sum(e[2] for e in tree)))
    return tree, trace


class DSU:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, v):
        if self.parent[v] != v:
            self.parent[v] = self.find(self.parent[v])
        return self.parent[v]

    def union(self, u, v):
        u, v = self.find(u), self.find(v)
        if u == v:
            return False
        if self.rank[u] < self.rank[v]:
            u, v = v, u
        self.parent[v] = u
        if self.rank[u] == self.rank[v]:
            self.rank[u] += 1
        return True

    def components(self):
        groups = {}
        for v in sorted(self.parent):
            groups.setdefault(self.find(v), []).append(v)
        return sorted(groups.values())


def kruskal(vertices, edges):
    dsu, tree, trace = DSU(vertices), [], []
    for u, v, w in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
        before = dsu.components()
        accepted = dsu.union(u, v)
        if accepted:
            tree.append((u, v, w))
        trace.append(dict(step=len(trace)+1, edge=(u, v, w),
                          accepted=accepted, before=before,
                          after=dsu.components(),
                          total=sum(e[2] for e in tree)))
        if len(tree) == len(vertices) - 1:
            break
    if len(tree) != len(vertices) - 1:
        raise ValueError("Граф незв'язний")
    return tree, trace


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    matrix, adj = representations(VERTICES, EDGES)
    pt, ptrace = prim(VERTICES, EDGES)
    kt, ktrace = kruskal(VERTICES, EDGES)
    result = dict(vertices=VERTICES, edges=EDGES, matrix=matrix,
                  adjacency=adj, prim=pt, prim_trace=ptrace,
                  kruskal=kt, kruskal_trace=ktrace,
                  total=sum(e[2] for e in pt))
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    lines = ["Варіант 7; вага 2--5 доповнена: 8", "Prim"]
    lines += [str(s) for s in ptrace]
    lines += ["Kruskal"] + [str(s) for s in ktrace]
    lines += ["Prim:"] + [f"{u}–{v}({w})" for u, v, w in pt]
    lines += ["Kruskal:"] + [f"{u}–{v}({w})" for u, v, w in kt]
    lines += [f"Вага обох дерев: {result['total']}"]
    (out / "console.txt").write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines[-3:]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results5"))
    run(parser.parse_args().out)
