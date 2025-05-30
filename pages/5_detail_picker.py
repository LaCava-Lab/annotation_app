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

with open("interchange.json", "r", encoding="utf-8") as f:
    interchange = json.load(f)

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

# Sidebar style
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
        {"label": "Coffee Break A"},
        {"label": "Experiment Details"},
        {"label": "Coffee Break B"},
        {"label": "Solution Details"},
        {"label": "Coffee Break C"}
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

doi_link = st.session_state.get("doi_link")

# Main content
current_label = st.session_state.current_page["page"]["label"]

if current_label == st.session_state.links[0]["label"]:
    st.title(st.session_state.links[0]["label"])
elif current_label == st.session_state.links[1]["label"]:
    st.title(st.session_state.links[1]["label"])
elif current_label == st.session_state.links[2]["label"]:
    # Hide sidebar with CSS
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .block-container {padding-top: 4rem;}
        </style>
    """, unsafe_allow_html=True)

    # Fetch Coffee Break A text from interchange.json
    coffee_break_a = interchange["pages"]["5_detail_picker"]["coffee_break_a"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_a['title']}")
    st.write(coffee_break_a["body"])

    if doi_link:
        st.button("Go to full-text paper", on_click=lambda: st.write(f"[Go to full-text paper]({doi_link})"))

    # Editable table for experiments and solutions
    exp_df = pd.DataFrame([
        {
            "Experiment name": "Immunoprecipitation",
            "Alternative Experiment Name": "",
            "Experiment Type": "PI",
            "Solution name": "extraction solution",
            "Alternative Solution Name": "",
            "Solution Type": "PI"
        }
    ])

    edited_df = st.data_editor(
        exp_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Experiment name": st.column_config.TextColumn("Experiment name", disabled=True),
            "Alternative Experiment Name": st.column_config.TextColumn("Alternative Experiment Name"),
            "Experiment Type": st.column_config.SelectboxColumn(
                "Experiment Type", options=["PI", "non-PI"]
            ),
            "Solution name": st.column_config.TextColumn("Solution name", disabled=True),
            "Alternative Solution Name": st.column_config.TextColumn("Alternative Solution Name"),
            "Solution Type": st.column_config.SelectboxColumn(
                "Solution Type", options=["PI", "non-PI"]
            ),
        },
        key="exp_editor"
    )

    # Validate and correct Solution Type based on Experiment Type
    corrected = False
    for idx, row in edited_df.iterrows():
        if row["Experiment Type"] == "non-PI" and row["Solution Type"] != "non-PI":
            edited_df.at[idx, "Solution Type"] = "non-PI"
            corrected = True

    if corrected:
        st.error("Solution Type was set to 'non-PI' for rows where Experiment Type is 'non-PI'.")

    # Save buttons for navigation
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            save()
            next()
elif current_label == st.session_state.links[3]["label"]:
    st.title(st.session_state.links[3]["label"])
elif current_label == st.session_state.links[4]["label"]:
    # Hide sidebar with CSS
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .block-container {padding-top: 4rem;}
        </style>
    """, unsafe_allow_html=True)

    # Fetch Coffee Break B text from interchange.json
    coffee_break_b = interchange["pages"]["5_detail_picker"]["coffee_break_b"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_b['title']}")
    st.write(coffee_break_b["body"])

    doi_link = st.session_state.get("doi_link")
    if doi_link:
        st.button("Go to full-text paper", on_click=lambda: st.write(f"[Go to full-text paper]({doi_link})"))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.selectbox("Experiment", ["Experiment"], key="experiment_select")
    with col2:
        st.selectbox("Bait 1", ["Bait 1"], key="bait_select")

    st.markdown("### Bait details:")

    bait_df = pd.DataFrame([
        {
            "Bait type 1": "Protein",
            "Bait type 2": "Experimental",
            "Name": "ORF2p",
            "Alt name": "",
            "Tag": "N/A",
            "Alt tag": "",
            "Species": "HEK293T",
            "Alt. species": "H.sapiens",
        }
    ])
    st.data_editor(
        bait_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bait_editor",
        column_config={
            "Bait type 1": st.column_config.TextColumn("Bait type 1", disabled=True),
            "Bait type 2": st.column_config.TextColumn("Bait type 2", disabled=True),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Alt name": st.column_config.TextColumn("Alt name"),
            "Tag": st.column_config.TextColumn("Tag"),
            "Alt tag": st.column_config.TextColumn("Alt tag"),
            "Species": st.column_config.TextColumn("Species"),
            "Alt. species": st.column_config.TextColumn("Alt. species"),
        }
    )

    st.markdown("### Interactor(s) details:")

    interactor_df = pd.DataFrame([
        {
            "Bait ref": 1,
            "Interactor type": "protein",
            "Name": "",
            "Alternative name": "N/A",
            "Species": "HEK293T",
            "Alternative species": "H.sapiens",
        }
    ])
    st.data_editor(
        interactor_df,
        num_rows="dynamic",
        use_container_width=True,
        key="interactor_editor",
        column_config={
            "Bait ref": st.column_config.TextColumn("Bait ref", disabled=True),
            "Interactor type": st.column_config.TextColumn("Interactor type", disabled=True),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Alternative name": st.column_config.TextColumn("Alternative name"),
            "Species": st.column_config.TextColumn("Species"),
            "Alternative species": st.column_config.TextColumn("Alternative species"),
        }
    )

    # Save buttons for navigation
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            save()
            next()

