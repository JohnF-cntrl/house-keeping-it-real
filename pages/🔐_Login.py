import streamlit as st
from utils.supabase_client import login, signup, logout, is_logged_in, get_current_user, restore_session

restore_session()

st.set_page_config(
    page_title="Login — house-keeping-it-real",
    page_icon="🔐",
    layout="centered"
)

# ── ALREADY LOGGED IN ──
if is_logged_in():
    user = get_current_user()
    st.success(f"✅ You're logged in as **{user.email}**")
    st.markdown("You can now save experiments from the analysis page.")
    if st.button("Log out", type="secondary"):
        logout()
        st.rerun()
    st.page_link("pages/🧬_Analysis.py", label="Go to Analysis", icon="🔬")

else:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("## 🔐 Login")
        st.markdown("*Sign in to save and share your experiments.*")
        st.divider()

        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            st.markdown("### Welcome back!")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button(
                    "Log In", type="primary", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    with st.spinner("Logging in..."):
                        success, message = login(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Login failed: {message}")

        with tab2:
            st.markdown("### Create an account")
            st.markdown("Free — no credit card required.")
            with st.form("signup_form"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input(
                    "Confirm password", type="password")
                submit_signup = st.form_submit_button(
                    "Create Account", type="primary", use_container_width=True)

            if submit_signup:
                if not new_email or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        success, message = signup(new_email, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(f"Signup failed: {message}")

    with col2:
        st.markdown("### Why create an account?")
        st.markdown("")
        st.success("💾 **Save experiments** — never lose your results")
        st.success("🔗 **Share results** — send a link to collaborators")
        st.success("📊 **View history** — access all past experiments")
        st.success("🆓 **Completely free** — no credit card required")
