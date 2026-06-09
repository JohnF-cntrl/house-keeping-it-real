import streamlit as st
import pandas as pd
import json
from utils.supabase_client import is_logged_in, get_current_user, get_my_experiments, delete_experiment

st.set_page_config(
    page_title="My Experiments — house-keeping-it-real",
    page_icon="📊",
    layout="wide"
)

st.title("📊 My Experiments")
st.markdown("*Your saved experiment history.*")
st.divider()

# ── NOT LOGGED IN ──
if not is_logged_in():
    st.warning("Please log in to view your saved experiments.")
    st.page_link("pages/🔐_Login.py", label="Go to Login", icon="🔐")
    st.stop()

# ── LOGGED IN ──
user = get_current_user()
st.markdown(f"Logged in as **{user.email}**")
st.divider()

experiments = get_my_experiments()

if not experiments:
    st.info("You haven't saved any experiments yet. Run an analysis and click **Save Experiment** to get started!")
else:
    st.markdown(f"### {len(experiments)} saved experiment{'s' if len(experiments) != 1 else ''}")
    spacer = st.empty()

    for exp in experiments:
        with st.expander(f"🧬 {exp['name']} — {exp['created_at'][:10]}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Experiment type:** {exp['experiment_type']}")
                st.markdown(f"**Genes:** {exp['genes']}")
                st.markdown(f"**Treatment groups:** {exp['treatment_groups']}")
                st.markdown(f"**Control group:** {exp['control_group']}")
                st.markdown(f"**Housekeeping gene:** {exp['housekeeping_gene']}")

                # Show share link if public
                if exp['is_public'] and exp['share_token']:
                    share_url = f"https://house-keeping-it-real.streamlit.app/?share={exp['share_token']}"
                    st.markdown(f"**Share link:** [{share_url}]({share_url})")

            with col2:
                # Download results as CSV
                try:
                    results_data = json.loads(exp['results_json'])
                    results_df = pd.DataFrame(results_data)
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"{exp['name'].replace(' ', '_')}_results.csv",
                        mime='text/csv',
                        key=f"download_{exp['id']}"
                    )
                except Exception:
                    pass

                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{exp['id']}"):
                    if delete_experiment(exp['id']):
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Could not delete. Please try again.")