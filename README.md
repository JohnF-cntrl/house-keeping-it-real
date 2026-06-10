# 🧬 house-keeping-it-real

A web-based qRT-PCR data analysis tool built for the St.A.B lab 
at Liberty University. Automates the full analysis pipeline from raw 
Ct values to publication-ready figures, with proper statistical 
handling of the litter effect.

## What it does
- Normalizes raw Ct values against housekeeping genes
- Calculates ΔΔCt and fold changes automatically
- Runs standard statistics (t-test, ANOVA) for in vitro data
- Runs Linear Mixed Models for in vivo data to account for the litter effect
- Generates publication-ready plots and exports
- Tracks litter/colony metadata linked to PCR results

## Built with
- Python
- Streamlit
- pandas, scipy, statsmodels, matplotlib, seaborn

## About
Built as part of the ASSURE Summer Research Program, Summer 2026.
