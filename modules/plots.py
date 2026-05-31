import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

def plot_fold_changes(df, gene_col, treatment_col, output_dir='outputs', lmm_pvalues=None):
    """
    Generate a publication-ready bar plot of fold changes
    with error bars and significance markers.
    lmm_pvalues: optional dict of {treatment_group: p_value} from LMM
    """
    fold_change_col = f'fold_change_{gene_col}'
    
    # Calculate mean and SEM per treatment group
    summary = df.groupby(treatment_col)[fold_change_col].agg(['mean', 'sem']).reset_index()
    summary.columns = [treatment_col, 'mean', 'sem']
    
    # Color palette
    colors = {'Vehicle': '#4CAF50', 'BPA': '#F44336', 'E2': '#2196F3'}
    bar_colors = [colors.get(t, '#9E9E9E') for t in summary[treatment_col]]
    
    # Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(
        summary[treatment_col],
        summary['mean'],
        yerr=summary['sem'],
        color=bar_colors,
        edgecolor='black',
        linewidth=0.8,
        capsize=5,
        width=0.5,
        error_kw={'elinewidth': 1.5, 'ecolor': 'black'}
    )
    
    # Reference line at fold change = 1
    ax.axhline(y=1, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Labels
    gene_display = gene_col.replace('_ct', '').upper()
    ax.set_title(f'{gene_display} Expression — Fold Change vs Vehicle',
                 fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Treatment Group', fontsize=11)
    ax.set_ylabel('Fold Change (2^-ΔΔCt)', fontsize=11)
    ax.set_ylim(bottom=0)
    
    # Significance markers
    add_significance_markers(ax, df, treatment_col, fold_change_col, summary, lmm_pvalues)
    
    plt.tight_layout()
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    filename = f'{output_dir}/{gene_display}_fold_change.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
    return filename

def add_significance_markers(ax, df, treatment_col, fold_change_col, summary, lmm_pvalues=None):
    """
    Add significance markers (* p<0.05, ** p<0.01, *** p<0.001).
    Uses LMM p-values if provided, otherwise falls back to t-test.
    """
    groups = summary[treatment_col].tolist()
    means = summary['mean'].tolist()
    control = df[df[treatment_col] == 'Vehicle'][fold_change_col]
    
    y_offset = max(means) * 1.05

    for i, group in enumerate(groups):
        if group == 'Vehicle':
            continue

        # Use LMM p-value if available, otherwise t-test
        if lmm_pvalues and group in lmm_pvalues:
            p = lmm_pvalues[group]
            label_suffix = " (LMM)"
        else:
            _, p = stats.ttest_ind(control, df[df[treatment_col] == group][fold_change_col])
            label_suffix = " (t-test)"

        if p < 0.001:
            marker = f'***{label_suffix}'
        elif p < 0.01:
            marker = f'**{label_suffix}'
        elif p < 0.05:
            marker = f'*{label_suffix}'
        else:
            marker = f'ns{label_suffix}'

        x1 = groups.index('Vehicle')
        x2 = i
        ax.plot([x1, x1, x2, x2],
                [y_offset, y_offset * 1.02, y_offset * 1.02, y_offset],
                color='black', linewidth=1)
        ax.text((x1 + x2) / 2, y_offset * 1.03, marker,
                ha='center', va='bottom', fontsize=9)
        y_offset *= 1.15

def plot_litter_variance(pct_litter, pct_residual, gene_col, output_dir='outputs'):
    """
    Pie chart showing variance explained by litter vs residual.
    """
    gene_display = gene_col.replace('_ct', '').upper()
    
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        [pct_litter, pct_residual],
        labels=[f'Litter effect\n({pct_litter}%)', f'Residual\n({pct_residual}%)'],
        colors=['#F44336', '#4CAF50'],
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax.set_title(f'{gene_display} — Variance Explained by Litter',
                 fontsize=12, fontweight='bold', pad=12)
    
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    filename = f'{output_dir}/{gene_display}_litter_variance.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
    return filename