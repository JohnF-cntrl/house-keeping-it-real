import pandas as pd
import numpy as np


def calculate_delta_ct(df, gene_col, housekeeping_col):
    """
    Calculate ΔCt = Ct(gene of interest) - Ct(housekeeping gene)
    """
    df[f'delta_ct_{gene_col}'] = df[gene_col] - df[housekeeping_col]
    return df


def calculate_delta_delta_ct(df, gene_col, control_group, treatment_col):
    """
    Calculate ΔΔCt = ΔCt(sample) - mean ΔCt(control group)
    """
    delta_ct_col = f'delta_ct_{gene_col}'

    # Get mean ΔCt of the control/vehicle group
    control_mean = df[df[treatment_col] == control_group][delta_ct_col].mean()

    df[f'delta_delta_ct_{gene_col}'] = df[delta_ct_col] - control_mean
    return df


def calculate_fold_change(df, gene_col):
    """
    Fold change = 2^(-ΔΔCt)
    """
    df[f'fold_change_{gene_col}'] = 2 ** (-df[f'delta_delta_ct_{gene_col}'])
    return df


def run_pipeline(df, gene_cols, housekeeping_col, treatment_col, control_group):
    """
    Run the full qPCR analysis pipeline for a list of genes.
    """
    for gene in gene_cols:
        df = calculate_delta_ct(df, gene, housekeeping_col)
        df = calculate_delta_delta_ct(df, gene, control_group, treatment_col)
        df = calculate_fold_change(df, gene)

    return df
