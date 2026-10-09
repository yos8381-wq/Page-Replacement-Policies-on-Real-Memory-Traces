"""
Predictive Framework for Page Replacement Policy Selection.

Given a memory trace, this module predicts which policy (LRU, Clock,
FIFO) will perform closest to OPT WITHOUT running full simulations.

Prediction rule (derived empirically from stack distance analysis):
  1. Compute Stack Distance statistics (median, p90, p99, max).
  2. Categorize the trace:
       - TIGHT      : median < 2 and p90 < 5     -> Any policy works
       - HEAVY_TAIL : p99 > 100                  -> OPT wins big; use Clock
       - MODERATE   : otherwise                  -> LRU wins; Clock close
"""

import sys
import os
import numpy as np


def compute_stack_distances(pages, max_refs=20000):
    """Compute stack distances for a sequence of page references."""
    pages = pages[:max_refs]
    recent = []
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


def classify_trace(pages, max_refs=20000):
    """Classify a trace based on its stack distance distribution."""
    distances = compute_stack_distances(pages, max_refs=max_refs)
    finite = np.array([d for d in distances if np.isfinite(d)])

    if len(finite) == 0:
        return {'category': 'EMPTY', 'recommendation': 'No data'}

    median = float(np.median(finite))
    p90 = float(np.percentile(finite, 90))
    p99 = float(np.percentile(finite, 99))
    max_d = float(np.max(finite))

    if p99 > 100:
        category = 'HEAVY_TAIL'
        recommendation = 'Clock (closest to LRU with low overhead)'
        reason = ('Long tail (p99=%.0f) makes LRU and FIFO '
                  'vulnerable; OPT wins by a large margin.' % p99)
    elif median < 2 and p90 < 5:
        category = 'TIGHT'
        recommendation = 'Any policy works; FIFO is cheapest'
        reason = ('Tight locality (median=%.1f, p90=%.0f); '
                  'all practical policies perform similarly.'
                  % (median, p90))
    else:
        category = 'MODERATE'
        recommendation = 'LRU (with Clock as a low-overhead alternative)'
        reason = ('Moderate locality (median=%.1f); '
                  'LRU fits the distribution well.' % median)

    return {
        'category': category,
        'median': median,
        'p90': p90,
        'p99': p99,
        'max': max_d,
        'recommendation': recommendation,
        'reason': reason,
    }


def main():
    sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), '..')))
    from trace.reader import TraceReader

    traces = {
        'swim': 'traces/real/swim.trace',
        'gcc':  'traces/real/gcc.trace',
        'bzip': 'traces/real/bzip.trace',
    }

    print('=' * 70)
    print('PREDICTIVE FRAMEWORK - Policy Recommendation from Stack Distance')
    print('=' * 70)

    for name, path in traces.items():
        reader = TraceReader(path)
        pages = reader.to_page_sequence(page_size=4096)
        result = classify_trace(pages, max_refs=20000)

        print('')
        print('--- ' + name + '.trace ---')
        print('  Category      : ' + result['category'])
        print('  Median        : %.1f' % result['median'])
        print('  P90 / P99     : %.1f / %.1f' % (result['p90'], result['p99']))
        print('  Max distance  : %.0f' % result['max'])
        print('  RECOMMENDATION: ' + result['recommendation'])
        print('  Reason        : ' + result['reason'])

    print('')
    print('=' * 70)


if __name__ == '__main__':
    main()
