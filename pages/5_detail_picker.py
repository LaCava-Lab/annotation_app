import streamlit as st
import uuid
import pandas as pd
import json
from streamlit_cookies_manager import CookieManager
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
from process_interchange import detail_picker
from src.various import get_pmid, handle_redirects, get_token, get_user_key
from st_components.BreadCrumbs import BreadCrumbs
from src.database import fetch_fulltext_by_pmid, add_completed_paper, clear_paper_in_progress, fetch_doi_by_pmid

# Set page config
st.set_page_config(initial_sidebar_state="expanded", page_title="Paper Annotation", layout="wide")
st.set_option("client.showSidebarNavigation", False)

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

with open("interchange.json", "r", encoding="utf-8") as f:
    interchange = json.load(f)

# State persistence helpers
def save_state_to_cookies():
    cookies["cards"] = json.dumps(st.session_state.get("cards", []))
    cookies["current_page"] = json.dumps(st.session_state.get("current_page", {}))
    cookies["pages"] = json.dumps(st.session_state.get("pages", []))
    cookies["active_solution_btn"] = json.dumps(st.session_state.get("active_solution_btn", {}))

def load_state_from_cookies():
    if "cards" not in st.session_state and "cards" in cookies and cookies["cards"]:
        st.session_state["cards"] = json.loads(cookies["cards"])
    if "current_page" not in st.session_state and "current_page" in cookies and cookies["current_page"]:
        st.session_state["current_page"] = json.loads(cookies["current_page"])
    if "pages" not in st.session_state and "pages" in cookies and cookies["pages"]:
        st.session_state["pages"] = json.loads(cookies["pages"])
    if "active_solution_btn" not in st.session_state and "active_solution_btn" in cookies and cookies["active_solution_btn"]:
        st.session_state["active_solution_btn"] = json.loads(cookies["active_solution_btn"])

# Load app state from cookies if present
load_state_from_cookies()

# Initialize session state
if "links" not in st.session_state:
    st.session_state.links = [
        {"label": "Experiment Picker"},
        {"label": "Solution Picker"},
        {"label": "Coffee Break A"},
        {"label": "Experiment Details"},
        {"label": "Coffee Break B"},
        {"label": "Solution Details"},
        {"label": "Coffee Break C"}
    ]
if "pages" not in st.session_state:
    st.session_state.pages = [
        {"index": i + 1, "label": link["label"], "visited": 0}
        for i, link in enumerate(st.session_state.links)
    ]
    st.session_state.pages[0]["visited"] = 1
if "current_page" not in st.session_state:
    st.session_state.current_page = {"page": st.session_state.links[0], "index": 0}

# Initialize cards for each page
if "cards" not in st.session_state:
    st.session_state["cards"] = [[] for _ in range(len(st.session_state.links))]
    
# Fetch the PMID
pmid = get_pmid(cookies)

# Redirect to pick paper if no paper in progress
if not pmid:
    st.error("No paper in progress. Please pick a paper to annotate.")
    st.switch_page("pages/2_pick_paper.py")

# Normalizing tab names to full section names
def normalize_section_name(section):
    s = section.strip().upper()
    if "INTRO" in s:
        return "INTRODOCTION"
    if "METHOD" in s:
        return "METHODS"
    if "RESULT" in s:
        return "RESULTS"
    if "DISCUSS" in s:
        return "DISCUSSION"
    if "SUPPL" in s:
        return "SUPPLEMENTARY"
    return section.strip()

# Load the selected paper's fulltext using backend function
if "paper_data" not in st.session_state:
    raw = fetch_fulltext_by_pmid(pmid, get_token(cookies))
    df = pd.DataFrame(raw)
    if df.empty:
        st.error("No fulltext data available for this paper.")
        st.stop()
    # Only keep rows with non-empty text
    df = df[df["TextValue"].notnull() & (df["TextValue"].str.strip() != "")]
    df = df.rename(columns={"TextValue": "text"})
    # Exclude ISSUE and FIG sections
    df = df[~df["Section"].str.upper().isin(["ISSUE", "FIG"])]
    # Normalize section names
    df["section_type"] = df["Section"].apply(normalize_section_name)
    st.session_state["paper_data"] = df
    st.session_state["tab_names"] = df["section_type"].drop_duplicates().tolist()
    token = get_token(cookies)
    doi_link = fetch_doi_by_pmid(pmid, token)
    if doi_link and not str(doi_link).startswith("http"):
        doi_link = f"https://doi.org/{doi_link}"
    st.session_state["doi_link"] = doi_link

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
        key = str(uuid.uuid4())
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

@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"]
    tmp = df[df.section_type == tab_name]
    lines = []
    for _, row in tmp.iterrows():
        t = row.get("Type", "").lower()
        text = row["text"]
        if t == "title_1":
            lines.append(f"# {text}")  # Largest heading
        elif t == "title_2":
            lines.append(f"## {text}")  # Second largest heading
        elif t == "title":
            lines.append(f"### {text}")  # Third largest heading
        else:
            lines.append(text)
    return "\n\n".join(lines) if lines else "No content available for this section."

