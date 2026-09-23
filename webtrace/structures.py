"""
================================================================================
WebTrace: Syllabus-Aligned Custom Data Structures (ECE 2103)
================================================================================
Implements textbook data structures from the ECE 2103 curriculum:

1. Vector (Linear Array / Dynamic Array):
   - Demonstrates: Linear Array representation in memory, dynamic resizing (capacity
     doubling), element insertion, traversal, Linear Search O(N), and Binary Search O(log N).

2. MinHeapPriorityQueue (Priority Queue / Binary Min-Heap):
   - Demonstrates: Complete binary tree mapped into a linear array, sift-up/sift-down
     heapify operations, O(log N) push and pop, O(1) peek.
   - Core prerequisite for Dijkstra's Shortest Path Algorithm.

3. BinarySearchTree (BST):
   - Demonstrates: Linked representation of binary trees, recursive/iterative search
     and insertion O(log N), deletion with 3 structural cases (leaf, single child,
     two children with in-order successor), and In-Order Traversal (lexicographical sorting).
================================================================================
"""

from typing import Any, Callable, Generator, Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")


# ==============================================================================
# 1. VECTOR (LINEAR ARRAY / DYNAMIC ARRAY)
# ==============================================================================
class Vector(Generic[T]):
    """
    A textbook Linear Array / Dynamic Array data structure.

    DSA Topics Covered:
    - Linear Array & representation in memory
    - Insertion & Traversal
    - Linear Search: O(N) worst/average case
    - Binary Search: O(log N) worst/average case (when elements are kept sorted)
    """

    def __init__(self, initial_capacity: int = 8) -> None:
        self._capacity = max(1, initial_capacity)
        self._size = 0
        # Simulated contiguous memory buffer of fixed capacity
        self._buffer: List[Optional[T]] = [None] * self._capacity

    @property
    def size(self) -> int:
        """Returns the logical number of elements stored in the vector."""
        return self._size

    @property
    def capacity(self) -> int:
        """Returns the physical capacity allocated in memory."""
        return self._capacity

    def is_empty(self) -> bool:
        """Checks if the array contains no elements."""
        return self._size == 0

    def _resize(self, new_capacity: int) -> None:
        """
        Doubles the physical storage buffer when capacity is exceeded.
        Demonstrates memory reallocation & element copying in Linear Arrays.
        Time Complexity: O(N) to copy elements. Amortized push_back is O(1).
        """
        new_buffer: List[Optional[T]] = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[i]
        self._buffer = new_buffer
        self._capacity = new_capacity

    def push_back(self, item: T) -> None:
        """
        Inserts an element at the end of the Linear Array.
        Amortized Time Complexity: O(1).
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        self._buffer[self._size] = item
        self._size += 1

    def add(self, item: T) -> None:
        """Compatibility alias for push_back."""
        self.push_back(item)

    def get(self, index: int) -> T:
        """Direct index access in O(1) time."""
        if index < 0 or index >= self._size:
            raise IndexError(f"Vector index {index} out of range [0, {self._size - 1}]")
        val = self._buffer[index]
        assert val is not None
        return val

    def set(self, index: int, item: T) -> None:
        """Updates element at index in O(1) time."""
        if index < 0 or index >= self._size:
            raise IndexError(f"Vector index {index} out of range [0, {self._size - 1}]")
        self._buffer[index] = item

    def linear_search(self, target: T) -> int:
        """
        Linear Search on the array.
        Time Complexity:
            Best Case: O(1) (target is at index 0)
            Worst/Average Case: O(N) (target is at the end or absent)
        Returns:
            Index of target if found, or -1 if absent.
        """
        for i in range(self._size):
            if self._buffer[i] == target:
                return i
        return -1

    def contains(self, target: T) -> bool:
        """Membership test using Linear Search."""
        return self.linear_search(target) != -1

    def binary_search(self, target: T) -> int:
        """
        Binary Search algorithm (requires vector elements to be sorted).
        Time Complexity: O(log N).
        Returns:
            Index of target if found, or -1 if absent.
        """
        low = 0
        high = self._size - 1

        while low <= high:
            mid = (low + high) // 2
            mid_val = self._buffer[mid]
            assert mid_val is not None

            if mid_val == target:
                return mid
            elif mid_val < target:  # type: ignore
                low = mid + 1
            else:
                high = mid - 1

        return -1

    def to_list(self) -> List[T]:
        """Converts logical contents to a standard Python list."""
        return [self._buffer[i] for i in range(self._size)]  # type: ignore

    def __iter__(self) -> Generator[T, None, None]:
        for i in range(self._size):
            yield self._buffer[i]  # type: ignore

    def __len__(self) -> int:
        return self._size

    def __contains__(self, item: T) -> bool:
        return self.contains(item)

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __repr__(self) -> str:
        return f"Vector(size={self._size}, capacity={self._capacity}, elements={self.to_list()})"


# ==============================================================================
# 2. PRIORITY QUEUE / BINARY MIN-HEAP
# ==============================================================================
class HeapItem(Generic[T]):
    """Wrapper storing a priority key and value payload."""
    __slots__ = ("priority", "value")

    def __init__(self, priority: float, value: T) -> None:
        self.priority = priority
        self.value = value

    def __lt__(self, other: "HeapItem") -> bool:
        return self.priority < other.priority

    def __repr__(self) -> str:
        return f"HeapItem(priority={self.priority}, value={self.value})"


class MinHeapPriorityQueue(Generic[T]):
    """
    Binary Min-Heap Priority Queue.

    DSA Topics Covered:
    - Representation of Complete Binary Trees in a Linear Array:
        Parent(i) = (i - 1) // 2
        LeftChild(i) = 2 * i + 1
        RightChild(i) = 2 * i + 2
    - Heapify Sift-Up (Bubble-Up): O(log N)
    - Heapify Sift-Down (Bubble-Down): O(log N)
    - Push: O(log N)
    - Pop (Extract-Min): O(log N)
    """

    def __init__(self) -> None:
        self._heap: List[HeapItem[T]] = []

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def push(self, priority: float, value: T) -> None:
        """Inserts an element and restores min-heap property via sift-up."""
        item = HeapItem(priority=priority, value=value)
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> Tuple[float, T]:
        """
        Extracts and returns the element with minimum priority (root).
        Time Complexity: O(log N).
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty Priority Queue")

        root = self._heap[0]
        last_item = self._heap.pop()

        if self._heap:
            self._heap[0] = last_item
            self._sift_down(0)

        return root.priority, root.value

    def peek(self) -> Tuple[float, T]:
        """Returns the minimum priority element without removing it: O(1)."""
        if self.is_empty():
            raise IndexError("Cannot peek into an empty Priority Queue")
        return self._heap[0].priority, self._heap[0].value

    def _sift_up(self, index: int) -> None:
        """Bubbles an element up to restore min-heap invariant."""
        parent = (index - 1) // 2
        while index > 0 and self._heap[index] < self._heap[parent]:
            self._heap[index], self._heap[parent] = self._heap[parent], self._heap[index]
            index = parent
            parent = (index - 1) // 2

    def _sift_down(self, index: int) -> None:
        """Bubbles an element down to restore min-heap invariant."""
        size = len(self._heap)
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if left < size and self._heap[left] < self._heap[smallest]:
                smallest = left

            if right < size and self._heap[right] < self._heap[smallest]:
                smallest = right

            if smallest != index:
                self._heap[index], self._heap[smallest] = self._heap[smallest], self._heap[index]
                index = smallest
            else:
                break

    def __len__(self) -> int:
        return len(self._heap)


