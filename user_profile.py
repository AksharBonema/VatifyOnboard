# user_profile.py

import streamlit as st
from supabase import Client

def render_user_profile(supabase: Client):
    """
    Displays user profile info and allows updates if necessary.
    """
    st.title("My Profile")

    user_id = st.session_state["user_id"]
    user_details_response = supabase.table("user_onboarding").select("*").eq("user_id", user_id).execute()
    user_details = user_details_response.data[0] if user_details_response.data else None

    if not user_details:
        st.info("No onboarding data found. Please complete onboarding first.")
        return

    st.write("**Contact Name:**", user_details.get("contact_name", ""))
    st.write("**Email Address:**", user_details.get("email_address", ""))
    st.write("**Mobile:**", user_details.get("mobile", ""))
    st.write("**Company Name:**", user_details.get("company_name", ""))

    st.write("---")
    st.subheader("Update Profile Info")

    new_contact_name = st.text_input("Contact Name", user_details.get("contact_name", ""))
    new_mobile = st.text_input("Mobile", user_details.get("mobile", ""))

    if st.button("Update Profile"):
        update_payload = {
            "contact_name": new_contact_name,
            "mobile": new_mobile
        }
        supabase.table("user_onboarding").update(update_payload).eq("user_id", user_id).execute()
        st.success("Profile updated successfully!")
        st.rerun()
