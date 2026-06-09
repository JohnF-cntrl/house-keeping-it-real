import streamlit as st
import pandas as pd
import json
from utils.supabase_client import restore_session, is_logged_in, get_current_user

restore_session()

# ── HANDLE SHARE LINKS ──
query_params = st.query_params
share_token = query_params.get("share", None)

if share_token:
    from utils.supabase_client import get_experiment_by_token
    from modules.qpcr import run_pipeline
    from modules.plots import plot_fold_changes

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
    page_icon="🏠",
    layout="wide"
)

# ── HERO SECTION ──
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("## 🧬 house-keeping-it-real")
    st.markdown(
        "### *A qRT-PCR analysis tool built for the St.A.B Lab, and beyond🚀!*")
    st.markdown("")
    st.markdown("")

    if is_logged_in():
        user = get_current_user()
        st.success(f"✅ Logged in as **{user.email}**")
        st.page_link("pages/📈Analysis.py", label="Go to Analysis", icon="🔬")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.page_link("pages/🔐_Login.py",
                         label="Log In / Sign Up", icon="🔐")
        with col_b:
            st.page_link("pages/📈Analysis.py",
                         label="Try without account", icon="🧬")

st.divider()

# ── FEATURES ──
st.markdown("### What it does")
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
**📊 Automated Analysis**

Enter raw Ct values and get
publication-ready fold change
plots and summary tables
instantly.
""")

with col2:
    st.info("""
**🐭 In Vivo Support**

Properly accounts for the
litter effect using Linear
Mixed Models.
""")

with col3:
    st.info("""
**💾 Save & Share**

Save experiments and share results
with collaborators.
""")

st.markdown("")
col4, col5, col6 = st.columns(3)

with col4:
    st.info("""
**🔬 Flexibility**

Works for any gene, any
treatment group, any
housekeeping gene —
fully flexible.
""")

with col5:
    st.info("""
**📱 Accessibility**

Access from any device,
any browser. No installation
required.
""")

with col6:
    st.info("""
**📖 Built-in Manual**

Full user manual available.
""")

st.divider()

# ── FOOTER ──
st.markdown("""
<div style='text-align: center; color: #999999; font-size: 13px; padding: 10px 0;'>
house-keeping-it-real | Developed by John Fayek | St.A.B Lab | ASSURE 2026<br>
<a href='https://github.com/JohnF-cntrl/house-keeping-it-real' target='_blank'>github.com/JohnF-cntrl/house-keeping-it-real</a>
</div>
""", unsafe_allow_html=True)
