"""
Stack Distance analysis.

Stack Distance for a reference = number of DISTINCT pages referenced
between the current reference and the previous reference to the same page.
- First-time references get distance = infinity (compulsory misses).
- Small distances -> high locality -> LRU should win.
- Large distances -> scan-heavy -> FIFO may be competitive.
"""

import sys
import os
from collections import OrderedDict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def compute_stack_distances(pages, max_refs=20000):
    """
    Compute stack distances for a sequence of page references.
    Capped at max_refs for performance (O(n^2) in the worst case).
    """
    pages = pages[:max_refs]
    recent = []              # MRU at end
    distances = []
    for page in pages:
        try:
            idx = recent.index(page)
            distance = len(recent) - idx - 1
            recent.pop(idx)
            recent.append(page)
            distances.append(distance)
        except ValueError:
            distances.append(np.inf)
            recent.append(page)
    return distances


def analyze_trace(pages, trace_name, output_dir, max_refs=20000):
    """Compute stack distances and generate plots."""
    print(f'  Computing stack distances for {trace_name} '
          f'(first {max_refs:,} refs)...')
    distances = compute_stack_distances(pages, max_refs=max_refs)

    # Separate compulsory misses
    finite = np.array([d for d in distances if np.isfinite(d)])
    compulsory = sum(1 for d in distances if np.isinf(d))

    # Statistics
    stats = {
        'trace': trace_name,
        'total_refs': len(distances),
        'compulsory_misses': compulsory,
        'mean_distance': float(np.mean(finite)) if len(finite) else 0,
        'median_distance': float(np.median(finite)) if len(finite) else 0,
        'p90_distance': float(np.percentile(finite, 90)) if len(finite) else 0,
        'p99_distance': float(np.percentile(finite, 99)) if len(finite) else 0,
        'max_distance': float(np.max(finite)) if len(finite) else 0,
    }

    # Histogram (log-binned)
    fig, ax = plt.subplots(figsize=(8, 5))
    max_d = int(stats['p99_distance']) + 1
    bins = np.arange(0, max_d + 2, max(1, max_d // 60))
    ax.hist(finite, bins=bins, color='steelblue',
            edgecolor='black', alpha=0.7)
    ax.axvline(stats['mean_distance'], color='red', linestyle='--',
               linewidth=2, label=f'Mean = {stats["mean_distance"]:.1f}')
    ax.axvline(stats['median_distance'], color='green', linestyle='--',
               linewidth=2, label=f'Median = {stats["median_distance"]:.1f}')
    ax.set_xlabel('Stack Distance (distinct pages)')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Stack Distance Distribution — {trace_name}.trace')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(output_dir, f'stack_distance_{trace_name}.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f'    Saved: {out}')

    return stats


def main():
    sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), '..')))
    from trace.reader import TraceReader

    output_dir = 'results/plots'
    os.makedirs(output_dir, exist_ok=True)

    traces = {
        'swim': 'traces/real/swim.trace',
        'gcc':  'traces/real/gcc.trace',
        'bzip': 'traces/real/bzip.trace',
    }

    all_stats = []
    for name, path in traces.items():
        print(f'\n=== {name} ===')
        reader = TraceReader(path)
        pages = reader.to_page_sequence(page_size=4096)
        stats = analyze_trace(pages, name, output_dir, max_refs=20000)
        all_stats.append(stats)
        for k, v in stats.items():
            if k != 'trace':
                print(f'    {k:20s}: {v}')

    # Save summary
    df = pd.DataFrame(all_stats)
    df.to_csv('results/stack_distance_summary.csv', index=False)
    print('\n*** Summary saved to results/stack_distance_summary.csv ***')


if __name__ == '__main__':
    main()
