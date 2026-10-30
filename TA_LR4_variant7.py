"""ЛР4, варіант 7. Ланцюжки та лінійне пробування.

Запуск: python TA_LR4_variant7.py --out results4
Повтори зберігаються як (слово, номер входження). Ключ K — сума
позицій букв українського алфавіту. Успішний пошук і видалення
кожного запису вимірюються на окремій копії початкової таблиці.
"""
import argparse
import json
import math
import re
from pathlib import Path

ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
POSITIONS = {c: i + 1 for i, c in enumerate(ALPHABET)}
PHRASE = "Людина без друзів — як дерево без коріння"
DELETED = object()


def records(text):
    counts, result = {}, []
    for word in re.findall("[а-яґєії]+", text.lower()):
        counts[word] = counts.get(word, 0) + 1
        result.append((word, counts[word]))
    return result


def key(record):
    return sum(POSITIONS[c] for c in record[0])


def address(record, method):
    k = key(record)
    if method == "division":
        return k % 13
    if method != "multiplication":
        raise ValueError("Невідома хеш-функція")
    a = (math.sqrt(5) - 1) / 2
    return math.floor(16 * (k * a - math.floor(k * a)))


class Node:
    def __init__(self, record):
        self.record, self.next = record, None


class Chaining:
    def __init__(self, method):
        self.method = method
        self.m = 13 if method == "division" else 16
        self.heads = [None] * self.m
        self.tails = [None] * self.m

    def insert(self, record):
        h = address(record, self.method)
        node = Node(record)
        if self.heads[h] is None:
            self.heads[h] = node
        else:
            self.tails[h].next = node
        self.tails[h] = node
        return [h]

    def search(self, record, delete=False):
        h = address(record, self.method)
        prev, node, c, path = None, self.heads[h], 0, []
        while node is not None:
            c += 1
            path.append(node.record)
            if node.record == record:
                if delete:
                    if prev is None:
                        self.heads[h] = node.next
                    else:
                        prev.next = node.next
                    if self.tails[h] is node:
                        self.tails[h] = prev
                return True, c, path
            prev, node = node, node.next
        return False, c, path

    def view(self):
        table = []
        for head in self.heads:
            chain = []
            while head is not None:
                chain.append(head.record)
                head = head.next
            table.append(chain)
        return table


class Probing:
    def __init__(self, method):
        self.method = method
        self.m = 13 if method == "division" else 16
        self.table = [None] * self.m

    def insert(self, record):
        h = address(record, self.method)
        path, first_deleted = [], None
        for i in range(self.m):
            j = (h + i) % self.m
            path.append(j)
            value = self.table[j]
            if value is DELETED and first_deleted is None:
                first_deleted = j
            if value is None:
                target = j if first_deleted is None else first_deleted
                self.table[target] = record
                return path
            if value is not DELETED and value == record:
                raise ValueError("Цей запис вже існує")
        if first_deleted is not None:
            self.table[first_deleted] = record
            return path
        raise OverflowError("Таблиця заповнена")

    def search(self, record, delete=False):
        h, c, path = address(record, self.method), 0, []
        for i in range(self.m):
            j = (h + i) % self.m
            path.append(j)
            value = self.table[j]
            if value is None:
                return False, c, path
            if value is DELETED:
                continue
            c += 1
            if value == record:
                if delete:
                    self.table[j] = DELETED
                return True, c, path
        return False, c, path

    def view(self):
        return ["DELETED" if x is DELETED else x for x in self.table]


def build(cls, method, items):
    table = cls(method)
    trace = []
    for record in items:
        path = table.insert(record)
        trace.append(dict(record=record, K=key(record),
                          h=address(record, method), path=path,
                          table=table.view()))
    return table, trace


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    items = records(PHRASE)
    result = {"phrase": PHRASE, "records": items, "tables": {}}
    console = [PHRASE]
    for method in ("division", "multiplication"):
        for cls in (Chaining, Probing):
            table, trace = build(cls, method, items)
            searches = []
            for record in items:
                found, c, path = table.search(record)
                fresh, _ = build(cls, method, items)
                deleted, dc, _ = fresh.search(record, delete=True)
                assert found and deleted and c == dc
                assert not fresh.search(record)[0]
                searches.append(dict(record=record, C=c, delete_C=dc,
                                     path=path))
            name = f"{cls.__name__}_{method}"
            result["tables"][name] = dict(
                final=table.view(), trace=trace, searches=searches,
                maximum=max(x["C"] for x in searches),
                mean=sum(x["C"] for x in searches)/len(items))
            console.append(name)
            console += [f"{i}: {x}" for i, x in enumerate(table.view())]
            console += [f"{x['record']}: C={x['C']}; шлях={x['path']}"
                        for x in searches]
            console.append(f"Середнє={result['tables'][name]['mean']:.6f}")
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    (out / "console.txt").write_text("\n".join(console), encoding="utf8")
    print("\n".join(console))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results4"))
    run(parser.parse_args().out)
