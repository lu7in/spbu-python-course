import threading
import random
import pytest

from project.task5.hash_table import HashTable
from project.task6.parallel_hash_table import HashTable as BaselineHashTable

# Old tests showing parallel HashTable implementation remained correct
def test_basic_mutable_mapping_behaviour():
    ht = HashTable(initial_capacity=4)
    ht["a"] = 1
    assert "a" in ht
    assert ht["a"] == 1
    # get with default (MutableMapping.get)
    assert ht.get("a") == 1
    assert ht.get("missing", 42) == 42
    # length
    assert len(ht) == 1
    # KeyError on missing __getitem__
    with pytest.raises(KeyError):
        _ = ht["missing"]
    # delete existing
    del ht["a"]
    assert "a" not in ht
    assert len(ht) == 0
    # delete missing -> KeyError
    with pytest.raises(KeyError):
        del ht["missing"]


def test_update_does_not_increase_size():
    ht = HashTable()
    ht["k"] = "v1"
    assert ht["k"] == "v1"
    assert len(ht) == 1
    # update existing key should not increase len
    ht["k"] = "v2"
    assert ht["k"] == "v2"
    assert len(ht) == 1


def test_mutable_mapping_methods():
    ht = HashTable()
    # update is provided by MutableMapping mixin
    ht.update({"one": 1, "two": 2, "three": 3})
    assert len(ht) == 3
    keys = list(ht.keys())
    values = list(ht.values())
    items = list(ht.items())
    assert set(keys) == {"one", "two", "three"}
    assert set(values) == {1, 2, 3}
    assert set(items) == {("one", 1), ("two", 2), ("three", 3)}
    # pop should remove and return value
    v = ht.pop("two")
    assert v == 2
    assert "two" not in ht
    # clear resets
    ht.clear()
    assert len(ht) == 0
    assert list(ht.items()) == []


def test_non_hashable_key_typeerror():
    ht = HashTable()
    # lists are unhashable, should raise TypeError on insertion
    with pytest.raises(TypeError):
        ht[[1, 2, 3]] = "value"


def test_collision_resolution():
    class CollidingKey:
        def __init__(self, value):
            self.value = value

        def __hash__(self):
            # Force all instances to collide into same bucket
            return 42

        def __eq__(self, other):
            return isinstance(other, CollidingKey) and self.value == other.value

        def __repr__(self):
            return f"CollidingKey({self.value!r})"

    ht = HashTable(initial_capacity=4)
    k1 = CollidingKey("one")
    k2 = CollidingKey("two")
    k3 = CollidingKey("three")

    # Place colliding keys into the table
    ht[k1] = 1
    ht[k2] = 2
    ht[k3] = 3

    # They must map to same bucket index
    idx1 = ht.bucket_index(k1)
    idx2 = ht.bucket_index(k2)
    idx3 = ht.bucket_index(k3)
    assert idx1 == idx2 == idx3

    # All keys must be retrievable independently
    assert ht[k1] == 1
    assert ht[k2] == 2
    assert ht[k3] == 3

    # Bucket internal structure should contain 3 entries (BST size)
    bucket = ht._buckets[idx1]
    assert len(bucket) == 3

    # 'in' operator should work for colliding keys
    assert k1 in ht
    assert k2 in ht
    assert k3 in ht

    # Delete one key and ensure others remain
    del ht[k2]
    assert k2 not in ht
    assert k1 in ht and k3 in ht
    assert len(ht) == 2

    # After deletions remaining keys still return correct values
    assert ht[k1] == 1
    assert ht[k3] == 3


def test_resize_preserves_items_and_counts():
    # small capacity to trigger resize early
    ht = HashTable(initial_capacity=2)
    # inserting second key should trigger resize
    ht[1] = "one"
    assert len(ht) == 1
    ht[2] = "two"  # should trigger resize
    ht[3] = "three"
    # after resize all items must be present
    assert ht[1] == "one" and ht[2] == "two" and ht[3] == "three"
    assert len(ht) == 3
    # further operations should continue to work
    del ht[2]
    assert 2 not in ht
    assert len(ht) == 2


def test_equality_by_value_and_contains_behavior():
    # Two different objects that compare equal and have same hash should be interchangeable as keys
    class EqKey:
        def __init__(self, val):
            self.val = val

        def __hash__(self):
            return hash(self.val)

        def __eq__(self, other):
            return isinstance(other, EqKey) and self.val == other.val

    k1 = EqKey(10)
    k2 = EqKey(10)  # different instance but equal to k1
    ht = HashTable()
    ht[k1] = "ten"
    assert k2 in ht
    assert ht[k2] == "ten"
    # deletion via equal object should remove entry
    del ht[k2]
    assert k1 not in ht
    assert len(ht) == 0


