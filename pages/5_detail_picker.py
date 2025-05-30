import streamlit as st
import uuid

# Set page config
st.set_page_config(initial_sidebar_state="expanded", page_title="Paper Annotation", layout="wide")
st.set_option("client.showSidebarNavigation", False)

import pandas as pd
import json
import os
from streamlit_cookies_manager import CookieManager
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
from process_interchange import detail_picker
from src.various import get_pmid, handle_redirects

from st_components.BreadCrumbs import BreadCrumbs

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")

if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Path to the folder containing JSON files
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = r"AWS_S3/users_table.xlsx"


# Function to load the selected paper's JSON file based on the PMID
def load_paper_by_pmid(pmid):
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # Check if the PMID matches
                    doc = raw[0]["documents"][0]
                    front = doc["passages"][0]  # Front matter
                    meta = front["infons"]
                    extracted_pmid = meta.get("article-id_pmid", None)
                    if extracted_pmid == pmid:
                        return raw
            except Exception as e:
                st.error(f"Error reading file {filename}: {e}")
    st.error(f"No JSON file found for PMID: {pmid}")
    st.stop()


# Fetch the PMID
pmid = get_pmid(cookies)

# Load the selected paper's JSON file
if "paper_data" not in st.session_state:
    raw = load_paper_by_pmid(pmid)
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

def colored_card(title, subtitle, bg_color="#1f77b4", text_color="#ffffff", key=None):
    if key is None:
        key = str(uuid.uuid4())  # Generate unique key if none provided

    container_id = f"card-{key}"

    st.markdown(f"""
                <div id="{container_id}" style="
                background: linear-gradient(135deg, {bg_color}, #333333);
                padding: 1.5rem;
                border-radius: 1.25rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                margin: 1rem 0;
                ">
                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.3rem;">
                                {title}
                </div>
                <div style="font-size: 1rem; font-weight: 400; opacity: 0.85;">
                                {subtitle}
                </div>
                </div>
        """, unsafe_allow_html=True)


if "pages" not in st.session_state:
    st.session_state.links = [
        {"label": "Experiment Picker"},
        {"label": "Solution Picker"},
        {"label": "Coffee Break"},
        {"label": "Protocol Details"},
        {"label": "Solution Details"},
    ]
    st.session_state.pages = [
        {"index": i + 1, "label": link["label"], "visited": 0}
        for i, link in enumerate(st.session_state.links)
    ]
    st.session_state.current_page = {"page": st.session_state.links[0], "index": 0}
    st.session_state.pages[0]["visited"] = 1


# func to change page
def changePage(index):
    st.session_state.current_page = {
        "page": st.session_state.links[index],
        "index": index
    }
    st.session_state.pages[index]["visited"] = 1
    st.rerun()


def next():
    if st.session_state.current_page["index"] < len(st.session_state.links) - 1:
        changePage(st.session_state.current_page["index"] + 1)

def prev():
    if st.session_state.current_page["index"] > 0:
        changePage(st.session_state.current_page["index"] - 1)

def save():
    pass

pageSelected = BreadCrumbs(st.session_state.links,st.session_state.current_page["page"],pages=st.session_state.pages)
# for i, link in enumerate(st.session_state.links):
#     if link["label"] == pageSelected:
#         st.session_state.current_page = {
#             "page": st.session_state.links[i],
#             "index": i
#         }
#         break

if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
    st.title(st.session_state.links[0]["label"])
elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
    st.title(st.session_state.links[1]["label"])
elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
    st.title(st.session_state.links[2]["label"])
elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
    st.title(st.session_state.links[3]["label"])
elif st.session_state.current_page["page"]["label"] == st.session_state.links[4]["label"]:
    st.title(st.session_state.links[4]["label"])
else:
    st.title("")



# Functions to load paper text + labels
@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"]
    tmp = df[df.section_type == tab_name]
    return tmp['text'].str.cat(sep="\n\n") if not tmp.empty else detail_picker["no_content_tab"]


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

results = []

for name, tab in zip(tab_names, tabs):
    with tab:
        result = text_highlighter(
            text=get_tab_body(name),
            labels=get_labels(),
            text_height=400,
            key=f"text_highlighter_{name}"  # Assign a unique key for each tab
        )

        results.append(result)

with st.sidebar:
    # Use the DOI link dynamically
    doi_link = st.session_state.get("doi_link")
    if doi_link:
        st.link_button("Go to full-text paper", doi_link)
    else:
        st.write("DOI link not available for this paper.")
    st.title("Paper Annotation")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("Prev"):
            prev()

    with col2:
        if st.button("Save"):
            save()

    with col3:
        if st.button("Save & Next"):
            save()
            next()

    table = TableSelect()

    for tab_index, tab_results in enumerate(results):  # results is your list of lists
        for i, item in enumerate(tab_results):
            colored_card(
                title=f"{item['tag']}",
                subtitle=item['text'],
                bg_color=item['color']
            )
