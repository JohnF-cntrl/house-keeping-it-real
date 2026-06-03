import pandas as pd
import numpy as np
from statsmodels.formula.api import mixedlm


def run_lmm(df, gene_col, treatment_col, litter_col, control_group):
    """
    Run a Linear Mixed Model for in vivo data.
    Accounts for the litter effect by treating litter ID as a random effect.
    Fixed effect: treatment group (what we care about)
    Random effect: litter ID (what we want to account for)
    """
    fold_change_col = f'fold_change_{gene_col}'

    # Make sure control group is the reference level
    df[treatment_col] = pd.Categorical(
        df[treatment_col],
        categories=[control_group] +
        [t for t in df[treatment_col].unique() if t != control_group]
    )

    formula = f'{fold_change_col} ~ C({treatment_col})'
    model = mixedlm(formula, df, groups=df[litter_col])
    result = model.fit(reml=True)

    return result


def summarize_lmm(result, gene_col):
    """
    Extract a clean summary table from the LMM result.
    Returns summary dataframe, pct_litter, pct_residual.
    pct_litter and pct_residual will be None if variance cannot be estimated.
    """
    summary = pd.DataFrame({
        'Estimate': result.fe_params,
        'Std Error': result.bse_fe,
        'p-value': result.pvalues
    })

    summary = summary.round(4)

    # Safely compute variance explained by litter
    pct_litter = None
    pct_residual = None

    try:
        litter_variance = float(result.cov_re.values[0][0])
        residual_variance = float(result.scale)

        if (
            np.isnan(litter_variance) or
            np.isnan(residual_variance) or
            np.isinf(litter_variance) or
            np.isinf(residual_variance) or
            (litter_variance + residual_variance) == 0
        ):
            pct_litter = None
            pct_residual = None
        else:
            total_variance = litter_variance + residual_variance
            pct_litter = round((litter_variance / total_variance) * 100, 1)
            pct_residual = round((residual_variance / total_variance) * 100, 1)

    except Exception:
        pct_litter = None
        pct_residual = None

    print(f"\n--- LMM Results for {gene_col} ---")
    print(summary.to_string())
    print(f"\nVariance explained by litter: {pct_litter}%")
    print(f"Residual variance:            {pct_residual}%")

    return summary, pct_litter, pct_residual
