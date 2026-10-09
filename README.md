# Page Replacement Policies on Real Memory Traces
## LRU, Clock, FIFO, and Optimal Compared in Python

A validated, open-source simulation study comparing four classical page replacement policies (LRU, Clock, FIFO, and OPT) on real memory traces from the SPEC benchmark suite (SWIM, GCC, BZIP2).

This work is part of a Master's research project in Advanced Operating Systems. It addresses three research questions:

- RQ1: How large is the page-fault-rate gap between LRU, Clock, and FIFO relative to the theoretical OPT on real application traces?
- RQ2: How does the gap change with available frame count, and where is the "knee of the curve"?
- RQ3: Can simple stack-distance features of a trace predict which practical policy performs best?

---

## Key Results

### 1. Textbook Validation - 100% Match

The simulator reproduces exact textbook results from Silberschatz et al. (Operating System Concepts, 10th ed., Chapter 10):

| Policy | Expected | Actual | Status |
|:-------|:--------:|:------:|:------:|
| FIFO   | 15       | 15     | PASS   |
| LRU    | 12       | 12     | PASS   |
| OPT    | 9        | 9      | PASS   |

Reference string: 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1 with 3 frames.

### 2. Policy Ranking on Real Traces

A total of 108 experiments (4 policies x 9 frame counts x 3 traces) confirmed the classical ranking:

    OPT < LRU < Clock < FIFO

with Clock consistently closer to LRU than to FIFO, empirically validating the theoretical claim that Clock approximates LRU.

### 3. Non-Monotonic Gap Behavior (Novel Finding)

The gap between practical policies and OPT does not always shrink with more frames. On gcc.trace, the gap grows from ~55% at 4 frames to ~180% at 256 frames before collapsing - an effect we call "Belady's Inverse Anomaly".

### 4. Predictive Framework from Stack Distance

Based on the Stack Distance Histogram, we classify any trace into one of three categories:

| Category   | Detection Rule         | Recommendation              |
|:-----------|:-----------------------|:----------------------------|
| TIGHT      | median < 2 and p90 < 5 | Any policy (FIFO cheapest)  |
| MODERATE   | otherwise              | LRU (Clock alternative)     |
| HEAVY_TAIL | p99 > 100              | Clock (closest to LRU)      |

Result: The framework correctly predicted the best policy for all three SPEC traces without running any full simulation.

---

## Repository Structure

    page-replacement-simulator/
    |
    +-- src/                          # Source code
    |   +-- trace/reader.py           # Trace file parser
    |   +-- policies/                 # LRU, FIFO, Clock, OPT
    |   +-- analysis/
    |       +-- plots.py              # Publication figures
    |       +-- stack_distance.py     # Stack distance histograms
    |       +-- predictor.py          # Predictive framework (RQ3)
    |
    +-- experiments/
    |   +-- run_experiments.py        # Runs 108 experiments
    |
    +-- tests/
    |   +-- test_validation.py        # Textbook validation
    |
    +-- results/
    |   +-- experiments.csv
    |   +-- stack_distance_summary.csv
    |   +-- plots/                    # 8 PNG figures (300 DPI)
    |
    +-- requirements.txt
    +-- LICENSE
    +-- README.md

---

## Quick Start

1. Install dependencies:

       pip install -r requirements.txt

2. Download SPEC traces (swim, gcc, bzip) and place in traces/real/.

3. Validate simulator:

       python3 tests/test_validation.py

4. Run experiments:

       python3 experiments/run_experiments.py

5. Generate plots:

       python3 src/analysis/plots.py

6. Apply predictive framework:

       python3 src/analysis/predictor.py

---

## Methodology

### Trace Collection

| Trace  | Type             | References | Unique Pages |
|:-------|:-----------------|:----------:|:------------:|
| swim   | Floating-point   | 1,520,886  | 1,503        |
| gcc    | Integer/compiler | 1,000,000  | 2,852        |
| bzip   | Compression      | 1,000,000  | 317          |

### Experimental Design

- Independent variables: policy (4), frame count (9), trace (3)
- Dependent variable: page fault rate
- Page size: 4096 bytes
- Total experiments: 108

---

## Novel Contributions

1. Systematic multi-policy comparison on real traces.
2. Validated, open-source Python simulator.
3. Predictive framework based on Stack Distance.
4. Quantitative "knee of the curve" analysis.
5. Documented non-monotonic gap behavior.

---

## References

1. L. A. Belady, IBM Systems Journal, 5(2), 1966.
2. P. J. Denning, Communications of the ACM, 11(5), 1968.
3. A. Silberschatz et al., Operating System Concepts, 10th ed., 2018.
4. A. S. Tanenbaum and H. Bos, Modern Operating Systems, 5th ed., 2023.
5. R. H. Arpaci-Dusseau and A. C. Arpaci-Dusseau, OSTEP, 2018.

---

## Author

Maged Dahaq - Computing Master's Student
GitHub: @yos8381-wq

## Acknowledgments

This work was conducted under the supervision of 
Dr. Wedad al-Sorori, Department of Computer Science – Lecturer – Graduate Studies – Advanced Operating Systems, 
University of Science and Technology, Sana'a, Yemen.


## License

MIT License. See LICENSE file for details.
