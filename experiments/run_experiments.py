"""
Run full experiments: all policies x all traces x frame counts.
Saves results to results/experiments.csv
"""

import sys
import os
import csv
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from policies.lru import LRUPolicy
from policies.fifo import FIFOPolicy
from policies.clock import ClockPolicy
from policies.opt import OPTPolicy
from trace.reader import TraceReader


# ============ CONFIGURATION ============
TRACES = {
    'swim': 'traces/real/swim.trace',
    'gcc':  'traces/real/gcc.trace',
    'bzip': 'traces/real/bzip.trace',
}

FRAME_COUNTS = [4, 8, 16, 32, 64, 128, 256, 512, 1024]

POLICIES = {
    'LRU':   LRUPolicy,
    'FIFO':  FIFOPolicy,
    'Clock': ClockPolicy,
    'OPT':   OPTPolicy,
}

PAGE_SIZE = 4096
MAX_REFERENCES = None   # None = use full trace; set to e.g. 100000 for quick runs
OUTPUT_CSV = 'results/experiments.csv'


def run_one(policy_name, PolicyClass, num_frames, pages):
    """Run a single experiment and return stats dict."""
    t0 = time.time()
    if policy_name == 'OPT':
        policy = PolicyClass(num_frames=num_frames, trace=pages)
    else:
        policy = PolicyClass(num_frames=num_frames)

    for p in pages:
        policy.access(p)

    stats = policy.get_stats()
    stats['runtime_seconds'] = round(time.time() - t0, 2)
    return stats


def main():
    os.makedirs('results', exist_ok=True)

    rows = []
    total = len(TRACES) * len(FRAME_COUNTS) * len(POLICIES)
    done = 0

    for trace_name, trace_path in TRACES.items():
        print(f'\n=== Loading {trace_name}.trace ===')
        reader = TraceReader(trace_path)
        pages = reader.to_page_sequence(page_size=PAGE_SIZE)
        if MAX_REFERENCES:
            pages = pages[:MAX_REFERENCES]
        print(f'  {len(pages):,} references, '
              f'{len(set(pages)):,} unique pages')

        for num_frames in FRAME_COUNTS:
            for policy_name, PolicyClass in POLICIES.items():
                stats = run_one(policy_name, PolicyClass,
                                num_frames, pages)
                rows.append({
                    'trace': trace_name,
                    'policy': policy_name,
                    'num_frames': num_frames,
                    'total_accesses': stats['total_accesses'],
                    'page_faults': stats['page_faults'],
                    'hits': stats['hits'],
                    'evictions': stats['evictions'],
                    'fault_rate': round(stats['fault_rate'], 6),
                    'hit_rate': round(stats['hit_rate'], 6),
                    'runtime_seconds': stats['runtime_seconds'],
                })
                done += 1
                print(f'  [{done:3d}/{total}] {trace_name:5s} '
                      f'frames={num_frames:4d} {policy_name:6s} '
                      f'faults={stats["page_faults"]:,}')

    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f'\n*** DONE! Results saved to {OUTPUT_CSV} ***')
    print(f'*** Total experiments: {len(rows)} ***')


if __name__ == '__main__':
    main()
