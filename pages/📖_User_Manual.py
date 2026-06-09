import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="User Manual — house-keeping-it-real",
    page_icon="📖",
    layout="wide"
)

st.title("📖 User Manual")
st.markdown("*Everything you need to know to use house-keeping-it-real.*")
st.divider()

# ── TABLE OF CONTENTS ──
with st.expander("📋 Table of Contents", expanded=False):
    st.markdown("""
    1. [Overview](#overview)
    2. [Getting Started](#getting-started)
    3. [Manual Data Entry](#manual-data-entry)
    4. [File Upload](#file-upload)
    5. [Understanding Your Results](#understanding-your-results)
    6. [In Vivo Mode & The Litter Effect](#in-vivo-mode-the-litter-effect)
    7. [Tips for Good Results](#tips-for-good-results)
    8. [Glossary](#glossary)
    """)

st.divider()

# ── 1. OVERVIEW ──
st.header("1. Overview")
st.markdown("""
**house-keeping-it-real** is a web-based qRT-PCR analysis tool that automates the full 
data processing pipeline — from raw Ct values to publication-ready figures — without 
requiring any coding knowledge.

The tool supports two experiment types:
""")

col1, col2 = st.columns(2)
with col1:
    st.info("""
**🔬 In Vitro**

For cell culture experiments where all 
samples are independent of each other.

Uses standard **t-test** statistics.
""")
with col2:
    st.info("""
**🐭 In Vivo**

For developmental mouse studies where 
pups from the same litter are related.

Uses **Linear Mixed Models** to properly 
account for the litter effect.
""")

st.divider()

# ── 2. GETTING STARTED ──
st.header("2. Getting Started")
st.markdown("""
Open the tool in any web browser — no installation required. 
In the sidebar on the left you will find two settings to configure before entering data.
""")

st.subheader("Experiment Type")
st.markdown("""
- **In vitro (no grouping effect)** — select this for cell culture experiments
- **In vivo (account for grouping effect)** — select this for mouse embryo studies where pups come from litters
""")

st.subheader("Data Entry Method")
st.markdown("""
- **✏️ Enter values manually** — type Ct values directly into an interactive table in the browser. Recommended for most users.
- **📂 Upload a file** — upload a CSV, Excel, or TXT file. See Section 4 for the required format.
""")

st.divider()

# ── 3. MANUAL DATA ENTRY ──
st.header("3. Manual Data Entry (Recommended)")
st.markdown("Manual entry walks you through three steps:")

st.subheader("Step 1 — Experiment Setup")

setup_table = pd.DataFrame({
    "Field": [
        "Number of samples",
        "Treatment groups",
        "Control group name",
        "Genes of interest",
        "Housekeeping gene name"
    ],
    "What to Enter": [
        "Total number of samples across all treatment groups",
        "Names of your treatment groups, comma separated — e.g. BPA, E2, Vehicle",
        "Name of your control group. Must match exactly one of the treatment groups above.",
        "Names of the genes you measured, comma separated — e.g. CD22, ABL1, TNF",
        "Name of your housekeeping/reference gene — e.g. GAPDH, ACTB"
    ]
})
st.dataframe(setup_table, use_container_width=True, hide_index=True)

st.subheader("Step 2 — Enter Your Ct Values")
st.markdown("""
An interactive table will appear with one row per sample. Fill in:
- **Sample ID** — pre-filled automatically, can be edited
- **Treatment** — select from the dropdown which treatment group this sample belongs to
- **Litter ID** — *(in vivo mode only)* which litter this sample came from
- **Gene Ct columns** — enter the raw Ct value from the PCR machine for each gene
- **Housekeeping gene Ct** — enter the raw Ct value for your housekeeping gene
""")

st.warning("⚠️ Ct values should typically be between 15 and 40. Do not include samples with undetermined or failed amplification.")

st.subheader("Step 3 — Run Analysis")
st.markdown("""
Click **▶️ Run Analysis**. The tool will automatically:
1. Calculate ΔCt values (normalizing against the housekeeping gene)
2. Calculate ΔΔCt values (normalizing against the control group)
3. Convert to fold changes
4. Run the appropriate statistical test
5. Generate interactive charts and summary tables
""")

st.divider()

