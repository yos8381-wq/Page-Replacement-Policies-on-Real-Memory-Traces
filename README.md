# Page Replacement Policies on Real Memory Traces
## LRU, Clock, FIFO, and Optimal Compared in Python

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Complete](https://img.shields.io/badge/status-complete-brightgreen.svg)]()

A validated, open-source simulation study comparing four classical page 
replacement policies — **LRU**, **Clock (Second Chance)**, **FIFO**, and 
**OPT (Belady's Optimal)** — on **real memory traces** from the SPEC 
benchmark suite (SWIM, GCC, BZIP2).

This work is part of a Master's research project in Advanced Operating 
Systems. It addresses three research questions:

- **RQ1:** How large is the page-fault-rate gap between LRU, Clock, and 
  FIFO relative to the theoretical OPT on real application traces?
- **RQ2:** How does the gap change with available frame count, and where 
  is the "knee of the curve"?
- **RQ3:** Can simple stack-distance features of a trace predict which 
  practical policy performs best?

---

## 📊 Key Results

### 1. Textbook Validation — 100% Match

The simulator reproduces exact textbook results from Silberschatz et al. 
(*Operating System Concepts*, 10th ed., Chapter 10):

| Policy | Expected | Actual | Status |
|:-------|:--------:|:------:|:------:|
| FIFO   | 15       | 15     | ✅ PASS |
| LRU    | 12       | 12     | ✅ PASS |
| OPT    | 9        | 9      | ✅ PASS |

*Reference string: `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1` with 3 frames.*

### 2. Policy Ranking on Real Traces

A total of **108 experiments** (4 policies × 9 frame counts × 3 traces) 
confirmed the classical ranking:
