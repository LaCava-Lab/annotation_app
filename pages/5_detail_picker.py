import streamlit as st
from st_components.TableSelect import TableSelect
from st_components.BreadCrumbs import BreadCrumbs

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

links = [
    {"label": "Protocol Picker"},
    {"label": "Solution Picker"},
    {"label": "Protocol Details"},
    {"label": "Solution Details"},
]

with st.sidebar:
    st.title("Paper Annotation")
    table = TableSelect()

pageSelected = BreadCrumbs(links)

if pageSelected == "Protocol Picker":
    st.title("Protocol Picker")
elif pageSelected == "Solution Picker":
    st.title("Solution Picker")
elif pageSelected == "Protocol Details":
    st.title("Protocol Details")
elif pageSelected == "Solution Details":
    st.title("Solution Details")
else:
    st.title("Unknown Page")

