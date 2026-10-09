"""
Trace reader for memory reference traces.
Supports multiple formats:
  Format A: <hex_address> <R|W>
  Format B: # <n> <hex_address> <n>   (found in swim.trace, gcc.trace, bzip.trace)
"""

from dataclasses import dataclass
from typing import Iterator, List
from pathlib import Path


@dataclass
class MemoryReference:
    """A single memory reference (address + operation)."""
    address: int
    operation: str  # 'R' or 'W'
    line_number: int = 0


class TraceReader:
    """Reads memory reference traces from files."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Trace file not found: {filepath}")

    def _parse_line(self, line: str, line_num: int):
        """Parses a single line and returns (address, operation) or None."""
        parts = line.split()
        if not parts:
            return None

        # Format B: # <n> <hex_address> <n>
        if parts[0] == '#' and len(parts) >= 3:
            try:
                address = int(parts[2], 16)
                operation = 'R'  # default; can be refined later
                return address, operation
            except ValueError:
                return None

        # Format A: <hex_address> <R|W>
        try:
            address = int(parts[0], 16)
            operation = parts[1] if len(parts) > 1 else 'R'
            if operation not in ('R', 'W'):
                operation = 'R'
            return address, operation
        except ValueError:
            return None

    def read(self) -> Iterator[MemoryReference]:
        """Yields MemoryReference objects from the trace file."""
        with open(self.filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                parsed = self._parse_line(line, line_num)
                if parsed is None:
                    continue
                address, operation = parsed
                yield MemoryReference(address, operation, line_num)

    def to_page_sequence(self, page_size: int = 4096) -> List[int]:
        """Converts memory references to a sequence of page numbers."""
        return [ref.address // page_size for ref in self.read()]
