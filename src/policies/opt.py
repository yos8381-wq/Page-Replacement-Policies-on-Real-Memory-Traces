"""
OPT (Optimal / Belady's) page replacement policy.

At each fault, evicts the page whose next use is farthest in the future.
Requires full knowledge of the trace — used as a theoretical lower bound.

Implementation:
- On construction, we precompute for each page the sorted list of positions
  where it appears in the trace.
- During access, we track a pointer `_pos` into the trace and use the
  precomputed lists to determine the "next use" of every resident page.
"""

from collections import defaultdict, deque
from .base import ReplacementPolicy


class OPTPolicy(ReplacementPolicy):
    """Optimal (Belady's) replacement policy."""

    def __init__(self, num_frames: int, trace=None):
        """
        Args:
            num_frames: number of physical frames
            trace: the full page sequence (list of ints). If None, OPT
                   cannot function correctly. Must be provided before access().
        """
        super().__init__(num_frames)
        self._trace = list(trace) if trace is not None else []
        self._pos = 0
        self._future = self._build_future_index(self._trace) if self._trace else {}

    @staticmethod
    def _build_future_index(trace):
        """Map page -> deque of positions (in increasing order)."""
        future = defaultdict(deque)
        for pos, page in enumerate(trace):
            future[page].append(pos)
        return future

    def set_trace(self, trace):
        """Set the trace and rebuild the future index."""
        self._trace = list(trace)
        self._pos = 0
        self._future = self._build_future_index(self._trace)

    def access(self, page: int) -> bool:
        if not self._trace:
            raise RuntimeError("OPT requires a trace. Call set_trace() first.")

        self.total_accesses += 1

        # Advance the pointer through the future lists: remove past positions
        # for the current page (should be at the front).
        self._consume_position(page)

        # HIT
        if page in self.frames:
            self.hits += 1
            self._pos += 1
            return False

        # FAULT
        self.page_faults += 1

        if len(self.frames) < self.num_frames:
            self.frames.append(page)
        else:
            victim = self._evict()
            self.frames.remove(victim)
            self.evictions += 1
            self.frames.append(page)

        self._pos += 1
        return True

    def _consume_position(self, page: int):
        """Remove the current position of `page` from its future list."""
        if page in self._future and self._future[page]:
            # The first element should be the current position
            if self._future[page][0] == self._pos:
                self._future[page].popleft()

    def _next_use(self, page: int):
        """Return the next position where `page` will be used, or infinity."""
        if page in self._future and self._future[page]:
            return self._future[page][0]
        return float('inf')

    def _evict(self) -> int:
        """Evict the page whose next use is farthest in the future."""
        victim = None
        farthest = -1
        for p in self.frames:
            nxt = self._next_use(p)
            if nxt > farthest:
                farthest = nxt
                victim = p
        return victim

    def reset(self) -> None:
        super().reset()
        self._pos = 0
        self._future = self._build_future_index(self._trace) if self._trace else {}
