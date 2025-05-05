import streamlit as st

def show_error_page():
    st.title("Log-in error")

    with st.container():
        st.markdown("""
        <div style="border: 1px solid #ccc; padding: 20px; background-color: #f9f9f9; border-radius: 5px;">
            <p>An error has occurred with your PIN when attempting to log you in. Please verify your e-mail matches the one you registered with and your PIN is the same you received by us. Both information is available in the verification e-mail we sent you from <strong>name@email.com</strong> after registration.</p>
            <p><strong>Note:</strong> YOU NEED TO HAVE REGISTERED TO HAVE A PIN. Go to the registration page if you have not already done so.</p>
            <p>If you have a PIN and still can't log in, contact <strong>info@email.com</strong> using your registered email with subject line "Lost PIN".</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back to log in page"):
            st.session_state.show_error = False
            st.experimental_rerun()

    with col2:
        if st.button("Go to registration page"):
            st.switch_page("pages/????.py") #still need to fill the page
