import streamlit as st
from utils.supabase_client import restore_session, is_logged_in, get_current_user

restore_session()

st.set_page_config(
    page_title="house-keeping-it-real",
    page_icon="🏠",
    layout="wide"
)

# ── HERO SECTION ──
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("## 🧬 house-keeping-it-real")
    st.markdown("### *A qRT-PCR analysis tool built for the St.A.B Lab, and beyond🚀!*")
    st.markdown("")
    st.markdown("")

    if is_logged_in():
        user = get_current_user()
        st.success(f"✅ Logged in as **{user.email}**")
        st.page_link("pages/📈Analysis.py", label="Go to Analysis", icon="🔬")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.page_link("pages/🔐_Login.py", label="Log In / Sign Up", icon="🔐")
        with col_b:
            st.page_link("pages/📈Analysis.py", label="Try without account", icon="🧬")

with col2:
    st.markdown("")
    st.markdown("")
    st.info("""
**🔬 What you can do:**

- Enter raw Ct values manually or upload a file
- Auto-calculate ΔΔCt and fold changes
- Generate interactive publication-ready charts
- Run Linear Mixed Models for in vivo litter correction
- Save and share experiments with collaborators
- Access from any device, anywhere
""")

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
Mixed Models — something
Excel can't do.
""")

with col3:
    st.info("""
**💾 Save & Share**

Save experiments to your
account and share results
with collaborators via
a simple link.
""")

st.markdown("")
col4, col5, col6 = st.columns(3)

with col4:
    st.info("""
**🔬 Any Gene, Any Lab**

Works for any gene, any
treatment group, any
housekeeping gene —
fully flexible.
""")

with col5:
    st.info("""
**📱 Works Anywhere**

Access from any device,
any browser. No installation
required.
""")

with col6:
    st.info("""
**📖 Built-in Manual**

Full user manual included
in the app — explaining
every result in plain
scientific language.
""")

st.divider()

# ── FOOTER ──
st.markdown("""
<div style='text-align: center; color: #999999; font-size: 13px; padding: 10px 0;'>
house-keeping-it-real | Developed by John Wadie | St.A.B Lab | ASSURE 2026<br>
<a href='https://github.com/JohnF-cntrl/house-keeping-it-real' target='_blank'>github.com/JohnF-cntrl/house-keeping-it-real</a>
</div>
""", unsafe_allow_html=True)