# Page navigation helpers
def changePage(index):
    st.session_state.current_page = {
        "page": st.session_state.links[index],
        "index": index
    }
    st.session_state.pages[index]["visited"] = 1
    save_state_to_cookies()
    st.rerun()

def next():
    if st.session_state.current_page["index"] < len(st.session_state.links) - 1:
        changePage(st.session_state.current_page["index"] + 1)

def prev():
    if st.session_state.current_page["index"] > 0:
        changePage(st.session_state.current_page["index"] - 1)

def save():
    save_state_to_cookies()

pageSelected = BreadCrumbs(st.session_state.links, st.session_state.current_page["page"], pages=st.session_state.pages)

def check_tag(tag):
    if 'non-PI' in tag:
        return "non-PI"
    else:
        return "PI"

doi_link = st.session_state.get("doi_link")

def displayTextHighlighter(labels, index):
    tab_names = st.session_state.get("tab_names", ["Unknown"])
    tabs = st.tabs(tab_names)
    results = []
    for i, (name, tab) in enumerate(zip(tab_names, tabs)):
        annotations = []
        if (len(st.session_state["cards"][st.session_state.current_page["index"]]) > 0):
            annotations = st.session_state["cards"][st.session_state.current_page["index"]][i]
        with tab:
            result = text_highlighter(
                text=get_tab_body(name),
                labels=labels,
                text_height=400,
                annotations=annotations,
                key=f"text_highlighter_{name}_{index}"
            )
            results.append(result)
    st.session_state["cards"][st.session_state.current_page["index"]] = results
    save_state_to_cookies()
    return results

if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
    st.title(st.session_state.links[0]["label"])
    labels = [
        ("PI experiment", "#6290C3"),
        ("non-PI experiment", "#F25757")
    ]
    st.session_state["cards"][0] = displayTextHighlighter(labels, 0)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
    st.title(st.session_state.links[1]["label"])
    labels = [("PI experiment", "#6290C3"),
              ("non-PI experiment", "#F25757")]
    st.session_state["cards"][1] = displayTextHighlighter(labels, 1)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
    st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
.block-container {padding-top: 4rem;}
</style>
        """, unsafe_allow_html=True)

    coffee_break_a = interchange["pages"]["5_detail_picker"]["coffee_break_a"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_a['title']}")
    st.write(coffee_break_a["body"])

    if doi_link:
        st.link_button("Go to full-text paper", doi_link)

    exp_highlights = []
    sol_highlights = []

    for tab_results in st.session_state["cards"][0]:
        for item in tab_results:
            exp_highlights.append(item)
    for tab_results in st.session_state["cards"][1]:
        for item in tab_results:
            sol_highlights.append(item)

    max_len = max(len(exp_highlights), len(sol_highlights))
    rows = []
    for i in range(max_len):
        exp = exp_highlights[i] if i < len(exp_highlights) else {}
        sol = sol_highlights[i] if i < len(sol_highlights) else {}
        rows.append({
            "Experiment name": exp.get("text", ""),
            "Alternative Experiment Name": "",
            "Experiment Type": "PI" if exp.get("tag", "") == "PI experiment" else "non-PI" if exp.get("tag", "") == "non-PI experiment" else "",
            "Solution name": sol.get("text", ""),
            "Alternative Solution Name": "",
            "Solution Type": "PI" if sol.get("tag", "") == "PI experiment" else "non-PI" if sol.get("tag", "") == "non-PI experiment" else ""
        })

    exp_df = pd.DataFrame(rows)

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

    corrected = False
    for idx, row in edited_df.iterrows():
        if row["Experiment Type"] == "non-PI" and row["Solution Type"] != "non-PI":
            edited_df.at[idx, "Solution Type"] = "non-PI"
            corrected = True

    if corrected:
        st.error("Solution Type was set to 'non-PI' for rows where Experiment Type is 'non-PI'.")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            save()
            next()
    save_state_to_cookies()

elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
    st.title(st.session_state.links[3]["label"])
    labels = [
        ("Select", "#82645E"),
    ]
    st.session_state["cards"][2] = displayTextHighlighter(labels, 2)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[4]["label"]:
    st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
.block-container {padding-top: 4rem;}
</style>
        """, unsafe_allow_html=True)

    coffee_break_b = interchange["pages"]["5_detail_picker"]["coffee_break_b"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_b['title']}")
    st.write(coffee_break_b["body"])

    if doi_link:
        st.link_button("Go to full-text paper", doi_link)

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

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            save()
            next()
    save_state_to_cookies()

elif st.session_state.current_page["page"]["label"] == st.session_state.links[5]["label"]:
    st.title(st.session_state.links[5]["label"])
    labels = [
        ("Buffer", "#F68E5F"),
        ("pH", "#56876D"),
        ("Salt", "#F9C784"),
        ("Detergent", "#007FFF"),
        ("Chelating", "#7D83FF"),
        ("Other", "#8898AA"),
    ]
    st.session_state["cards"][3] = displayTextHighlighter(labels, 3)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[6]["label"]:
    st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
