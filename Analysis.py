import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
from modules.qpcr import run_pipeline
from modules.lmm import run_lmm, summarize_lmm
from modules.plots import plot_fold_changes, plot_litter_variance
from utils.supabase_client import is_logged_in, save_experiment, restore_session

# ── RESTORE SESSION ──
restore_session()

# ── HANDLE SHARE LINKS ──
query_params = st.query_params
share_token = query_params.get("share", None)

if share_token:
    from utils.supabase_client import get_experiment_by_token
    exp = get_experiment_by_token(share_token)
    if exp:
        st.set_page_config(
            page_title=f"{exp['name']} — house-keeping-it-real", page_icon="🧬", layout="wide")
        st.title(f"🧬 {exp['name']}")
        st.markdown(f"*Shared experiment — {exp['created_at'][:10]}*")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Experiment type:** {exp['experiment_type']}")
            st.markdown(
                f"**Genes:** {', '.join([g.replace('_ct','').upper() for g in exp['genes'].split(',')])}")
            st.markdown(f"**Treatment groups:** {exp['treatment_groups']}")
        with col2:
            st.markdown(f"**Control group:** {exp['control_group']}")
            st.markdown(
                f"**Housekeeping gene:** {exp['housekeeping_gene'].replace('_ct','').upper()}")

        st.divider()

        gene_cols_shared = exp['genes'].split(',')
        housekeeping_col_shared = exp['housekeeping_gene']
        treatment_col_shared = 'treatment'
        control_group_shared = exp['control_group']

        if exp.get('raw_data_json'):
            raw_df = pd.DataFrame(json.loads(exp['raw_data_json']))
            for col in gene_cols_shared + [housekeeping_col_shared]:
                if col in raw_df.columns:
                    raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')

            shared_results = run_pipeline(
                raw_df, gene_cols_shared, housekeeping_col_shared,
                treatment_col_shared, control_group_shared
            )

            for gene in gene_cols_shared:
                gene_display = gene.replace('_ct', '').upper()
                st.subheader(f"📊 {gene_display}")
                plot_fig = plot_fold_changes(
                    shared_results, gene, treatment_col_shared)
                st.plotly_chart(
                    plot_fig, use_container_width=False, key=f"share_plot_{gene}")

                fold_col = f'fold_change_{gene}'
                summary_table = shared_results.groupby(treatment_col_shared)[fold_col].agg(
                    ['mean', 'sem', 'count']
                ).reset_index()
                summary_table.columns = ['Treatment',
                                         'Mean Fold Change', 'SEM', 'N']
                summary_table = summary_table.round(4)
                summary_table['SEM'] = summary_table['SEM'].fillna('N/A')
                st.dataframe(
                    summary_table, use_container_width=False, hide_index=True)
                st.divider()
        else:
            results_data = json.loads(exp['results_json'])
            results_df = pd.DataFrame(results_data)
            genes = results_df['Gene'].unique()
            for gene in genes:
                st.subheader(f"📊 {gene}")
                gene_df = results_df[results_df['Gene'] == gene][[
                    'Treatment', 'Mean Fold Change', 'SEM', 'N']]
                st.dataframe(gene_df, use_container_width=False,
                             hide_index=True)
                st.divider()

        csv_data = pd.DataFrame(json.loads(exp['results_json']))
        csv = csv_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download results as CSV",
            data=csv,
            file_name=f"{exp['name'].replace(' ','_')}_results.csv",
            mime='text/csv'
        )
        st.stop()
    else:
        st.set_page_config(page_title="house-keeping-it-real",
                           page_icon="🧬", layout="wide")
        st.error("This shared experiment could not be found or is no longer public.")
        st.stop()

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="house-keeping-it-real",
    page_icon="🧬",
    layout="wide"
)

# ── HEADER ──
st.title("🧬 house-keeping-it-real")
st.markdown("*A qRT-PCR analysis tool built for any lab, any experiment.*")
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

    input_method = st.radio(
        "How would you like to enter your data?",
        ["✏️ Enter values manually", "📂 Upload a file"],
        help="Manual entry lets you type values directly. Upload supports CSV, Excel, and TXT files."
    )

    st.divider()

    if is_logged_in():
        from utils.supabase_client import get_current_user, logout
        user = get_current_user()
        st.success(f"✅ {user.email}")
        if st.button("Log out", type="secondary"):
            logout()
            st.rerun()
    else:
        st.info("💡 Log in to save & share experiments.")
        st.page_link("pages/🔐_Login.py", label="Log In / Sign Up", icon="🔐")


