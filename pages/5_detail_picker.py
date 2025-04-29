import streamlit as st
import pandas as pd
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect

# Fallback initialization for session state
if "paper_data" not in st.session_state:
    df = pd.read_csv("AWS_S3/papers/pmid000.csv")
    df.fillna(value={'subtitle': '0'}, inplace=True)
    st.session_state["paper_data"] = df

# Sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 370px;
        }
    </style>
    <style>
        .block-container {
            padding-top: 4rem;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.link_button("Go to full-text paper", 'https://doi.org/10.1073/pnas.1121568109')
    st.title("Paper Annotation")
    TableSelect()

# Functions to load paper text + labels
@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"]
    if tab_name == "Front page":
        tmp = df[df.section_title.isin(["Title", "Authors", "Abstract"])]
        return tmp['paragraph_string'].str.cat(sep="\n\n")
    elif tab_name in ["Introduction", "Materials and Methods", "Results", "Discussion", "Legends"]:
        txt = ""
        tmp = df[df.section_title == tab_name]
        subsections = tmp['subtitle'].unique()
        for sub in subsections:
            if sub == '0':
                txt += tmp['paragraph_string'].str.cat(sep="\n\n") + "\n\n"
            else:
                txt += f"\n\n{sub}"
                sub_txt = tmp[tmp.subtitle == sub]['paragraph_string'].str.cat(sep="\n")
                txt += f"\n\n{sub_txt}"
        return txt
    return "Trouble"

@st.cache_data
def get_labels():
    return [
        ("buffer", "pink"),
        ("pH", "lightsalmon"),
        ("salt", "lightblue"),
        ("detergent", "yellow"),
        ("chelating", "orange"),
        ("inhibitors", "violet"),
        ("other", "lightgrey")
    ]

# Main app: Tabs + Highlighting

tab_names = ["Front page", "Introduction", "Materials and Methods", "Results", "Discussion", "Legends"]
tabs = st.tabs(tab_names)

for name, tab in zip(tab_names, tabs):
    with tab:
        result = text_highlighter(
            text=get_tab_body(name),
            labels=get_labels(),
            text_height=400
        )