.block-container {padding-top: 4rem;}
</style>
        """, unsafe_allow_html=True)

    coffee_break_c = interchange["pages"]["5_detail_picker"]["coffee_break_c"]
    st.title(interchange["pages"]["5_detail_picker"]["title"])
    st.markdown(f"#### {coffee_break_c['title']}")
    st.write(coffee_break_c["body"])

    if doi_link:
        st.link_button("Go to full-text paper", doi_link)

    col1, col2 = st.columns([1, 1])
    with col1:
        experiment_type = st.selectbox("Experiment Type", ["PI", "non-PI"], key="exp_type_3")
    with col2:
        if experiment_type == "PI":
            solution_type_options = ["PI", "non-PI"]
        else:
            solution_type_options = ["non-PI"]
        solution_type = st.selectbox("Solution Type", solution_type_options, key="sol_type_3")

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
    st.radio(
        "Solution details",
        ["Solution details not listed:", "Solution details listed:"],
        index=1,
        key="solution_details_radio",
        label_visibility="collapsed"
    )

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

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            st.session_state["completed_paper"] = pmid
            cookies["completed_paper"] = pmid

            if "selected_paper" in st.session_state:
                del st.session_state["selected_paper"]

            cookies["selected_paper"] = ""

            if "paper_in_progress" in st.session_state:
                del st.session_state["paper_in_progress"]

            cookies["paper_in_progress"] = ""
            cookies.save()

            user_key = get_user_key(cookies)
            token = get_token(cookies)
            if user_key:
                # Only clear after add_completed_paper succeeds
                if add_completed_paper(user_key, pmid):
                    clear_paper_in_progress(user_key, token)

            if "pages" in st.session_state:
                del st.session_state["pages"]
            if "current_page" in st.session_state:
                del st.session_state["current_page"]

            st.set_option("client.showSidebarNavigation", True)
            st.switch_page("pages/7_thanks.py")
else:
    st.title("")

def render_sidebar():
    with st.sidebar:
        st.title("Paper Annotation")

        if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
            st.subheader("Step 1/4 : Identify experiments (names)")
            st.markdown(
                "Identify all the experimental methods used in the paper and determine if they contain any steps that **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**. We are not interested in identifying methods that are exclusively computational.")
        elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
            st.subheader("Step 2/4 : Identify solutions (names)")
            st.markdown(
                "For each of the laboratory experiments that you identified in the previous step, select the solution names used in distinct steps of the experimental protocol. If the solution is intended to **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**, thet it should be classified as \"PI\", and as \"non-PI\" otherwise, like before. An experiment that has been labeled as \"non-PI\" cannot contain \"PI\" solutions, but the opposite is possible.")
        elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
            st.subheader("Step 3/4 : Experiment details")
            st.markdown(
                "For each of the PI laboratory experiments that you identified in the first step, find the details we ask  below. For each selected question you will need to find the answer in the text of the paper (\"Select\" button). In the case the information is split in multiple locations in the paper, then you can append more text to your current selection by pressing the \"Add to selection\" button, repeating as many times as necessary. The \"Select\" button is reset when you move on to the next question.")
        elif st.session_state.current_page["page"]["label"] == st.session_state.links[5]["label"]:
            st.subheader("Step 4/4 : Solution composition")
            st.markdown(
                "For each of the PI solutions that you identified in the second step, find their detailed composition in the text after selecting the right button for the type of chemical. If the composition of a solution used in the experiments is not described in detail but instead is offered as a reference to previous work, then select that reference in-text withe the corresponding button selected.  ")
        else:
            st.title("")

        if doi_link:
            st.link_button("Go to full-text paper", doi_link, use_container_width=True)
        else:
            st.write("DOI link not available for this paper.")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("Prev", use_container_width=True):
                prev()

        with col2:
            if st.button("Save", use_container_width=True):
                save()

        with col3:
            if st.button("Save & Next", use_container_width=True):
                save()
                next()

        if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
            header = {
                "column_1": "Experiment name",
                "column_2": "Type"
            }
            for tab_index, tab_results in enumerate(st.session_state["cards"][0]):
                for i, item in enumerate(tab_results):
                    colored_card(
                        title=f"{item['tag']}",
                        subtitle=item['text'],
                        bg_color=item['color']
                    )
        elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
            buttons = []
            for tab_index, tab_results in enumerate(st.session_state["cards"][0]):
                for i, item in enumerate(tab_results):
                    details = {
                        "index": i,
                        "name": item["text"],
                        "type": check_tag(item["tag"]),
                        "background_color": "#6290C3" if check_tag(item["tag"]) == "PI" else "#F25757",
                        "text_color": "white"
                    }
                    buttons.append(details)
            header = {
                "column_1": "Experiment > Solution",
                "column_2": "Type"
            }
            st.session_state["active_solution_btn"] = TableSelect(header, buttons, 2, key=st.session_state.links[1]["label"])

        elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
            st.title(st.session_state.links[2]["label"])

        elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
            st.title(st.session_state.links[3]["label"])
        else:
            st.title("")

if "Coffee Break" not in st.session_state.current_page["page"]["label"]:
    render_sidebar()