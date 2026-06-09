import streamlit as st
from supabase import create_client, Client

def restore_session():
    """Restore session from session state if available."""
    if "session" in st.session_state and st.session_state["session"]:
        try:
            supabase = get_supabase()
            session = st.session_state["session"]
            supabase.auth.set_session(
                session.access_token,
                session.refresh_token
            )
            # Refresh user
            user = supabase.auth.get_user()
            if user:
                st.session_state["user"] = user.user
        except Exception:
            st.session_state.pop("user", None)
            st.session_state.pop("session", None)

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_current_user():
    """Get the currently logged in user from session state."""
    return st.session_state.get("user", None)


def is_logged_in():
    """Check if a user is currently logged in."""
    return st.session_state.get("user") is not None


def login(email: str, password: str):
    """Log in with email and password. Returns (success, message)."""
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state["user"] = response.user
        st.session_state["session"] = response.session
        return True, "Logged in successfully!"
    except Exception as e:
        return False, str(e)


def signup(email: str, password: str):
    """Sign up with email and password. Returns (success, message)."""
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return True, "Account created! Please check your email to confirm your account, then log in."
        return False, "Signup failed. Please try again."
    except Exception as e:
        return False, str(e)


def logout():
    """Log out the current user."""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("session", None)


def save_experiment(name: str, experiment_type: str, treatment_groups: list,
                    control_group: str, genes: list, housekeeping_gene: str,
                    results_json: str, is_public: bool = False):
    """Save an experiment to the database. Returns (success, experiment_id)."""
    try:
        import secrets as secrets_lib
        supabase = get_supabase()
        user = get_current_user()
        if not user:
            return False, "Not logged in"

        share_token = secrets_lib.token_urlsafe(16) if is_public else None

        data = {
            "user_id": user.id,
            "name": name,
            "experiment_type": experiment_type,
            "treatment_groups": ",".join(treatment_groups),
            "control_group": control_group,
            "genes": ",".join(genes),
            "housekeeping_gene": housekeeping_gene,
            "results_json": results_json,
            "is_public": is_public,
            "share_token": share_token
        }

        response = supabase.table("experiments").insert(data).execute()
        if response.data:
            return True, response.data[0]["id"], share_token
        return False, "Save failed", None
    except Exception as e:
        return False, str(e), None


def get_my_experiments():
    """Get all experiments for the current user."""
    try:
        supabase = get_supabase()
        user = get_current_user()
        if not user:
            return []
        response = supabase.table("experiments")\
            .select("*")\
            .eq("user_id", user.id)\
            .order("created_at", desc=True)\
            .execute()
        return response.data or []
    except Exception:
        return []


def get_experiment_by_token(token: str):
    """Get a public experiment by its share token."""
    try:
        supabase = get_supabase()
        response = supabase.table("experiments")\
            .select("*")\
            .eq("share_token", token)\
            .eq("is_public", True)\
            .execute()
        if response.data:
            return response.data[0]
        return None
    except Exception:
        return None


def delete_experiment(experiment_id: str):
    """Delete an experiment by ID."""
    try:
        supabase = get_supabase()
        supabase.table("experiments")\
            .delete()\
            .eq("id", experiment_id)\
            .execute()
        return True
    except Exception:
        return False