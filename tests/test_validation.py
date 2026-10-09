"""
Validation test: reproduce textbook results from Silberschatz et al.,
Operating System Concepts, 10th ed., Chapter 10.
Reference string: 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1
Number of frames: 3
Expected: FIFO=15, LRU=12, OPT=9
"""

import sys
sys.path.insert(0, 'src')

from policies.lru import LRUPolicy
from policies.fifo import FIFOPolicy
from policies.opt import OPTPolicy


def run_test():
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3,
                        0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    num_frames = 3

    results = {}

    # FIFO
    fifo = FIFOPolicy(num_frames=num_frames)
    for p in reference_string:
        fifo.access(p)
    results['FIFO'] = fifo.page_faults

    # LRU
    lru = LRUPolicy(num_frames=num_frames)
    for p in reference_string:
        lru.access(p)
    results['LRU'] = lru.page_faults

    # OPT
    opt = OPTPolicy(num_frames=num_frames, trace=reference_string)
    for p in reference_string:
        opt.access(p)
    results['OPT'] = opt.page_faults

    # Expected values from Silberschatz
    expected = {'FIFO': 15, 'LRU': 12, 'OPT': 9}

    print('=' * 50)
    print('TEXTBOOK VALIDATION (Silberschatz, 10th ed., Ch. 10)')
    print('=' * 50)
    print(f'Reference string: {reference_string}')
    print(f'Number of frames: {num_frames}')
    print()

    all_passed = True
    for policy in ['FIFO', 'LRU', 'OPT']:
        actual = results[policy]
        exp = expected[policy]
        status = '[PASS]' if actual == exp else '[FAIL]'
        if actual != exp:
            all_passed = False
        print(f'{policy:6s}  expected={exp:3d}  actual={actual:3d}  {status}')

    print()
    if all_passed:
        print('*** ALL TESTS PASSED - Simulator is valid! ***')
    else:
        print('*** SOME TESTS FAILED - Check implementation! ***')

    return all_passed


if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
