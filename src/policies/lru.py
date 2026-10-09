"""
LRU (Least Recently Used) page replacement policy.

Evicts the page that has not been used for the longest time.
Uses an OrderedDict to track recency in O(1) per access.
"""

from collections import OrderedDict
from .base import ReplacementPolicy


class LRUPolicy(ReplacementPolicy):
    """Least Recently Used replacement policy."""

    def __init__(self, num_frames: int):
        super().__init__(num_frames)
        # OrderedDict: most recently used at the end
        self._recency = OrderedDict()

    def access(self, page: int) -> bool:
        self.total_accesses += 1

        if page in self._recency:
            # HIT: move page to the most-recent position
            self._recency.move_to_end(page)
            self.hits += 1
            return False

        # FAULT
        self.page_faults += 1
        self._handle_fault(page)
        self._recency[page] = True
        return True

    def _evict(self) -> int:
        # Evict the least-recently used page (first item in OrderedDict)
        victim, _ = self._recency.popitem(last=False)
        return victim

    def reset(self) -> None:
        super().reset()
        self._recency = OrderedDict()