# ── 4. FILE UPLOAD ──
st.header("4. File Upload")
st.markdown("""
If you prefer to upload a file, it must follow this exact format. 
Supported file types: **CSV, Excel (.xlsx), TXT (tab-separated)**.
""")

example_df = pd.DataFrame({
    'sample_id':  ['S01', 'S02', 'S03', 'S04'],
    'litter_id':  ['L1', 'L1', 'L2', 'L2'],
    'treatment':  ['BPA', 'Vehicle', 'BPA', 'Vehicle'],
    'cd22_ct':    [28.3, 31.2, 27.8, 30.9],
    'gapdh_ct':   [20.2, 20.1, 20.3, 20.0],
})
st.dataframe(example_df, use_container_width=False, hide_index=True)

st.markdown("""
- **sample_id** — unique identifier for each sample
- **litter_id** — litter or grouping ID *(required for in vivo mode, can be omitted for in vitro)*
- **treatment** — treatment group name
- **gene_ct columns** — one column per gene with the `_ct` suffix (e.g. `cd22_ct`, `tnf_ct`)
- **housekeeping_ct** — housekeeping gene column also needs the `_ct` suffix (e.g. `gapdh_ct`)
""")

st.divider()

# ── 5. UNDERSTANDING RESULTS ──
st.header("5. Understanding Your Results")

st.subheader("5.1 The Analysis Pipeline")
st.markdown(
    "The tool performs these calculations automatically on your raw Ct values:")

col1, col2, col3 = st.columns(3)
with col1:
    st.success("""
**Step 1 — ΔCt**

ΔCt = Ct(gene) − Ct(housekeeping)

Removes variation caused by 
differences in RNA loading 
between samples.
""")
with col2:
    st.success("""
**Step 2 — ΔΔCt**

ΔΔCt = ΔCt(sample) − mean ΔCt(vehicle)

Makes all values relative 
to your vehicle/control group.
""")
with col3:
    st.success("""
**Step 3 — Fold Change**

Fold Change = 2^(−ΔΔCt)

Vehicle = 1.0

A value of 2.0 means twice 
the expression of vehicle.
""")

st.subheader("5.2 Fold Change Plot")
st.markdown("""
Each bar represents one treatment group. Key elements:

- **Bar height** — the mean fold change. Vehicle should always be close to 1.0.
- **Error bars** — the Standard Error of the Mean (SEM). Short bars = consistent replicates. Tall bars = high variability.
- **Dashed line at y=1** — the reference line representing the vehicle control level.
- **Significance brackets** — compare each treatment group to the vehicle control.
""")

st.subheader("5.3 Significance Markers")

sig_table = pd.DataFrame({
    "Marker": ["ns", "*", "**", "***"],
    "Meaning": ["Not significant", "Significant", "Very significant", "Highly significant"],
    "p-value threshold": ["p > 0.05", "p < 0.05", "p < 0.01", "p < 0.001"],
    "Interpretation": [
        "Cannot confidently conclude the treatment had an effect",
        "The effect is statistically significant",
        "Strong statistical evidence of an effect",
        "Very strong statistical evidence of an effect"
    ]
})
st.dataframe(sig_table, use_container_width=True, hide_index=True)

st.warning("""
⚠️ **Important:** Getting 'ns' does not mean there is no biological effect. 
It may simply mean you don't have enough replicates yet. 
Typically **N ≥ 5 per group** is needed to reliably detect significance.
""")

st.subheader("5.4 Summary Table (In Vitro)")
st.markdown("""
The summary table shows:
- **Treatment** — the treatment group name
- **Mean Fold Change** — average fold change across all replicates. Vehicle should be close to 1.0.
- **SEM** — Standard Error of the Mean. Smaller values mean more consistent replicates. Shows as N/A with only one replicate.
- **N** — number of replicates in that group.
""")

st.divider()

# ── 6. IN VIVO ──
st.header("6. In Vivo Mode & The Litter Effect")
st.markdown("""
When studying developmental mouse models, all pups from the same litter share the same 
mother, womb environment, and chemical exposure. This means pups from the same litter 
are **not statistically independent** — they are more similar to each other than to pups 
from a different litter.

If this is ignored and all pups are treated as independent samples, the statistics become 
overconfident and can produce **false positives**. This is called the **litter effect**.
""")