# ── HELPER: Summary Table ──
def render_summary_table(results, treatment_col, gene, gene_display):
    fold_col = f'fold_change_{gene}'
    summary_table = results.groupby(treatment_col)[fold_col].agg(
        ['mean', 'sem', 'count']
    ).reset_index()
    summary_table.columns = ['Treatment', 'Mean Fold Change', 'SEM', 'N']
    summary_table = summary_table.round(4)
    summary_table['SEM'] = summary_table['SEM'].fillna('N/A')
    st.dataframe(summary_table, use_container_width=False, hide_index=True)
    csv = summary_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download results as CSV",
        data=csv,
        file_name=f'{gene_display}_results.csv',
        mime='text/csv',
        key=f"download_csv_{gene}"
    )


# ── HELPER: Run Analysis ──
def run_analysis(df, gene_cols, housekeeping_col, treatment_col, control_group, litter_col=None):
    ct_cols = gene_cols + [housekeeping_col]
    for col in ct_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    results = run_pipeline(df, gene_cols, housekeeping_col,
                           treatment_col, control_group)

    st.session_state["analysis_done"] = True
    st.session_state["last_df"] = df.copy()
    st.session_state["last_results"] = results.copy()
    st.session_state["last_gene_cols"] = gene_cols
    st.session_state["last_housekeeping_col"] = housekeeping_col
    st.session_state["last_treatment_col"] = treatment_col
    st.session_state["last_control_group"] = control_group
    st.session_state["last_experiment_type"] = experiment_type

    return results


# ── HELPER: Display Results ──
def display_results(results, gene_cols, treatment_col, control_group, df):
    st.subheader("📊 Results")

    for gene in gene_cols:
        gene_display = gene.replace('_ct', '').upper()
        st.markdown(f"### {gene_display}")

        lmm_pvalues = None
        pct_litter = None
        pct_residual = None
        summary = None

        if "In vivo" in experiment_type and st.session_state.get("last_litter_col"):
            litter_col = st.session_state["last_litter_col"]
            try:
                lmm_result = run_lmm(
                    results, gene, treatment_col, litter_col, control_group)
                summary, pct_litter, pct_residual = summarize_lmm(
                    lmm_result, gene)
                lmm_pvalues = {}
                for idx in summary.index:
                    for group in df[treatment_col].unique():
                        if group != control_group and group in str(idx):
                            lmm_pvalues[group] = summary.loc[idx, 'p-value']
            except Exception as e:
                st.warning(
                    f"LMM could not be fitted for {gene_display}: {str(e)}")

        plot_fig = plot_fold_changes(
            results, gene, treatment_col, lmm_pvalues=lmm_pvalues)

        tab_labels = ["Fold Change Plot", "LMM Results (in vivo)"] \
            if "In vivo" in experiment_type \
            else ["Fold Change Plot", "Summary Table"]

        tab1, tab2 = st.tabs(tab_labels)

        with tab1:
            st.plotly_chart(plot_fig, use_container_width=False,
                            key=f"plot_{gene}")

        with tab2:
            if "In vivo" in experiment_type:
                if summary is not None:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Fixed Effects (Treatment)**")
                        st.dataframe(summary, use_container_width=True)
                    with col_b:
                        variance_ok = (
                            pct_litter is not None and
                            pct_residual is not None and
                            not (isinstance(pct_litter, float) and np.isnan(pct_litter)) and
                            not (isinstance(pct_residual, float)
                                 and np.isnan(pct_residual))
                        )
                        if variance_ok:
                            variance_fig = plot_litter_variance(
                                pct_litter, pct_residual, gene)
                            st.plotly_chart(
                                variance_fig, use_container_width=False, key=f"variance_{gene}")
                        else:
                            st.info(
                                "Not enough data to estimate litter variance. Add more litters.")
                else:
                    st.warning(
                        "LMM results unavailable — check that you have enough litters and samples.")
            else:
                render_summary_table(
                    results, treatment_col, gene, gene_display)

    st.divider()
    st.success("✅ Analysis complete!")


