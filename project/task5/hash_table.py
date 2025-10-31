"""
Implementation of a hash table.
- The HashTable class implements MutableMapping (dictionary behavior).
- Collisions are resolved by separate chaining, where each chain
  is a binary search tree (BST).
- Access via [], the 'in' operator, deletion via 'del'.
- Implemented in-order and reverse-order traversals.
- __iter__ returns in-order traversal of keys.
"""

from collections.abc import MutableMapping
from typing import Optional, Generator, Iterator, Tuple, Any


class BSTNode:
    """Class representing a node in a binary search tree."""

    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BST:
    """
    Class representing a binary search tree. And methods to work with it, including:
    - insertion
    - deletion
    - search
    - in-order traversal
    - reverse-order traversal
    """

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size = 0

    def _comparator(self, a, b) -> int:
        """
        Compare two keys a and b.
        Returns:
            -1 if a < b,
             0 if a == b,
             1 if a > b
        """
        if a == b:
            return 0

        ha = hash(a)
        hb = hash(b)
        if ha != hb:
            return -1 if ha < hb else 1

        try:
            if a < b:
                return -1
            elif a > b:
                return 1
        except TypeError:
            return -1 if id(a) < id(b) else 1

    def insert(self, key, value) -> bool:
        """
        Inserts key/value.
        If the key already exists (by ==), replaces the value.
        Returns True if a new key was inserted, False if an existing key was replaced.
        """
        if self.root is None:
            self.root = BSTNode(key, value)
            self._size = 1
            return True

        cur = self.root
        while True:
            c = self._comparator(key, cur.key)
            if c == 0:
                cur.value = value
                return False
            elif c < 0:
                if cur.left is None:
                    cur.left = BSTNode(key, value)
                    self._size += 1
                    return True
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = BSTNode(key, value)
                    self._size += 1
                    return True
                cur = cur.right

    def _find_node(self, key) -> Optional[BSTNode]:
        cur = self.root
        while cur is not None:
            c = self._comparator(key, cur.key)
            if c == 0:
                return cur
            elif c < 0:
                cur = cur.left
            else:
                cur = cur.right
        return None

    def find(self, key):
        """Method for searching by a key."""
        node = self._find_node(key)
        return node.value if node is not None else None

    def _min_node(self, node: BSTNode) -> BSTNode:
        cur = node
        while cur.left is not None:
            cur = cur.left
        return cur

    def _delete_rec(
        self, node: Optional[BSTNode], key
    ) -> Tuple[Optional[BSTNode], bool]:
        if node is None:
            return None, False
        c = self._comparator(key, node.key)
        if c < 0:
            new_left, deleted = self._delete_rec(node.left, key)
            node.left = new_left
            return node, deleted
        elif c > 0:
            new_right, deleted = self._delete_rec(node.right, key)
            node.right = new_right
            return node, deleted
        else:
            if node.left is None:
                return node.right, True
            elif node.right is None:
                return node.left, True
            else:
                succ = self._min_node(node.right)
                node.key, node.value = succ.key, succ.value
                new_right, _ = self._delete_rec(node.right, succ.key)
                node.right = new_right
                return node, True

    def delete(self, key) -> bool:
        """
        Deletes a key. Returns True if the key was deleted, False if not found.
        """
        new_root, deleted = self._delete_rec(self.root, key)
        if deleted:
            self.root = new_root
            self._size -= 1
        return deleted

    def _inorder(
        self, node: Optional[BSTNode]
    ) -> Generator[Tuple[Any, Any], None, None]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield (node.key, node.value)
        yield from self._inorder(node.right)

    def inorder(self) -> Generator[Tuple[Any, Any], None, None]:
        """In-order traversal"""
        yield from self._inorder(self.root)

    def _reverse_order(
        self, node: Optional[BSTNode]
    ) -> Generator[Tuple[Any, Any], None, None]:
        if node is None:
            return
        yield from self._reverse_order(node.right)
        yield (node.key, node.value)
        yield from self._reverse_order(node.left)

    def reverse_order(self) -> Generator[Tuple[Any, Any], None, None]:
        """Reverse-order traversal"""
        yield from self._reverse_order(self.root)

    def __iter__(self) -> Iterator:
        """Iterate over keys in ascending order."""
        return self._inorder(self.root)

    def __reversed__(self) -> Iterator:
        """Iterate over keys in descending order."""
        return self._reverse_order(self.root)

    def __len__(self):
        return self._size


class HashTable(MutableMapping):
    """
    Hash table implementing MutableMapping.
    Bucket = BST.
    """

    def __init__(self, initial_capacity: int = 8):
        if initial_capacity <= 0:
            raise ValueError("initial_capacity must be > 0")
        self._capacity = initial_capacity
        self._buckets = [BST() for _ in range(self._capacity)]
        self._size = 0

    def bucket_index(self, key) -> int:
        return hash(key) % self._capacity

    def resize(self, new_capacity: int) -> None:
        new_capacity = int(new_capacity)
        if new_capacity <= 0:
            return
        old_items = list(self.items_forward())
        self._capacity = new_capacity
        self._buckets = [BST() for _ in range(self._capacity)]
        self._size = 0
        for k, v in old_items:
            idx = self.bucket_index(k)
            inserted = self._buckets[idx].insert(k, v)
            if inserted:
                self._size += 1

    def __getitem__(self, key):
        idx = self.bucket_index(key)
        node_val = self._buckets[idx]._find_node(key)
        if node_val is None:
            raise KeyError(key)
        return node_val.value

    def __setitem__(self, key, value) -> None:
        idx = self.bucket_index(key)
        inserted_new = self._buckets[idx].insert(key, value)
        if inserted_new:
            self._size += 1
            if self._size > self._capacity:
                self.resize(self._capacity * 2)

    def __delitem__(self, key) -> None:
        idx = self.bucket_index(key)
        deleted = self._buckets[idx].delete(key)
        if not deleted:
            raise KeyError(key)
        self._size -= 1

    def __iter__(self):
        """
        Should return in-order traversal of keys.
        Iterate through buckets in index order, perform in-order traversal in each bucket.
        (does not guarantee order)
        """
        for bucket in self._buckets:
            if bucket.root is not None:
                yield from bucket

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key) -> bool:
        idx = self.bucket_index(key)
        return self._buckets[idx].find(key) is not None

    def items_forward(self) -> Generator[Tuple[Any, Any], None, None]:
        for bucket in self._buckets:
            yield from bucket.inorder()

    def keys(self):
        for k, _ in self.items_forward():
            yield k

    def values(self):
        for _, v in self.items_forward():
            yield v

    def items(self):
        return self.items_forward()

    def clear(self):
        self._buckets = [BST() for _ in range(self._capacity)]
        self._size = 0
