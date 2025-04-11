# auth.py

import streamlit as st
from supabase import create_client, Client, AuthApiError

def render_login_view(supabase: Client):
    """
    Displays the login form and handles login logic.
    """
    st.image("VATIFY.png", width=150)  # Smaller logo
    st.title("VATIFY: Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user and user.user:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.user.id
                st.session_state["user_email"] = user.user.email
                st.success(f"Welcome back, {user.user.email}!")
                st.rerun()
            else:
                st.error("Invalid credentials, please try again.")
        except AuthApiError as e:
            st.error(f"Error logging in: {e}")

    if st.button("Go to Sign Up"):
        st.session_state["auth_mode"] = "signup"
        st.rerun()

    if st.button("Forgot Password?"):
        st.session_state["auth_mode"] = "forgot_password"
        st.rerun()


def render_signup_view(supabase: Client):
    """
    Displays the sign-up form and handles user registration logic.
    Inserts a default role ("user") from the front end.
    (Ensure that any trigger on auth.users for inserting into user_roles is disabled or removed.)
    """
    st.image("VATIFY.png", width=150)  # Smaller logo
    st.title("VATIFY: Sign Up")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not email or not password or not confirm_password:
            st.error("All fields are required.")
            return
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        try:
            # Attempt to sign up using Supabase Auth.
            result = supabase.auth.sign_up({"email": email, "password": password})
            # Check if a user object exists.
            if not result.user:
                st.error("Sign up failed. Please try again.")
            else:
                # Insert the default role into user_roles table from the front end.
                default_role = {"user_id": result.user.id, "role": "user"}
                supabase.table("user_roles").insert(default_role).execute()

                st.success("Sign up successful! Please check your email for the verification link.")
                st.session_state["auth_mode"] = "login"
                st.rerun()
        except Exception as e:
            st.error(f"Error signing up: {e}")

    if st.button("Go to Login"):
        st.session_state["auth_mode"] = "login"
        st.rerun()



def render_forgot_password_view(supabase: Client):
    """
    Displays the forgot password form and sends a password reset link.
    """
    st.image("VATIFY.png", width=150)  # Smaller logo
    st.title("VATIFY: Forgot Password")

    email = st.text_input("Enter your email address")

    if st.button("Send Reset Link"):
        if not email:
            st.error("Please enter an email address.")
            return

        try:
            supabase.auth.reset_password_for_email(email)
            st.success(f"Password reset link sent to {email}.")
        except AuthApiError as e:
            st.error(f"Error sending password reset: {e}")

    if st.button("Go to Login"):
        st.session_state["auth_mode"] = "login"
        st.rerun()


def logout_user():
    """
    Logs out the current user by clearing session state.
    """
    st.session_state.clear()
    st.session_state["auth_mode"] = "login"
    st.rerun()
