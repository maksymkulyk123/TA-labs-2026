"""ЛР 1, варіант 7: сортування вибором і вставками.

Порівнянням вважається тільки порівняння ключів. Присвоюванням є запис
у змінну або комірку масиву; службові лічильники до них не включено.
"""

DATA = [41, 68, 67, 10, 7, 69, 95, 43, 98]


def selection_sort(values):
    a = list(values)
    comparisons = assignments = 0
    trace = []
    for i in range(len(a) - 1):
        minimum = i
        assignments += 1
        checks = []
        for j in range(i + 1, len(a)):
            comparisons += 1
            less = a[j] < a[minimum]
            checks.append((j, a[j], a[minimum], less))
            if less:
                minimum = j
                assignments += 1
        chosen = a[minimum]
        if minimum != i:
            temporary = a[i]
            a[i] = a[minimum]
            a[minimum] = temporary
            assignments += 3
        trace.append({"pass": i, "minimum_index": minimum,
                      "minimum_value": chosen, "checks": checks,
                      "array": a.copy(), "comparisons": comparisons,
                      "assignments": assignments})
    return a, comparisons, assignments, trace


def insertion_sort(values):
    a = list(values)
    comparisons = assignments = 0
    trace = []
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        assignments += 2
        checks = []
        while j >= 0:
            comparisons += 1
            greater = a[j] > key
            checks.append((j, a[j], key, greater))
            if not greater:
                break
            a[j + 1] = a[j]
            j -= 1
            assignments += 2
        a[j + 1] = key
        assignments += 1
        trace.append({"pass": i, "key": key, "position": j + 1,
                      "checks": checks, "array": a.copy(),
                      "comparisons": comparisons, "assignments": assignments})
    return a, comparisons, assignments, trace


def verify():
    expected = sorted(DATA)
    for algorithm in (selection_sort, insertion_sort):
        result, _, _, _ = algorithm(DATA)
        assert result == expected
        for case in ([], [1], [2, 2, 1], [3, -1, 3, 0], list(range(10)), list(range(10, 0, -1))):
            assert algorithm(case)[0] == sorted(case)


if __name__ == "__main__":
    verify()
    for algorithm in (selection_sort, insertion_sort):
        result, comparisons, assignments, trace = algorithm(DATA)
        print(algorithm.__name__, "result:", result)
        print("key comparisons:", comparisons, "assignments:", assignments)
        for row in trace:
            print(row)
