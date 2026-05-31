from modules.plots import plot_fold_changes, plot_litter_variance
from modules.lmm import run_lmm, summarize_lmm
import pandas as pd
from modules.qpcr import run_pipeline

# Load sample data
df = pd.read_csv('data/sample_data.csv')

# Define our genes, housekeeping gene, treatment column and control group
gene_cols = ['il10_ct', 'tnf_ct']
housekeeping_col = 'gapdh_ct'
treatment_col = 'treatment'
control_group = 'Vehicle'

# Run the pipeline
results = run_pipeline(df, gene_cols, housekeeping_col,
                       treatment_col, control_group)

# Print the results
print(results[['sample_id', 'treatment', 'litter_id',
               'fold_change_il10_ct', 'fold_change_tnf_ct']].to_string())


# Test LMM on il10
result = run_lmm(results, 'il10_ct', 'treatment', 'litter_id', 'Vehicle')
summarize_lmm(result, 'il10_ct')


# Plot fold changes
plot_fold_changes(results, 'il10_ct', 'treatment')

# Plot litter variance from LMM
_, pct_litter, pct_residual = summarize_lmm(result, 'il10_ct')
plot_litter_variance(pct_litter, pct_residual, 'il10_ct')