st.subheader("6.1 Linear Mixed Model (LMM)")
st.markdown("""
In vivo mode uses a **Linear Mixed Model** which accounts for the litter effect before 
drawing conclusions about treatment. It splits variation in your data into two parts:

- **Litter variance** — how much variation is simply due to pups coming from different litters (biological noise)
- **Residual variance** — everything else, including the actual treatment effect

The treatment effect is only evaluated *after* accounting for litter, giving a more 
honest and statistically rigorous result.
""")

st.subheader("6.2 Reading the LMM Results Tab")
st.markdown("""
**Fixed Effects Table:**
- **Estimate** — the size of the treatment effect after accounting for litter. Larger = bigger effect.
- **Std Error** — uncertainty around the estimate. Small Std Error relative to Estimate = confident result.
- **p-value** — probability the result is due to chance. Below 0.05 = statistically significant.

**Variance Pie Chart:**
Shows what percentage of variation is explained by the litter effect vs residual variation. 
A large red slice means the litter effect was dominant and correcting for it was important.
""")

st.info("💡 The LMM requires at least 3 litters per treatment group to produce reliable results.")

st.divider()

# ── 7. TIPS ──
st.header("7. Tips for Good Results")

tips = [
    "Always include at least **3 biological replicates** per treatment group. More replicates = more statistical power.",
    "For in vivo experiments, aim for **4-5 litters per treatment group** for reliable LMM estimates.",
    "Make sure your housekeeping gene Ct values are **consistent across samples** (within ~1 cycle). Large variation suggests poor RNA quality.",
    "Ct values **above 35** may indicate poor amplification and should be interpreted cautiously.",
    "The **vehicle/control group fold change should always be close to 1.0**. If it's not, check your data entry.",
    "'ns' (not significant) does not mean no effect — it may simply mean **more replicates are needed**.",
    "Use the **Download results as CSV** button to save your summary table for further analysis or record keeping.",
]

for tip in tips:
    st.markdown(f"✅ {tip}")

st.divider()

# ── 8. GLOSSARY ──
st.header("8. Glossary")

glossary = pd.DataFrame({
    "Term": [
        "Ct / Cq value",
        "Housekeeping gene",
        "ΔCt (Delta Ct)",
        "ΔΔCt (Delta Delta Ct)",
        "Fold Change",
        "SEM",
        "p-value",
        "ns",
        "t-test",
        "LMM",
        "Litter effect",
        "N",
        "Biological replicate",
    ],
    "Definition": [
        "Cycle threshold — the PCR cycle at which fluorescence crosses a threshold. Lower Ct = more starting RNA.",
        "A reference gene stably expressed regardless of treatment (e.g. GAPDH, ACTB). Used to normalize for RNA loading differences.",
        "Ct(gene of interest) minus Ct(housekeeping gene). Normalizes for RNA loading differences between samples.",
        "ΔCt(sample) minus mean ΔCt(control group). Makes all values relative to the control.",
        "2^(−ΔΔCt). Vehicle = 1.0. A value of 2.0 means twice the expression. A value of 0.5 means half the expression.",
        "Standard Error of the Mean. Measures variability between replicates. Shown as error bars on the chart.",
        "The probability that a result occurred by chance. Below 0.05 is considered statistically significant.",
        "Not significant. The p-value was above 0.05.",
        "Statistical test used in vitro to compare two groups.",
        "Linear Mixed Model. Statistical test used in vivo that accounts for the litter effect.",
        "The statistical non-independence of pups from the same litter due to shared maternal environment and chemical exposure.",
        "Number of biological replicates in a group.",
        "An independent biological sample. Different from a technical replicate (running the same sample twice).",
    ]
})
st.dataframe(glossary, use_container_width=True, hide_index=True)

st.divider()

# ── FOOTER ──
st.markdown("""
<div style='text-align: center; color: #999999; font-size: 13px; padding: 20px 0;'>
house-keeping-it-real | Developed by John Fayek | St.A.B Lab | ASSURE 2026<br>
<a href='https://github.com/JohnF-cntrl/house-keeping-it-real' target='_blank'>github.com/JohnF-cntrl/house-keeping-it-real</a>
</div>
""", unsafe_allow_html=True)
