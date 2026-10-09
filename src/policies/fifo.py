"""
FIFO (First-In-First-Out) page replacement policy.

Evicts the page that was loaded into memory earliest,
regardless of how recently or frequently it has been used.
"""

from collections import deque
from .base import ReplacementPolicy


class FIFOPolicy(ReplacementPolicy):
    """First-In-First-Out replacement policy."""

    def __init__(self, num_frames: int):
        super().__init__(num_frames)
        self._queue = deque()  # insertion order

    def access(self, page: int) -> bool:
        self.total_accesses += 1

        if page in self.frames:
            self.hits += 1
            return False

        # FAULT
        self.page_faults += 1
        self._handle_fault(page)   # removes victim from frames if full
        self._queue.append(page)   # record arrival time
        return True

    def _evict(self) -> int:
        # Oldest page = first item in the queue
        return self._queue.popleft()

    def reset(self) -> None:
        super().reset()
        self._queue = deque()
