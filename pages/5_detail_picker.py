import streamlit as st
from st_components.TableSelect import TableSelect

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 370px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Using "with" notation
with st.sidebar:
    st.title("Paper Annotation")

    TableSelect()