elif current_label == st.session_state.links[5]["label"]:
    st.title(st.session_state.links[5]["label"])
elif current_label == st.session_state.links[6]["label"]:

    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .block-container {padding-top: 4rem;}
        </style>
    """, unsafe_allow_html=True)

    # Fetch Coffee Break C text from interchange.json
    coffee_break_c = interchange["pages"]["5_detail_picker"]["coffee_break_c"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_c['title']}")
    st.write(coffee_break_c["body"])

    doi_link = st.session_state.get("doi_link")
    if doi_link:
        st.button("Go to full-text paper", on_click=lambda: st.write(f"[Go to full-text paper]({doi_link})"))

    # Dropdowns
    col1, col2 = st.columns([1, 1])
    with col1:
        experiment_type = st.selectbox("Experiment Type", ["PI", "non-PI"], key="exp_type_3")
    with col2:
        if experiment_type == "PI":
            solution_type_options = ["PI", "non-PI"]
        else:
            solution_type_options = ["non-PI"]
        solution_type = st.selectbox("Solution Type", solution_type_options, key="sol_type_3")

    # pH, Temperature, Time
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        st.text_input("pH", value="7.4")
    with col2:
        st.text_input("Temperature (°C)", value="4", key="temperature_input")
    with col3:
        st.selectbox(
            "Time",
            [
                "0–5 min", "5–10 min", "10–15 min", "15–30 min", "30–60 min",
                "1–2 h", "2–4 h", "4–8 h", "8–16 h"
            ],
            key="time_select"
        )
    # Radio buttons
    st.radio(
        "Solution details",  # Non-empty label for accessibility
        ["Solution details not listed:", "Solution details listed:"],
        index=1,
        key="solution_details_radio",
        label_visibility="collapsed"  # Hides the label visually
    )

    # Editable table for solution details
    solution_df = pd.DataFrame([
        {
            "Chemical type": "Buffer",
            "Name": "HEPES",
            "Alternative name": "",
            "Quantity": "20",
            "Alternative Quantity": "",
            "Unit": "mM",
            "Alternative unit": ""
        }
    ])
    st.data_editor(
        solution_df,
        num_rows="dynamic",
        use_container_width=True,
        key="solution_editor",
        column_config={
            "Chemical type": st.column_config.SelectboxColumn(
                "Chemical type",
                options=[
                    "Buffer", "Salt", "Detergent", "Enzyme", "Inhibitor",
                    "Reducing agent", "Substrate", "Other"
                ]
            ),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Quantity": st.column_config.TextColumn("Quantity", disabled=True),
            "Unit": st.column_config.TextColumn("Unit", disabled=True),
        }
    )

    # Save buttons for navigation
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            st.switch_page("pages/7_thanks.py")
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

def render_highlighter():
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
    st.session_state["results"] = results  # Store results in session_state

def render_sidebar():
    with st.sidebar:
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

        results = st.session_state.get("results", [])
        for tab_index, tab_results in enumerate(results):  # results is your list of lists
            for i, item in enumerate(tab_results):
                colored_card(
                    title=f"{item['tag']}",
                    subtitle=item['text'],
                    bg_color=item['color']
                )

# Render sidebar and highlighter everywhere except coffee breaks
if "Coffee Break" not in current_label:
    render_highlighter()
    render_sidebar()