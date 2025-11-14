"""
Thread-safe adaptation of the hash table implemented with BST buckets.

- Uses a reader-writer lock to allow many concurrent readers and exclusive writers.
- All public methods of HashTable are protected:
  - Readers (getitem, contains, iteration, keys/values/items, find-like operations) acquire a read lock.
  - Writers (setitem, delitem, resize, clear) acquire a write lock.
- The underlying BST implementation is unchanged from the single-threaded version
  (operations on a BST are invoked only while the appropriate table-level lock is held).
"""

from collections.abc import MutableMapping
from typing import Optional, Generator, Iterator, Tuple, Any, ContextManager
import threading
from contextlib import contextmanager


class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BST:
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size = 0

    def _comparator(self, a, b) -> int:
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
            pass
        return -1 if id(a) < id(b) else 1

    def insert(self, key, value) -> bool:
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
        yield from self._reverse_order(self.root)

    def __iter__(self) -> Iterator:
        return self._inorder(self.root)

    def __reversed__(self) -> Iterator:
        return self._reverse_order(self.root)

    def __len__(self):
        return self._size


class _RWLock:
    """
    Simple reader-writer lock. Multiple readers can hold the lock simultaneously.
    Writers acquire the lock exclusively.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._readers = 0
        self._writer = False
        self._writers_waiting = 0

    @contextmanager
    def read_lock(self) -> Generator:
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self) -> Generator:
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()

    def acquire_read(self):
        with self._cond:
            while self._writer or self._writers_waiting > 0:
                self._cond.wait()
            self._readers += 1

    def release_read(self):
        with self._cond:
            self._readers -= 1
            if self._readers == 0:
                self._cond.notify_all()

    def acquire_write(self):
        with self._cond:
            self._writers_waiting += 1
            while self._writer or self._readers > 0:
                self._cond.wait()
            self._writers_waiting -= 1
            self._writer = True

    def release_write(self):
        with self._cond:
            self._writer = False
            self._cond.notify_all()


class HashTable(MutableMapping):
    """
    Thread-safe hash table using BST buckets and a table-level reader-writer lock.
    """

    def __init__(self, initial_capacity: int = 8):
        if initial_capacity <= 0:
            raise ValueError("initial_capacity must be > 0")
        self._capacity = initial_capacity
        self._buckets = [BST() for _ in range(self._capacity)]
        self._size = 0
        self._rw = _RWLock()

    def bucket_index(self, key) -> int:
        return hash(key) % self._capacity

    def resize(self, new_capacity: int) -> None:
        new_capacity = int(new_capacity)
        if new_capacity <= 0:
            return
        # resize requires exclusive access
        with self._rw.write_lock():
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
        with self._rw.read_lock():
            idx = self.bucket_index(key)
            node_val = self._buckets[idx]._find_node(key)
            if node_val is None:
                raise KeyError(key)
            return node_val.value

    def __setitem__(self, key, value) -> None:
        with self._rw.write_lock():
            idx = self.bucket_index(key)
            inserted_new = self._buckets[idx].insert(key, value)
            if inserted_new:
                self._size += 1
                if self._size > self._capacity:
                    # resize doubles capacity
                    new_cap = max(2, self._capacity * 2)
                    # perform resize while still holding write lock
                    old_items = list(self.items_forward())
                    self._capacity = new_cap
                    self._buckets = [BST() for _ in range(self._capacity)]
                    self._size = 0
                    for k, v in old_items:
                        idx2 = self.bucket_index(k)
                        if self._buckets[idx2].insert(k, v):
                            self._size += 1

    def __delitem__(self, key) -> None:
        with self._rw.write_lock():
            idx = self.bucket_index(key)
            deleted = self._buckets[idx].delete(key)
            if not deleted:
                raise KeyError(key)
            self._size -= 1

    def __iter__(self):
        # iteration is a read operation (snapshot-like). Acquire read lock and yield.
        with self._rw.read_lock():
            # iterate over buckets in index order and yield keys in order per bucket
            for bucket in self._buckets:
                if bucket.root is not None:
                    for k, _ in bucket.inorder():
                        yield k

    def __len__(self) -> int:
        with self._rw.read_lock():
            return self._size

    def __contains__(self, key) -> bool:
        with self._rw.read_lock():
            idx = self.bucket_index(key)
            return self._buckets[idx].find(key) is not None

    def items_forward(self) -> Generator[Tuple[Any, Any], None, None]:
        with self._rw.read_lock():
            for bucket in self._buckets:
                yield from bucket.inorder()

    def keys(self):
        with self._rw.read_lock():
            for k, _ in self.items_forward():
                yield k

    def values(self):
        with self._rw.read_lock():
            for _, v in self.items_forward():
                yield v

    def items(self):
        return self.items_forward()

    def clear(self):
        with self._rw.write_lock():
            self._buckets = [BST() for _ in range(self._capacity)]
            self._size = 0
