import streamlit as st
import pandas as pd
import json
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
# from st_components.BreadCrumbs import BreadCrumbs

# Set page config
st.set_page_config(initial_sidebar_state="expanded", page_title="Paper Annotation", layout="wide")

# Fallback initialization for session state
if "paper_data" not in st.session_state:
    # Load the selected paper's JSON file
    selected_paper = st.session_state.get("selected_paper")
    if selected_paper:
        json_path = f"Full_text_jsons/{selected_paper['filename']}"
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            doc = raw[0]["documents"][0]
            all_data = []
            doi_link = None  # Initialize DOI link
            for passage in doc["passages"]:
                section_type = passage["infons"].get("section_type", "Unknown")
                text = passage.get("text", "")
                all_data.append({
                    "section_type": section_type,
                    "text": text
                })
                # Extract DOI link from the metadata
                if "article-id_doi" in passage["infons"]:
                    doi_link = f"https://doi.org/{passage['infons']['article-id_doi']}"
            # Convert to DataFrame
            df = pd.DataFrame(all_data)
            # Filter out sections that do not need to be annotated
            df = df[~df["section_type"].isin(["TITLE", "REF", "SUPPL", "AUTH_CONT", "COMP_INT", "ACK_FUND"])]
            st.session_state["paper_data"] = df
            st.session_state["tab_names"] = df["section_type"].unique().tolist()  # Extract unique tab names
            st.session_state["doi_link"] = doi_link  # Save the DOI link in session state
    else:
        st.error("No paper selected. Please go back to the Pick Paper page.")
        st.stop()

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

links = [
    {"label": "Protocol Picker"},
    {"label": "Solution Picker"},
    {"label": "Protocol Details"},
    {"label": "Solution Details"},
]

with st.sidebar:
    # Use the DOI link dynamically
    doi_link = st.session_state.get("doi_link")
    if doi_link:
        st.link_button("Go to full-text paper", doi_link)
    else:
        st.write("DOI link not available for this paper.")
    st.title("Paper Annotation")
    table = TableSelect()

# pageSelected = BreadCrumbs(links)
#
# if pageSelected == "Protocol Picker":
#     st.title("Protocol Picker")
# elif pageSelected == "Solution Picker":
#     st.title("Solution Picker")
# elif pageSelected == "Protocol Details":
#     st.title("Protocol Details")
# elif pageSelected == "Solution Details":
#     st.title("Solution Details")
# else:
#     st.title("Unknown Page")

# Functions to load paper text + labels
@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"]
    tmp = df[df.section_type == tab_name]
    return tmp['text'].str.cat(sep="\n\n") if not tmp.empty else "No content available for this section."

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

# Dynamically load tab names from session state
tab_names = st.session_state.get("tab_names", ["Unknown"])
tabs = st.tabs(tab_names)

for name, tab in zip(tab_names, tabs):
    with tab:
        result = text_highlighter(
            text=get_tab_body(name),
            labels=get_labels(),
            text_height=400,
            key=f"text_highlighter_{name}"  # Assign a unique key for each tab
        )