"""ЛР3, варіант 7. Запуск: python TA_LR3_variant7.py --out results3.

C — порівняння значень ключів, включаючи завершальні хибні.
S — обміни, W=3*S — присвоювання даних через тимчасову змінну.
Перевірки індексів та записи журналу не входять до C/W.
"""
import argparse
import csv
import json
from pathlib import Path

INPUT = [41, 68, 67, 10, 7, 69, 95, 43, 98]


def heap_sort(a, key=lambda x: x):
    """Сортує a на місці. Журнал потрібен лише для демонстрації."""
    events, passes = [], []
    stats = {"C": 0, "S": 0, "W": 0}

    def log(text):
        events.append({"step": len(events) + 1,
                       "phase": phase, "call": call,
                       "condition_action": text, "array": a.copy()})

    def swap(i, j):
        x, y = a[i], a[j]
        temp = a[i]
        a[i] = a[j]
        a[j] = temp
        stats["S"] += 1
        stats["W"] += 3
        log(f"Swap({i},{j}): {x} <-> {y}")

    def sink(i, n):
        k = i
        while True:
            j = 2 * k + 1
            log(f"k={k}; j={j}; j>=n: {j}>={n} -> {j>=n}")
            if j >= n:
                break
            right = j + 1 < n
            log(f"j+1<n: {j+1}<{n} -> {right}")
            if right:
                stats["C"] += 1
                choose_right = key(a[j+1]) > key(a[j])
                log(f"A[{j+1}]>A[{j}]: {a[j+1]}>{a[j]} -> {choose_right}")
                if choose_right:
                    j += 1
            stats["C"] += 1
            stop = key(a[k]) >= key(a[j])
            log(f"A[{k}]>=A[{j}]: {a[k]}>={a[j]} -> {stop}")
            if stop:
                break
            swap(k, j)
            k = j

    n = len(a)
    phase = "build"
    for i in range(n // 2 - 1, -1, -1):
        call = f"Sink({i},{n})"
        first = len(events)
        before = stats.copy()
        sink(i, n)
        passes.append({"phase": phase, "i": i, "n": n,
                       "array": a.copy(), "first": first,
                       "last": len(events),
                       "C": stats["C"]-before["C"],
                       "S": stats["S"]-before["S"]})
    phase = "sort"
    for i in range(n - 1, 0, -1):
        call = f"Swap(0,{i}); Sink(0,{i})"
        first = len(events)
        before = stats.copy()
        swap(0, i)
        sink(0, i)
        passes.append({"phase": phase, "i": i, "n": i,
                       "array": a.copy(), "first": first,
                       "last": len(events),
                       "C": stats["C"]-before["C"],
                       "S": stats["S"]-before["S"]})
    return stats, events, passes


def quick_sort(a):
    """Хоар, pivot — середній елемент. Та сама модель C/S/W."""
    stats = {"C": 0, "S": 0, "W": 0}

    def sort(lo, hi):
        if lo >= hi:
            return
        pivot = a[(lo + hi) // 2]
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while True:
                stats["C"] += 1
                if not a[i] < pivot:
                    break
                i += 1
            j -= 1
            while True:
                stats["C"] += 1
                if not a[j] > pivot:
                    break
                j -= 1
            if i >= j:
                break
            temp = a[i]
            a[i] = a[j]
            a[j] = temp
            stats["S"] += 1
            stats["W"] += 3
        sort(lo, j)
        sort(j + 1, hi)

    sort(0, len(a) - 1)
    return stats


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    a = INPUT.copy()
    stats, events, passes = heap_sort(a)
    q = INPUT.copy()
    qs = quick_sort(q)
    unstable = [(2, "a"), (2, "b"), (1, "c")]
    heap_sort(unstable, key=lambda x: x[0])
    result = dict(input=INPUT, sorted=a, stats=stats,
                  quick_stats=qs, passes=passes, events=events,
                  unstable=unstable)
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    with (out / "trace.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=events[0].keys())
        writer.writeheader()
        writer.writerows(events)
    text = [f"Вхід: {INPUT}"]
    for e in events:
        text.append(f"{e['step']:03} {e['phase']} {e['call']}: "
                    f"{e['condition_action']} | {e['array']}")
    text += [f"Результат: {a}", f"Heapsort: {stats}",
             f"Quicksort: {qs}", f"Нестійкість: {unstable}"]
    (out / "console.txt").write_text("\n".join(text), encoding="utf8")
    print("\n".join(text[-4:]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results3"))
    run(parser.parse_args().out)