# ── HELPER: Save Form ──
def show_save_form(results, gene_cols, treatment_col, control_group, housekeeping_col, df):
    st.subheader("💾 Save This Experiment")

    if is_logged_in():
        exp_name = st.text_input(
            "Experiment name", placeholder="e.g. BPA CD22 June 2025", key="exp_name_input")
        is_public = st.checkbox(
            "Make this experiment publicly shareable", key="is_public_input")

        if st.button("Save Experiment", type="primary", key="save_btn"):
            if not exp_name:
                st.error("Please enter a name for this experiment.")
            else:
                try:
                    summary_data = []
                    for gene in gene_cols:
                        fold_col = f'fold_change_{gene}'
                        gene_summary = results.groupby(treatment_col)[fold_col].agg(
                            ['mean', 'sem', 'count']
                        ).reset_index()
                        gene_summary.columns = [
                            'Treatment', 'Mean Fold Change', 'SEM', 'N']
                        gene_summary['Gene'] = gene.replace('_ct', '').upper()
                        summary_data.append(gene_summary)

                    all_results = pd.concat(summary_data).round(4)
                    results_json = all_results.fillna(
                        'N/A').to_json(orient='records')
                    raw_data_json = df.to_json(orient='records')

                    with st.spinner("Saving..."):
                        success, exp_id, share_token = save_experiment(
                            name=exp_name,
                            experiment_type=st.session_state.get(
                                "last_experiment_type", experiment_type),
                            treatment_groups=list(df[treatment_col].unique()),
                            control_group=control_group,
                            genes=gene_cols,
                            housekeeping_gene=housekeeping_col,
                            results_json=results_json,
                            raw_data_json=raw_data_json,
                            is_public=is_public
                        )

                    if success:
                        st.success(
                            "✅ Experiment saved! View it in My Experiments.")
                        if is_public and share_token:
                            share_url = f"https://house-keeping-it-real.streamlit.app/?share={share_token}"
                            st.markdown(f"**Share link:** {share_url}")
                    else:
                        st.error(f"Could not save: {exp_id}")
                except Exception as e:
                    st.error(f"Error saving: {str(e)}")
    else:
        st.info("💡 Log in to save and share your experiments.")
        st.page_link("pages/🔐_Login.py", label="Log In / Sign Up", icon="🔐")


# ════════════════════════════════════════
# ── MANUAL ENTRY MODE ──
# ════════════════════════════════════════
if "manually" in input_method:

    st.subheader("✏️ Manual Data Entry")
    st.markdown("Configure your experiment below, then fill in your Ct values.")
    st.divider()

    with st.expander("Step 1 — Experiment Setup", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            n_samples = st.number_input(
                "Number of samples", min_value=1, max_value=500, value=9, step=1)
            treatment_groups_input = st.text_input(
                "Treatment groups (comma separated)", value="BPA, E2, Vehicle")
            control_group_manual = st.text_input(
                "Control group name (must match one above exactly)", value="Vehicle")
        with col2:
            genes_input = st.text_input(
                "Genes of interest (comma separated)", value="IL10, TNF")
            housekeeping_manual = st.text_input(
                "Housekeeping gene name", value="GAPDH")

    treatment_groups = [t.strip()
                        for t in treatment_groups_input.split(',') if t.strip()]
    gene_names = [g.strip() for g in genes_input.split(',') if g.strip()]
    all_gene_names = gene_names + [housekeeping_manual]
    gene_cols_manual = [f"{g.lower()}_ct" for g in gene_names]
    housekeeping_col_manual = f"{housekeeping_manual.lower()}_ct"

    with st.expander("Step 2 — Enter Your Ct Values", expanded=True):
        st.markdown("Fill in the table below. Click any cell to edit it.")
        template_data = {
            'sample_id': [f'S{str(i+1).zfill(2)}' for i in range(n_samples)],
            'treatment': [treatment_groups[i % len(treatment_groups)] for i in range(n_samples)],
        }
        if "In vivo" in experiment_type:
            template_data['litter_id'] = [
                f'L{(i // 3) + 1}' for i in range(n_samples)]
        for gene in all_gene_names:
            template_data[f"{gene.lower()}_ct"] = [None] * n_samples
        template_df = pd.DataFrame(template_data)

        edited_df = st.data_editor(
            template_df,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                'sample_id': st.column_config.TextColumn('Sample ID'),
                'treatment': st.column_config.SelectboxColumn('Treatment', options=treatment_groups),
                **({'litter_id': st.column_config.TextColumn('Litter ID')} if "In vivo" in experiment_type else {}),
                **{f"{gene.lower()}_ct": st.column_config.NumberColumn(f"{gene} Ct", min_value=0.0, max_value=50.0, step=0.01, format="%.2f") for gene in all_gene_names}
            },
            hide_index=True
        )

    st.divider()
    if st.button("▶️ Run Analysis", type="primary"):
        ct_cols = [f"{g.lower()}_ct" for g in all_gene_names]
        if edited_df[ct_cols].isnull().any().any():
            st.error("⚠️ Please fill in all Ct values before running the analysis.")
        elif control_group_manual not in treatment_groups:
            st.error(
                f"⚠️ Control group '{control_group_manual}' doesn't match any treatment group.")
        else:
            litter_col_manual = 'litter_id' if "In vivo" in experiment_type else None
            st.session_state["last_litter_col"] = litter_col_manual
            with st.spinner("Running analysis..."):
                run_analysis(edited_df, gene_cols_manual, housekeeping_col_manual,
                             'treatment', control_group_manual, litter_col_manual)


