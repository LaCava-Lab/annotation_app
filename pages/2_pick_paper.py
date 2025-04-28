import streamlit as st

st.set_page_config(page_title="Pick Paper", layout="wide")

st.title("Select the paper you will annotate")
st.markdown("""
            Go through the list of five options we offer bellow and select the paper you are most comfortable with (yes, if it is a paper you co-authored you can still be the annotator. Actually it would be ideal!). Feel free to follow the external links to the paper's full text to understand better its question and experimental methodologies. If you don't like any of the five papers we randomly selected for you, just refresh the list through the button bellow for new options.
            """)

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

def select(option, key):
    if st.session_state.selected_option == option:
        st.session_state.selected_option = None
        st.session_state[key] = False  # uncheck this one
    else:
        st.session_state.selected_option = option
        # uncheck all others
        for k in ["a", "b", "c", "d", "e"]:
            if k != key:
                st.session_state[k] = False
                
st.write("")
st.write("")
st.write("")

page_1 = st.checkbox("Authors1, Title1, Journal1, Issue1, volume1, pages1, link1",
                     key="a", value=st.session_state.get("a", False),
                     on_change=select, args=("A", "a"))
page_2 = st.checkbox("Authors2, Title2, Journal2, Issue2, volume2, pages2, link2",
                     key="b", value=st.session_state.get("b", False),
                     on_change=select, args=("B", "b"))
page_3 = st.checkbox("Authors3, Title3, Journal3, Issue3, volume3, pages3, link3",
                     key="c", value=st.session_state.get("c", False),
                     on_change=select, args=("C", "c"))
page_4 = st.checkbox("Authors4, Title4, Journal4, Issue4, volume4, pages4, link4",
                     key="d", value=st.session_state.get("d", False),
                     on_change=select, args=("D", "d"))
page_5 = st.checkbox("Authors5, Title5, Journal5, Issue5, volume5, pages5, link5",
                     key="e", value=st.session_state.get("e", False),
                     on_change=select, args=("E", "e"))

st.write("")
st.write("")
st.write("")

col2,col3 = st.columns([6,6], gap="large")

with col2:
    st.button("Go to annotation", type="primary", disabled=not st.session_state.selected_option)

with col3:
    st.button("Refresh paper list", type="secondary")