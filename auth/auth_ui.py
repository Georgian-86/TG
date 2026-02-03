#2iGL76G9H5ah2Ka

import streamlit as st
from auth.user_db import create_user, verify_user
from auth.otp import generate_otp, send_otp

def auth_ui():
    st.title("🔐 TeachGenie.ai Access")

    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])

    # ---------------- SIGN IN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Sign In"):
            if verify_user(email, password):
                otp = generate_otp()
                st.session_state.otp = otp
                st.session_state.pending_user = email
                send_otp(email, otp)
                st.success("OTP sent to your email 📩")
            else:
                st.error("Invalid email or password")

    # ---------------- SIGN UP ----------------
    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if new_pass != confirm:
                st.error("Passwords do not match")
            elif create_user(new_email, new_pass):
                st.success("Account created! Please sign in 🔑")
            else:
                st.error("User already exists")

    # ---------------- OTP ----------------
    if "otp" in st.session_state:
        st.divider()
        entered = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if entered == st.session_state.otp:
                st.session_state.logged_in = True
                st.success("Login successful 🎉")
            else:
                st.error("Invalid OTP")
