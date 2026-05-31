import streamlit as st
import pandas as pd
from modules.qpcr import run_pipeline
from modules.lmm import run_lmm, summarize_lmm
from modules.plots import plot_fold_changes, plot_litter_variance

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="house-keeping-it-real",
    page_icon="🧬",
    layout="wide"
)

# ── HEADER ──
st.title("🧬 house-keeping-it-real")
st.markdown("*A qRT-PCR analysis tool for Dr. Stevenson's lab — and beyond.*")
st.divider()

# ── SIDEBAR ──
with st.sidebar:
    st.header("⚙️ Experiment Settings")

    experiment_type = st.radio(
        "Experiment type",
        ["In vitro (no grouping effect)",
         "In vivo (account for grouping effect)"],
        help="In vivo mode uses a Linear Mixed Model to account for litter or other grouping effects."
    )

    st.divider()
    st.markdown("**Upload your data**")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# ── MAIN AREA ──
if uploaded_file is None:
    st.info("👈 Upload your CSV file in the sidebar to get started.")

    st.markdown("### Expected CSV format")
    st.markdown("Your CSV should have the following columns:")
    example = pd.DataFrame({
        'sample_id':  ['S01', 'S02', 'S03'],
        'mouse_id':   ['M01', 'M02', 'M03'],
        'litter_id':  ['L1', 'L1', 'L2'],
        'treatment':  ['BPA', 'Vehicle', 'E2'],
        'gene1_ct':   [28.3, 31.2, 27.1],
        'gapdh_ct':   [20.2, 20.1, 20.2],
    })
    st.dataframe(example, use_container_width=True)
    st.markdown("""
    - **sample_id** — unique identifier for each sample
    - **litter_id** — litter or grouping ID *(required for in vivo mode)*
    - **treatment** — treatment group name (e.g. BPA, E2, Vehicle)
    - **gene_ct columns** — one column per gene including your housekeeping gene
    """)

else:
    # Load data
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded {len(df)} samples successfully!")

    with st.expander("Preview raw data"):
        st.dataframe(df, use_container_width=True)

    st.divider()

    # ── COLUMN SELECTION ──
    st.subheader("🔧 Configure Analysis")
    col1, col2, col3 = st.columns(3)

    all_cols = df.columns.tolist()

    with col1:
        treatment_col = st.selectbox(
            "Treatment column",
            all_cols,
            index=all_cols.index('treatment') if 'treatment' in all_cols else 0
        )
        control_group = st.selectbox(
            "Control group", df[treatment_col].unique().tolist())

    with col2:
        housekeeping_col = st.selectbox(
            "Housekeeping gene column",
            all_cols,
            index=all_cols.index('gapdh_ct') if 'gapdh_ct' in all_cols else 0
        )
        gene_options = [c for c in all_cols if c.endswith(
            '_ct') and c != housekeeping_col]
        gene_cols = st.multiselect(
            "Genes of interest", gene_options, default=gene_options)

    with col3:
        if "In vivo" in experiment_type:
            litter_col_options = [
                c for c in all_cols if 'litter' in c or 'group' in c or 'id' in c.lower()]
            litter_col = st.selectbox(
                "Grouping variable column", litter_col_options)

    st.divider()

    # ── RUN ANALYSIS ──
    if st.button("▶️ Run Analysis", type="primary"):
        if not gene_cols:
            st.error("Please select at least one gene of interest.")
        else:
            with st.spinner("Running analysis..."):

                # Run qPCR pipeline
                results = run_pipeline(
                    df, gene_cols, housekeeping_col, treatment_col, control_group)

                st.subheader("📊 Results")

                for gene in gene_cols:
                    gene_display = gene.replace('_ct', '').upper()
                    st.markdown(f"### {gene_display}")

                    # Run LMM first if in vivo so we have p-values for the plot
                    lmm_pvalues = None
                    lmm_result = None
                    pct_litter = None
                    pct_residual = None
                    summary = None

                    if "In vivo" in experiment_type:
                        lmm_result = run_lmm(
                            results, gene, treatment_col, litter_col, control_group)
                        summary, pct_litter, pct_residual = summarize_lmm(
                            lmm_result, gene)

                        # Extract LMM p-values for each treatment group
                        lmm_pvalues = {}
                        for idx in summary.index:
                            for group in df[treatment_col].unique():
                                if group != control_group and group in str(idx):
                                    lmm_pvalues[group] = summary.loc[idx,
                                                                     'p-value']

                    # Generate fold change plot with correct p-values
                    plot_path = plot_fold_changes(
                        results, gene, treatment_col, lmm_pvalues=lmm_pvalues
                    )

                    tab_labels = ["Fold Change Plot", "LMM Results (in vivo)"] \
                        if "In vivo" in experiment_type \
                        else ["Fold Change Plot", "Summary Table"]

                    tab1, tab2 = st.tabs(tab_labels)

                    with tab1:
                        st.image(plot_path, use_container_width=False)

                    with tab2:
                        if "In vivo" in experiment_type:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown("**Fixed Effects (Treatment)**")
                                st.dataframe(summary, use_container_width=True)
                            with col_b:
                                variance_path = plot_litter_variance(
                                    pct_litter, pct_residual, gene)
                                st.image(variance_path,
                                         use_container_width=False)
                        else:
                            fold_col = f'fold_change_{gene}'
                            summary_table = results.groupby(treatment_col)[fold_col].agg(
                                ['mean', 'sem', 'count']
                            ).reset_index()
                            summary_table.columns = [
                                'Treatment', 'Mean Fold Change', 'SEM', 'N']
                            summary_table = summary_table.round(4)

                            # CSV download
                            csv = summary_table.to_csv(
                                index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Download results as CSV",
                                data=csv,
                                file_name=f'{gene_display}_results.csv',
                                mime='text/csv'
                            )
                            st.dataframe(
                                summary_table, use_container_width=True)

                st.divider()
                st.success(
                    "✅ Analysis complete! Check the outputs/ folder for saved figures.")
