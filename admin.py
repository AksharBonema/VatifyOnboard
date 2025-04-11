# admin.py

import streamlit as st
from supabase import Client

def render_admin_dashboard(supabase: Client):
    """
    Displays an admin dashboard with a list of users and their onboarding status.
    """
    st.title("VATIFY: Admin Dashboard")

    # Example: List all users in user_onboarding
    user_data_response = supabase.table("user_onboarding").select("*").execute()
    all_users = user_data_response.data if user_data_response.data else []

    st.subheader("All Onboarded Users")
    if not all_users:
        st.info("No users found.")
    else:
        for user in all_users:
            st.write(f"- **User ID**: {user['user_id']}")
            st.write(f"  **Name**: {user['contact_name']}")
            st.write(f"  **Email**: {user['email_address']}")
            st.write("---")
