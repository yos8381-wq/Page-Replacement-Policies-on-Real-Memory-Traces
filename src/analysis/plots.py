"""
Generate publication-quality plots from experimental results.
Output: results/plots/*.png
"""

import sys
import os
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')   # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


# Aesthetic settings for publication
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['legend.fontsize'] = 10

# Consistent colors across plots
COLORS = {
    'OPT':   '#2E86AB',   # Blue
    'LRU':   '#A23B72',   # Magenta
    'Clock': '#F18F01',   # Orange
    'FIFO':  '#C73E1D',   # Red
}
MARKERS = {'OPT': 'o', 'LRU': 's', 'Clock': '^', 'FIFO': 'D'}


def plot_fault_rate_vs_frames(df, trace_name, output_dir):
    """One plot per trace: fault rate vs. number of frames."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sub = df[df['trace'] == trace_name]

    for policy in ['OPT', 'LRU', 'Clock', 'FIFO']:
        data = sub[sub['policy'] == policy].sort_values('num_frames')
        ax.plot(data['num_frames'], data['fault_rate'] * 100,
                marker=MARKERS[policy], color=COLORS[policy],
                label=policy, linewidth=2, markersize=7)

    ax.set_xscale('log', base=2)
    ax.set_xlabel('Number of Frames (log₂ scale)')
    ax.set_ylabel('Page Fault Rate (%)')
    ax.set_title(f'Page Fault Rate vs. Frame Count — {trace_name}.trace')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(output_dir, f'fault_rate_{trace_name}.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f'  Saved: {out}')


def plot_all_traces_comparison(df, output_dir):
    """One plot per policy: comparison across the three traces."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    for ax, trace_name in zip(axes, ['swim', 'gcc', 'bzip']):
        sub = df[df['trace'] == trace_name]
        for policy in ['OPT', 'LRU', 'Clock', 'FIFO']:
            data = sub[sub['policy'] == policy].sort_values('num_frames')
            ax.plot(data['num_frames'], data['fault_rate'] * 100,
                    marker=MARKERS[policy], color=COLORS[policy],
                    label=policy, linewidth=2, markersize=6)
        ax.set_xscale('log', base=2)
        ax.set_xlabel('Number of Frames')
        ax.set_ylabel('Page Fault Rate (%)')
        ax.set_title(f'{trace_name}.trace')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(output_dir, 'comparison_all_traces.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f'  Saved: {out}')


def plot_policy_gap_analysis(df, output_dir):
    """Plot the gap between each policy and OPT (as % increase)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax, trace_name in zip(axes, ['swim', 'gcc', 'bzip']):
        sub = df[df['trace'] == trace_name]
        opt = sub[sub['policy'] == 'OPT'].set_index('num_frames')['fault_rate']

        for policy in ['LRU', 'Clock', 'FIFO']:
            data = sub[sub['policy'] == policy].set_index('num_frames')
            # Only where OPT > 0
            valid = opt > 0
            gap_pct = ((data['fault_rate'][valid] - opt[valid]) / opt[valid]) * 100
            ax.plot(gap_pct.index, gap_pct.values,
                    marker=MARKERS[policy], color=COLORS[policy],
                    label=f'{policy} vs. OPT', linewidth=2, markersize=7)

        ax.set_xscale('log', base=2)
        ax.set_xlabel('Number of Frames')
        ax.set_ylabel('Fault Rate Increase over OPT (%)')
        ax.set_title(f'{trace_name}.trace')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = os.path.join(output_dir, 'gap_vs_opt.png')
    plt.savefig(out, dpi=300)
    plt.close()
    print(f'  Saved: {out}')


def main():
    csv_path = 'results/experiments.csv'
    output_dir = 'results/plots'
    os.makedirs(output_dir, exist_ok=True)

    print(f'Loading {csv_path}...')
    df = pd.read_csv(csv_path)
    print(f'  {len(df)} experiments loaded')

    print('\nGenerating plots...')
    for trace_name in ['swim', 'gcc', 'bzip']:
        plot_fault_rate_vs_frames(df, trace_name, output_dir)
    plot_all_traces_comparison(df, output_dir)
    plot_policy_gap_analysis(df, output_dir)

    print(f'\n*** All plots saved to {output_dir}/ ***')


if __name__ == '__main__':
    main()
