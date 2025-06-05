import streamlit as st

st.set_page_config(page_title="Log-in error")

st.title("Log-in error")

st.write("""
An error has occurred with your PIN when attempting to log you in. Please verify your e-mail matches the one you registered with and your PIN is the same you received by us. Both information is available in the verification e-mail we sent you from name1@email.com after registration. Please note, YOU NEED TO HAVE REGISTERED TO HAVE A PIN, go to the registration page if you have not already done so.

If you have a PIN and you try to log in again with the correct information and you still have issues please contact info@email.com using the email you used to register and the subject line “Lost PIN”. We will reach out to you help regarding recovering your PIN.
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("Back to log in page"):
        st.switch_page("login.py")

with col2:
    st.button("Go to registration page", disabled=True)