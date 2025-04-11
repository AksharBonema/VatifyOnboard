import streamlit as st
from supabase import create_client, Client

# Import local modules
import auth
import onboard
import user_profile
import admin
import contact
import live_demo

# Initialize connection to Supabase
SUPABASE_URL = "https://wtpufclshxbpkdnuczzq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0cHVmY2xzaHhicGtkbnVjenpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQyNjU2NDAsImV4cCI6MjA1OTg0MTY0MH0.tW8TD_F4dmOGH4TEzFMZmeQmdtDlJ6dZQg8mjH1Ad1A"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_user_role(user_id: str) -> str:
    """
    Fetch the user's role from a 'user_roles' table.
    Returns 'admin' if found, otherwise 'user'.
    """
    role_resp = supabase.table("user_roles").select("role").eq("user_id", user_id).execute()
    if role_resp.data and len(role_resp.data) > 0:
        return role_resp.data[0]["role"]
    return "user"

def main():
    st.set_page_config(page_title="VATIFY", layout="wide")

    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"  # can be 'login', 'signup', 'forgot_password'
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"
    if "role" not in st.session_state:
        st.session_state["role"] = "user"

    if not st.session_state["logged_in"]:
        # Render auth screens
        if st.session_state["auth_mode"] == "login":
            auth.render_login_view(supabase)
        elif st.session_state["auth_mode"] == "signup":
            auth.render_signup_view(supabase)
        elif st.session_state["auth_mode"] == "forgot_password":
            auth.render_forgot_password_view(supabase)
    else:
        # Fetch role if it is still default (i.e., not changed)
        if st.session_state["role"] == "user":
            user_role = fetch_user_role(st.session_state["user_id"])
            st.session_state["role"] = user_role

        # Logged in user: show sidebar with icons
        st.sidebar.image("VATIFY.png", use_container_width=True)

        # Build dynamic menu; "Admin" will be shown only if the role is "admin".
        base_pages = ["Home", "Onboard", "Profile", "Contact", "Live Demo", "Logout"]
        if st.session_state["role"] == "admin":
            base_pages.insert(3, "Admin")  # Insert Admin before Contact

        menu = st.sidebar.radio(
            "VATIFY Menu",
            options=base_pages,
            format_func=lambda x: {
                "Home": "🏠 Home",
                "Onboard": "📝 Onboard",
                "Profile": "👤 Profile",
                "Contact": "📞 Contact",
                "Admin": "🔧 Admin",
                "Live Demo": "🎬 Live Demo",
                "Logout": "🚪 Logout"
            }[x]
        )

        if menu == "Home":
            st.session_state["current_page"] = "Home"

            st.markdown("## 👋 Welcome to VATIFY,")
            st.markdown(f"### {st.session_state.get('user_email', 'User')}")
            st.markdown("---")

            # Create columns for quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                onboarding = supabase.table("user_onboarding").select("*").eq("user_id", st.session_state["user_id"]).execute()
                onboarding_data = onboarding.data[0] if onboarding.data else None
                if onboarding_data:
                    st.metric(label="🧾 Onboarding Status", value="Complete")
                else:
                    st.metric(label="🧾 Onboarding Status", value="Incomplete")
            with col2:
                docs = supabase.table("document_uploads").select("*").eq("user_id", st.session_state["user_id"]).execute()
                doc_data = docs.data[0] if docs.data else None
                uploaded_docs = sum(
                    1 for key in ["cipc_document_url", "id_document_url", "tax_clearance_url", "power_of_attorney_url"]
                    if doc_data and doc_data.get(key)
                )
                st.metric(label="📂 Documents Uploaded", value=f"{uploaded_docs}/4")
            with col3:
                profile_complete = all([
                    onboarding_data.get("contact_name"),
                    onboarding_data.get("company_name"),
                    onboarding_data.get("email_address")
                ]) if onboarding_data else False
                st.metric(label="👤 Profile Info", value="Complete" if profile_complete else "Incomplete")

            st.markdown("---")
            st.subheader("📋 Next Steps")
            if not onboarding_data:
                st.warning("You haven’t started your onboarding yet. Click the 📝 Onboard tab to begin.")
            elif uploaded_docs < 4:
                st.info("You're almost there! Please upload the remaining documents.")
            else:
                st.success("All done! We'll process your registration soon.")
            st.markdown("### 💡 Tips to get started:")
            st.markdown("""
            - Use the **📝 Onboard** tab to update your company and contact details.
            - Upload key documents like your CIPC and Tax Clearance.
            - Track your progress using this dashboard.
            - Need help? Reach out to our support team at [bokang@bonema.co.za](mailto:bokang@bonema.co.za)
            """)
            st.markdown("---")
            st.caption("© 2025 VATIFY. All rights reserved.")

        elif menu == "Onboard":
            st.session_state["current_page"] = "Onboard"
            onboard.render_onboarding_form(supabase)

        elif menu == "Profile":
            st.session_state["current_page"] = "Profile"
            user_profile.render_user_profile(supabase)
        
        elif menu == "Contact":
            st.session_state["current_page"] = "Contact"
            contact.render_contact_page()
        
        elif menu == "Admin":
            st.session_state["current_page"] = "Admin"
            admin.render_admin_dashboard(supabase)
        
        elif menu == "Live Demo":
            st.session_state["current_page"] = "Live Demo"
            # Call live_demo without passing supabase, as it's not required.
            live_demo.render_live_demo_page()
        
        elif menu == "Logout":
            auth.logout_user()  # Clears session state and reruns

if __name__ == "__main__":
    main()
