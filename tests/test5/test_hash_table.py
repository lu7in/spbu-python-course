import pytest
from project.task5.hash_table import HashTable, BST


def test_bst_insert_find_and_traversals():
    bst = BST()
    assert len(bst) == 0

    assert bst.insert(5, "5") is True
    assert bst.insert(1, "1") is True
    assert bst.insert(9, "9") is True
    assert bst.insert(3, "3") is True

    # Replacing existing key returns False and updates value
    assert bst.insert(3, "three") is False
    assert len(bst) == 4
    assert bst.find(3) == "three"

    # In-order should be sorted by integer keys
    inorder = list(bst.inorder())
    keys_inorder = [k for k, _ in inorder]
    assert keys_inorder == sorted(keys_inorder)

    # Reverse-order should be opposite of in-order
    rev = list(bst.reverse_order())
    keys_rev = [k for k, _ in rev]
    assert keys_rev == sorted(keys_inorder, reverse=True)

    assert list(iter(bst)) == inorder


def test_bst_delete_cases():
    bst = BST()
    pairs = [(3, "a"), (1, "b"), (4, "c"), (0, "d"), (2, "e"), (5, "f")]
    for k, v in pairs:
        bst.insert(k, v)
    assert len(bst) == 6

    # Delete a leaf (0)
    assert bst.delete(0) is True
    assert bst.find(0) is None
    assert len(bst) == 5

    # Delete node with one child (4 has only right child 5)
    assert bst.delete(4) is True
    assert bst.find(4) is None
    assert len(bst) == 4

    # Delete node with two children (3)
    assert bst.delete(3) is True
    assert bst.find(3) is None
    assert len(bst) == 3

    # Deleting non-existent key returns False
    assert bst.delete(999) is False


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