# ════════════════════════════════════════
# ── FILE UPLOAD MODE ──
# ════════════════════════════════════════
else:
    st.subheader("📂 Upload Your Data")
    uploaded_file = st.file_uploader("Upload CSV, Excel, or TXT file", type=[
                                     "csv", "xlsx", "xls", "txt"])

    if uploaded_file is None:
        st.info("👆 Upload your file above to get started.")
        example = pd.DataFrame({
            'sample_id': ['S01', 'S02', 'S03'], 'litter_id': ['L1', 'L1', 'L2'],
            'treatment': ['BPA', 'Vehicle', 'E2'], 'il10_ct': [28.3, 31.2, 27.1],
            'tnf_ct': [30.1, 33.0, 28.9], 'gapdh_ct': [20.2, 20.1, 20.2],
        })
        st.dataframe(example, use_container_width=True)
    else:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.txt'):
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ Loaded {len(df)} samples successfully!")
        with st.expander("Preview raw data"):
            st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("🔧 Configure Analysis")
        col1, col2, col3 = st.columns(3)
        all_cols = df.columns.tolist()

        with col1:
            treatment_col = st.selectbox("Treatment column", all_cols, index=all_cols.index(
                'treatment') if 'treatment' in all_cols else 0)
            control_group = st.selectbox(
                "Control group", df[treatment_col].unique().tolist())
        with col2:
            housekeeping_col = st.selectbox("Housekeeping gene column", all_cols, index=all_cols.index(
                'gapdh_ct') if 'gapdh_ct' in all_cols else 0)
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
        if st.button("▶️ Run Analysis", type="primary"):
            if not gene_cols:
                st.error("Please select at least one gene of interest.")
            else:
                litter_col_upload = litter_col if "In vivo" in experiment_type else None
                st.session_state["last_litter_col"] = litter_col_upload
                with st.spinner("Running analysis..."):
                    run_analysis(df, gene_cols, housekeeping_col,
                                 treatment_col, control_group, litter_col_upload)


# ════════════════════════════════════════
# ── SHOW RESULTS FROM SESSION STATE ──
# ════════════════════════════════════════
if st.session_state.get("analysis_done"):
    results = st.session_state["last_results"]
    gene_cols = st.session_state["last_gene_cols"]
    treatment_col = st.session_state["last_treatment_col"]
    control_group = st.session_state["last_control_group"]
    housekeeping_col = st.session_state["last_housekeeping_col"]
    df = st.session_state["last_df"]

    display_results(results, gene_cols, treatment_col, control_group, df)
    show_save_form(results, gene_cols, treatment_col,
                   control_group, housekeeping_col, df)
