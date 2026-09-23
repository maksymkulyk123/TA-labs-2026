"""ЛР 2, варіант 7: два сортування злиттям і quicksort Хоара.

Порівняння: лише порівняння ключів. Присвоювання: записи до змінних,
допоміжних списків і масиву, крім оновлення самих лічильників.
"""

DATA = [41, 68, 67, 10, 7, 69, 95, 43, 98]


def merge_iterative(values, key=lambda x: x):
    a = list(values)
    comparisons = assignments = 0
    trace = []
    width = 1
    while width < len(a):
        events = []
        for left in range(0, len(a), 2 * width):
            middle = min(left + width, len(a))
            right = min(left + 2 * width, len(a))
            if middle == right:
                continue
            i, j, merged = left, middle, []
            assignments += 3
            while i < middle and j < right:
                comparisons += 1
                if key(a[i]) <= key(a[j]):
                    merged.append(a[i]); i += 1
                else:
                    merged.append(a[j]); j += 1
                assignments += 2
            while i < middle:
                merged.append(a[i]); i += 1; assignments += 2
            while j < right:
                merged.append(a[j]); j += 1; assignments += 2
            a[left:right] = merged
            assignments += len(merged)
            events.append((left, middle, right, merged.copy()))
        width *= 2
        assignments += 1
        trace.append({"width": width // 2, "merges": events, "array": a.copy(),
                      "comparisons": comparisons, "assignments": assignments})
    return a, comparisons, assignments, trace


def merge_recursive(values, key=lambda x: x):
    comparisons = assignments = 0
    trace = []
    tree = []
    next_id = 0

    def visit(a, parent=None, side=""):
        nonlocal comparisons, assignments, next_id
        node_id = next_id; next_id += 1
        tree.append({"id": node_id, "parent": parent, "side": side,
                     "input": a.copy(), "output": None})
        if len(a) <= 1:
            tree[node_id]["output"] = a.copy()
            return a
        mid = len(a) // 2
        left = visit(a[:mid], node_id, "L")
        right = visit(a[mid:], node_id, "R")
        i = j = 0
        out = []
        assignments += 3
        while i < len(left) and j < len(right):
            comparisons += 1
            if key(left[i]) <= key(right[j]):
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
            assignments += 2
        while i < len(left):
            out.append(left[i]); i += 1; assignments += 2
        while j < len(right):
            out.append(right[j]); j += 1; assignments += 2
        tree[node_id]["output"] = out.copy()
        trace.append({"left": left, "right": right, "result": out.copy(),
                      "comparisons": comparisons, "assignments": assignments})
        return out

    result = visit(list(values))
    return result, comparisons, assignments, trace, tree


def quicksort_hoare(values, key=lambda x: x):
    a = list(values)
    comparisons = assignments = 0
    trace = []
    tree = []
    next_id = 0

    def visit(lo, hi, parent=None, side=""):
        nonlocal comparisons, assignments, next_id
        node_id = next_id; next_id += 1
        node = {"id": node_id, "parent": parent, "side": side,
                "lo": lo, "hi": hi, "before": a[lo:hi + 1].copy(),
                "pivot": None, "split": None}
        tree.append(node)
        if lo >= hi:
            return
        pivot = a[lo]
        i, j = lo - 1, hi + 1
        assignments += 3
        node["pivot"] = pivot
        swaps = []
        while True:
            while True:
                i += 1; assignments += 1
                comparisons += 1
                if key(a[i]) >= key(pivot):
                    break
            while True:
                j -= 1; assignments += 1
                comparisons += 1
                if key(a[j]) <= key(pivot):
                    break
            if i >= j:
                node["split"] = j
                trace.append({"lo": lo, "hi": hi, "pivot": pivot,
                              "split": j, "swaps": swaps,
                              "array": a.copy(), "comparisons": comparisons,
                              "assignments": assignments})
                break
            a[i], a[j] = a[j], a[i]
            assignments += 2
            swaps.append((i, j, a.copy()))
        visit(lo, j, node_id, "L")
        visit(j + 1, hi, node_id, "R")

    if a:
        visit(0, len(a) - 1)
    return a, comparisons, assignments, trace, tree


def verify():
    cases = [DATA, [], [1], [2, 2, 1], [3, -1, 3, 0],
             list(range(10)), list(range(10, 0, -1))]
    for case in cases:
        expected = sorted(case)
        assert merge_iterative(case)[0] == expected
        assert merge_recursive(case)[0] == expected
        assert quicksort_hoare(case)[0] == expected
    tagged = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    expected = [(1, "b"), (1, "d"), (2, "a"), (2, "c")]
    assert merge_iterative(tagged, key=lambda x: x[0])[0] == expected
    assert merge_recursive(tagged, key=lambda x: x[0])[0] == expected


if __name__ == "__main__":
    verify()
    for algorithm in (merge_iterative, merge_recursive, quicksort_hoare):
        result = algorithm(DATA)
        print(algorithm.__name__, "result:", result[0])
        print("key comparisons:", result[1], "assignments:", result[2])
        for event in result[3]:
            print(event)
