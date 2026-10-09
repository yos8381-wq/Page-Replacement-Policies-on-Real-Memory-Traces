"""
Base class for all page replacement policies.
Defines the interface that every policy must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional


class ReplacementPolicy(ABC):
    """
    Abstract base class for page replacement policies.

    Every policy must implement:
      - access(page): called for each memory reference
      - Returns True if page fault occurred, False if hit
    """

    def __init__(self, num_frames: int):
        if num_frames <= 0:
            raise ValueError("num_frames must be positive")
        self.num_frames = num_frames
        self.frames = []          # current pages in memory
        self.page_faults = 0
        self.hits = 0
        self.total_accesses = 0
        self.evictions = 0

    @abstractmethod
    def access(self, page: int) -> bool:
        """
        Process a memory access to `page`.

        Returns:
            True  → page fault (page was not in memory)
            False → page hit (page was already in memory)
        """
        pass

    @abstractmethod
    def _evict(self) -> int:
        """Select and return the victim page to evict."""
        pass

    def _handle_fault(self, page: int) -> None:
        """Handle a page fault: evict if full, then insert."""
        if len(self.frames) >= self.num_frames:
            victim = self._evict()
            self.frames.remove(victim)
            self.evictions += 1
        self.frames.append(page)

    def reset(self) -> None:
        """Reset the policy state for a new simulation."""
        self.frames = []
        self.page_faults = 0
        self.hits = 0
        self.total_accesses = 0
        self.evictions = 0

    def get_stats(self) -> dict:
        """Return performance statistics."""
        return {
            'policy': self.__class__.__name__,
            'num_frames': self.num_frames,
            'total_accesses': self.total_accesses,
            'page_faults': self.page_faults,
            'hits': self.hits,
            'evictions': self.evictions,
            'fault_rate': (self.page_faults / self.total_accesses
                           if self.total_accesses > 0 else 0.0),
            'hit_rate': (self.hits / self.total_accesses
                         if self.total_accesses > 0 else 0.0),
        }
