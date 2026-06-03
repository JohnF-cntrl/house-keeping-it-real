import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import os


def plot_fold_changes(df, gene_col, treatment_col, output_dir='outputs', lmm_pvalues=None):
    """
    Generate an interactive Plotly bar chart of fold changes
    with error bars and significance markers.
    Returns a Plotly figure object.
    """
    fold_change_col = f'fold_change_{gene_col}'

    summary = df.groupby(treatment_col)[fold_change_col].agg(
        ['mean', 'sem']).reset_index()
    summary.columns = [treatment_col, 'mean', 'sem']
    summary['sem'] = summary['sem'].fillna(0)

    color_map = {
        'Vehicle': '#4CAF50',
        'BPA':     '#F44336',
        'E2':      '#2196F3',
    }
    bar_colors = [color_map.get(t, '#9E9E9E') for t in summary[treatment_col]]

    gene_display = gene_col.replace('_ct', '').upper()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=summary[treatment_col],
        y=summary['mean'],
        error_y=dict(
            type='data',
            array=summary['sem'].tolist(),
            visible=True,
            color='#333333',
            thickness=1.5,
            width=6
        ),
        marker=dict(
            color=bar_colors,
            line=dict(color='#333333', width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>Mean Fold Change: %{y:.4f}<extra></extra>',
        name=''
    ))

    fig.add_hline(
        y=1,
        line_dash='dash',
        line_color='#999999',
        line_width=1.2
    )

    annotations = build_significance_annotations(
        df, summary, treatment_col, fold_change_col, lmm_pvalues
    )
    for ann in annotations:
        fig.add_annotation(ann)

    shapes = build_significance_shapes(
        df, summary, treatment_col, fold_change_col, lmm_pvalues
    )
    for shape in shapes:
        fig.add_shape(shape)

    fig.update_layout(
        title=dict(
            text=f'{gene_display} Expression — Fold Change vs Vehicle',
            font=dict(size=16, color='#1F4E79'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Treatment Group', font=dict(size=13)),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(text='Fold Change (2<sup>-ΔΔCt</sup>)',
                       font=dict(size=13)),
            tickfont=dict(size=12),
            rangemode='tozero'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        width=600,
        height=480,
        margin=dict(t=80, b=60, l=70, r=40)
    )

    fig.update_xaxes(showgrid=False, showline=True, linecolor='#CCCCCC')
    fig.update_yaxes(showgrid=True, gridcolor='#EEEEEE',
                     showline=True, linecolor='#CCCCCC')

    # Try to save PNG if kaleido is installed
    os.makedirs(output_dir, exist_ok=True)
    try:
        fig.write_image(f'{output_dir}/{gene_display}_fold_change.png')
    except Exception:
        pass

    return fig


def build_significance_annotations(df, summary, treatment_col, fold_change_col, lmm_pvalues):
    groups = summary[treatment_col].tolist()
    means = summary['mean'].tolist()
    annotations = []

    if len(groups) < 2:
        return annotations

    control_group = groups[0]
    control_data = df[df[treatment_col] == control_group][fold_change_col]
    non_control = [g for g in groups if g != control_group]

    if not non_control:
        return annotations

    max_y = max(means)
    y_offset = max_y * 1.12

    for group in non_control:
        x1 = groups.index(control_group)
        x2 = groups.index(group)

        if lmm_pvalues and group in lmm_pvalues:
            p = lmm_pvalues[group]
            suffix = " (LMM)"
        else:
            sample_data = df[df[treatment_col] == group][fold_change_col]
            if len(control_data) < 2 or len(sample_data) < 2:
                y_offset *= 1.18
                continue
            _, p = stats.ttest_ind(control_data, sample_data)
            suffix = " (t-test)"

        if p < 0.001:
            marker = f'***{suffix}'
        elif p < 0.01:
            marker = f'**{suffix}'
        elif p < 0.05:
            marker = f'*{suffix}'
        else:
            marker = f'ns{suffix}'

        annotations.append(dict(
            x=(x1 + x2) / 2,
            y=y_offset * 1.04,
            text=marker,
            showarrow=False,
            font=dict(size=11, color='#333333'),
            xref='x',
            yref='y'
        ))
        y_offset *= 1.18

    return annotations


def build_significance_shapes(df, summary, treatment_col, fold_change_col, lmm_pvalues):
    groups = summary[treatment_col].tolist()
    means = summary['mean'].tolist()
    shapes = []

    if len(groups) < 2:
        return shapes

    control_group = groups[0]
    control_data = df[df[treatment_col] == control_group][fold_change_col]
    non_control = [g for g in groups if g != control_group]

    if not non_control:
        return shapes

    max_y = max(means)
    y_offset = max_y * 1.12

    for group in non_control:
        x1 = groups.index(control_group)
        x2 = groups.index(group)

        if lmm_pvalues and group in lmm_pvalues:
            p = lmm_pvalues[group]
        else:
            sample_data = df[df[treatment_col] == group][fold_change_col]
            if len(control_data) < 2 or len(sample_data) < 2:
                y_offset *= 1.18
                continue
            _, p = stats.ttest_ind(control_data, sample_data)

        for shape in [
            dict(type='line', x0=x1, x1=x1, y0=y_offset, y1=y_offset * 1.02,
                 xref='x', yref='y', line=dict(color='#333333', width=1)),
            dict(type='line', x0=x1, x1=x2, y0=y_offset * 1.02, y1=y_offset * 1.02,
                 xref='x', yref='y', line=dict(color='#333333', width=1)),
            dict(type='line', x0=x2, x1=x2, y0=y_offset, y1=y_offset * 1.02,
                 xref='x', yref='y', line=dict(color='#333333', width=1)),
        ]:
            shapes.append(shape)

        y_offset *= 1.18

    return shapes


def plot_litter_variance(pct_litter, pct_residual, gene_col):
    gene_display = gene_col.replace('_ct', '').upper()

    fig = go.Figure(data=[go.Pie(
        labels=['Litter effect', 'Residual'],
        values=[pct_litter, pct_residual],
        hole=0.3,
        marker=dict(
            colors=['#F44336', '#4CAF50'],
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>',
        textinfo='label+percent',
        textfont=dict(size=13)
    )])

    fig.update_layout(
        title=dict(
            text=f'{gene_display} — Variance Explained by Litter',
            font=dict(size=14, color='#1F4E79'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        height=400,
        width=450,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor='white'
    )

    return fig
