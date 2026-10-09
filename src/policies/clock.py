"""
Clock (Second Chance) page replacement policy.

Approximates LRU using a circular buffer and a reference bit.
- On a hit: set the reference bit to 1.
- On a fault: scan from the hand position:
    * If bit == 1: give second chance (set bit to 0, advance hand).
    * If bit == 0: evict this page, insert new page (bit = 1), advance hand.
"""

from .base import ReplacementPolicy


class ClockPolicy(ReplacementPolicy):
    """Clock (Second Chance) replacement policy."""

    def __init__(self, num_frames: int):
        super().__init__(num_frames)
        self.frames = []                # pages; index = slot number
        self._ref_bits = []             # parallel list of reference bits
        self._hand = 0                  # clock hand position
        self._page_to_slot = {}         # page -> slot index (for O(1) hits)

    def access(self, page: int) -> bool:
        self.total_accesses += 1

        # HIT
        if page in self._page_to_slot:
            slot = self._page_to_slot[page]
            self._ref_bits[slot] = 1    # second chance granted
            self.hits += 1
            return False

        # FAULT
        self.page_faults += 1

        # Still have empty slots?
        if len(self.frames) < self.num_frames:
            slot = len(self.frames)
            self.frames.append(page)
            self._ref_bits.append(1)
            self._page_to_slot[page] = slot
            return True

        # No empty slot: find a victim via the clock hand
        victim_slot = self._find_victim()
        victim_page = self.frames[victim_slot]
        del self._page_to_slot[victim_page]

        self.frames[victim_slot] = page
        self._ref_bits[victim_slot] = 1
        self._page_to_slot[page] = victim_slot
        self.evictions += 1
        return True

    def _find_victim(self) -> int:
        """Advance the clock hand until a page with ref_bit == 0 is found."""
        while True:
            if self._ref_bits[self._hand] == 0:
                victim_slot = self._hand
                self._hand = (self._hand + 1) % self.num_frames
                return victim_slot
            # Give second chance
            self._ref_bits[self._hand] = 0
            self._hand = (self._hand + 1) % self.num_frames

    def _evict(self) -> int:
        # Clock performs its own eviction inside access();
        # _evict() is not called by the base class for this policy.
        raise NotImplementedError("Clock handles eviction inside access().")

    def reset(self) -> None:
        super().reset()
        self.frames = []
        self._ref_bits = []
        self._hand = 0
        self._page_to_slot = {}
