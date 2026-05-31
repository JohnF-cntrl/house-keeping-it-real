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
results = run_pipeline(df, gene_cols, housekeeping_col, treatment_col, control_group)

# Print the results
print(results[['sample_id', 'treatment', 'litter_id', 
               'fold_change_il10_ct', 'fold_change_tnf_ct']].to_string())