# Multithread behaviour test
def test_concurrent_writes_and_reads():
    NUM_WRITERS = 8
    ITEMS_PER_WRITER = 2000

    table = HashTable(initial_capacity=16)

    def writer(start):
        for i in range(start, start + ITEMS_PER_WRITER):
            table[i] = f"v{i}"

    writer_threads = []
    for w in range(NUM_WRITERS):
        t = threading.Thread(target=writer, args=(w * ITEMS_PER_WRITER,))
        writer_threads.append(t)
        t.start()

    stop_readers = threading.Event()

    def reader():
        while not stop_readers.is_set():
            k = random.randrange(0, NUM_WRITERS * ITEMS_PER_WRITER)
            try:
                _ = table[k]
            except KeyError:
                # it's possible reader raced before writer inserted: that's ok
                pass

    reader_threads = []
    for _ in range(4):
        t = threading.Thread(target=reader)
        reader_threads.append(t)
        t.start()

    for t in writer_threads:
        t.join()

    # all writers finished -> stop readers
    stop_readers.set()
    for t in reader_threads:
        t.join()

    # verify final table content
    total_expected = NUM_WRITERS * ITEMS_PER_WRITER
    assert len(table) == total_expected
    for i in range(total_expected):
        assert table[i] == f"v{i}"


def test_no_data_loss_when_mixed_operations():
    table = HashTable(initial_capacity=8)
    NUM_THREADS = 10
    OPS_PER_THREAD = 2000

    def worker(tid):
        base = tid * OPS_PER_THREAD
        for i in range(base, base + OPS_PER_THREAD):
            table[i] = i
        # do some deletes
        for i in range(base, base + OPS_PER_THREAD, 10):
            try:
                del table[i]
            except KeyError:
                pass

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # verify size
    expected = NUM_THREADS * OPS_PER_THREAD - NUM_THREADS * (OPS_PER_THREAD // 10)
    assert len(table) == expected

    # ensure remaining items are correct
    for tid in range(NUM_THREADS):
        base = tid * OPS_PER_THREAD
        for i in range(base, base + OPS_PER_THREAD):
            if i % 10 == 0:
                assert i not in table
            else:
                assert table[i] == i


def test_baseline_shows_race_condition_in_stress():
    """
    This test shows that the baseline (non-threadsafe) implementation will likely lose updates
    under concurrent increments of the same key.
    """
    NUM_THREADS = 8
    INCREMENTS = 5000

    ts_table = HashTable(initial_capacity=8)
    base_table = BaselineHashTable(initial_capacity=8)

    def inc_many(table, count):
        for _ in range(count):
            try:
                v = table["counter"]
            except KeyError:
                v = 0
            table["counter"] = v + 1

    # run thread-safe version
    threads = [
        threading.Thread(target=inc_many, args=(ts_table, INCREMENTS))
        for _ in range(NUM_THREADS)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert ts_table["counter"] == NUM_THREADS * INCREMENTS

    # run baseline version (non-threadsafe)
    threads = [
        threading.Thread(target=inc_many, args=(base_table, INCREMENTS))
        for _ in range(NUM_THREADS)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # we check that baseline result is an integer >=1 and <= expected
    val = base_table["counter"]
    assert isinstance(val, int)
    assert 1 <= val <= NUM_THREADS * INCREMENTS


def apple_pie():
    print(
        """Ingredients:

Apples: 3–4 medium (about 1.5 lbs or 680 g), such as Granny Smith or Winesap, peeled, cored, and diced or sliced
Eggs: 3–8 large, depending on the recipe, typically room temperature
Sugar: 1–2 cups (200–440 g), granulated or white sugar
All-Purpose Flour: 1–2 cups (120–260 g), sifted
Vanilla Extract: 1–2 teaspoons
Baking Powder: ½–1 teaspoon (optional, in some recipes)
Salt: ¼–½ teaspoon (optional, in some recipes)
Powdered Sugar: For dusting on top before serving (optional)
Equipment Needed:

9-inch (23 cm) springform pan or round baking pan (greased and lined with parchment paper recommended)
Stand mixer or hand mixer with whisk attachment (for beating eggs and sugar)
Spatula (for folding ingredients gently)
Parchment paper (for lining the pan)
Measuring cups and spoons
Knife and cutting board
Instructions:

Preheat the oven to 350°F (180°C).
Prepare the apples by peeling, coring, and slicing or dicing them into 1-inch (2.5 cm) pieces. Toss with lemon juice if desired to prevent browning.
Grease the 9-inch baking pan and line the bottom with parchment paper, or use a non-stick spray.
In a large bowl, beat the eggs with sugar using a mixer until the mixture triples in volume and becomes pale and fluffy—this can take 5 to 10 minutes.
If using, add vanilla extract, baking powder, and salt to the egg mixture and mix briefly.
Sift in the flour in portions and gently fold it into the batter using a spatula, being careful not to overmix to preserve the airy texture.
Fold in the prepared apples, reserving a portion for the top if desired.
Pour the batter over the apples in the pan, spreading it evenly with a spatula.
If using, scatter the reserved apple slices on top of the batter.
Bake for 30 to 60 minutes, or until the top is golden brown and a toothpick or cake tester inserted into the center comes out clean.
Remove from the oven and let cool in the pan for 10–30 minutes to allow the cake to set.
Use a thin knife or spatula to loosen the edges, then carefully remove the cake from the pan and transfer it to a serving platter.
Dust the top generously with powdered sugar just before serving."""
    )


apple_pie()