# ==============================================================================
# 3. BINARY SEARCH TREE (BST)
# ==============================================================================
class BSTNode(Generic[T]):
    """Node in a linked Binary Search Tree."""
    def __init__(self, key: str, value: T) -> None:
        self.key: str = key
        self.value: T = value
        self.left: Optional["BSTNode[T]"] = None
        self.right: Optional["BSTNode[T]"] = None

    def __repr__(self) -> str:
        return f"BSTNode(key={self.key})"


class BinarySearchTree(Generic[T]):
    """
    Binary Search Tree (BST) for indexing crawled web pages.

    DSA Topics Covered:
    - Linked memory representation of Binary Trees
    - Tree Traversal: In-Order Traversal yields elements in sorted order
    - BST Invariant: Left subtree keys < Node key < Right subtree keys
    - Search: O(log N) average, O(N) worst case
    - Insertion: O(log N) average, O(N) worst case
    - Deletion: Covers all 3 textbook cases:
        Case 1: Leaf node (no children)
        Case 2: Node with single child
        Case 3: Node with two children (replaces with in-order successor)
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode[T]] = None
        self._count: int = 0

    @property
    def count(self) -> int:
        return self._count

    def insert(self, key: str, value: T) -> None:
        """Inserts key-value pair into the BST."""
        if self.root is None:
            self.root = BSTNode(key, value)
            self._count += 1
            return

        curr = self.root
        while True:
            if key == curr.key:
                # Update existing key
                curr.value = value
                return
            elif key < curr.key:
                if curr.left is None:
                    curr.left = BSTNode(key, value)
                    self._count += 1
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = BSTNode(key, value)
                    self._count += 1
                    return
                curr = curr.right

    def search(self, key: str) -> Optional[T]:
        """
        Searches for a key in the BST.
        Time Complexity: O(log N) average.
        Returns:
            Stored value if found, or None.
        """
        curr = self.root
        while curr:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def delete(self, key: str) -> bool:
        """
        Deletes a node with the specified key from the BST.
        Covers 3 deletion cases: leaf node, 1 child, 2 children.
        Returns:
            True if deleted, False if key was not found.
        """
        initial_count = self._count
        self.root = self._delete_recursive(self.root, key)
        return self._count < initial_count

    def _delete_recursive(self, node: Optional[BSTNode[T]], key: str) -> Optional[BSTNode[T]]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Key matched! Found node to delete.
            self._count -= 1

            # Case 1 & 2: Node has 0 or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 3: Node has 2 children
            # Find in-order successor (smallest node in right subtree)
            successor = self._find_min(node.right)
            node.key = successor.key
            node.value = successor.value
            # Compensate count because recursive call will decrement
            self._count += 1
            node.right = self._delete_recursive(node.right, successor.key)

        return node

    def _find_min(self, node: BSTNode[T]) -> BSTNode[T]:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def inorder_traversal(self) -> List[Tuple[str, T]]:
        """
        In-order traversal (Left -> Root -> Right).
        Produces keys in strictly sorted ascending order.
        """
        result: List[Tuple[str, T]] = []

        def _traverse(node: Optional[BSTNode[T]]) -> None:
            if node:
                _traverse(node.left)
                result.append((node.key, node.value))
                _traverse(node.right)

        _traverse(self.root)
        return result

    def height(self) -> int:
        """Computes tree height: max depth from root to leaf."""
        def _calc_height(node: Optional[BSTNode[T]]) -> int:
            if node is None:
                return 0
            return 1 + max(_calc_height(node.left), _calc_height(node.right))

        return _calc_height(self.root)

    def __contains__(self, key: str) -> bool:
        return self.search(key) is not None

    def __len__(self) -> int:
        return self._count
