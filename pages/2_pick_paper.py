import streamlit as st
import os
import json
import random
import pandas as pd

st.set_page_config(page_title="Pick Paper", layout="wide")
st.title("Select the paper you will annotate")

st.markdown("""
Go through the list of five options we offer below and select the paper you are most comfortable with.
If you don't like any of the five papers, click the "Refresh paper list" button for a new set.
""")

# Path to folder with JSON papers
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = "AWS_S3\\users_table.xlsx"

# Loads the metadata from JSON files in the specified folder.
@st.cache_data
def load_paper_metadata():
    papers = []
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    doc = raw[0]["documents"][0]
                    front = doc["passages"][0]  # front matter
                    meta = front["infons"]
                    title = front["text"]

                    # Extract and clean up authors
                    authors = []
                    for k, v in meta.items():
                        if k.startswith("name_"):
                            parts = v.split(";")
                            surname = next((p.split(":")[1] for p in parts if p.startswith("surname:")), "").strip()
                            given_names = next((p.split(":")[1] for p in parts if p.startswith("given-names:")), "").strip()
                            if surname and given_names:
                                authors.append(f"{given_names} {surname}")
                            elif surname:
                                authors.append(surname)
                            elif given_names:
                                authors.append(given_names)
                    authors_str = ", ".join(authors)

                    # Extract pages
                    fpage = meta.get("fpage", "N/A")
                    lpage = meta.get("lpage", "N/A")
                    pages = f"{fpage}-{lpage}" if fpage != "N/A" and lpage != "N/A" else "N/A"

                    papers.append({
                        "title": title,
                        "authors": authors_str,
                        "volume": meta.get("volume", "?"),
                        "issue": meta.get("issue", "?"),
                        "pages": pages,
                        "year": meta.get("year", "?"),
                        "doi": meta.get("article-id_doi", ""),
                        "link": f"https://doi.org/{meta.get('article-id_doi', '')}",
                        "filename": filename
                    })
            except Exception as e:
                print(f"Skipping {filename}: {e}")
    return papers

all_papers = load_paper_metadata()

# Function to refresh paper list
def refresh_paper_list():
    num_to_select = min(5, len(all_papers))
    st.session_state.paper_choices = random.sample(all_papers, k=num_to_select)
    st.session_state.selected_option = None
    # Clear checkbox states
    for k in ["a", "b", "c", "d", "e"]:
        if k in st.session_state:
            del st.session_state[k]

# Function to update the "Paper in progress" column
def update_paper_in_progress(user_id, pmid):
    # Load the users table
    users_df = pd.read_excel(USERS_TABLE_PATH)

    # Find the row corresponding to the user
    user_row = users_df[users_df["userID"] == user_id]

    if not user_row.empty:
        # Update the "Paper in progress" column
        users_df.loc[users_df["userID"] == user_id, "Paper in progress"] = pmid

        # Save the updated table back to the Excel file
        users_df.to_excel(USERS_TABLE_PATH, index=False)
    else:
        print(f"User with ID {user_id} not found.")

# Initialize session state for paper choices
if "paper_choices" not in st.session_state:
    refresh_paper_list()

# Initialize session state for selected option
def select(option, key):
    if st.session_state.selected_option == option:
        st.session_state.selected_option = None
        st.session_state[key] = False
    else:
        st.session_state.selected_option = option
        for k in ["a", "b", "c", "d", "e"]:
            if k != key:
                st.session_state[k] = False

# Display the 5 random papers
for i, paper in enumerate(st.session_state.paper_choices):
    key = chr(ord("a") + i)
    label = (
        f"**{paper['authors']}**, "
        f"*{paper['title']}* "
        f"({paper['year']})\n\n"
    )

    # Dynamically construct the metadata parts
    metadata_parts = []
    if paper.get('issue', '?') != "?":
        metadata_parts.append(f"**Issue:** {paper['issue']}")
    if paper.get('volume', '?') != "?":
        metadata_parts.append(f"**Volume:** {paper['volume']}")
    if paper.get('pages', 'N/A') != "N/A":
        metadata_parts.append(f"**Pages:** {paper['pages']}")

    # Join metadata parts with a comma
    if metadata_parts:
        label += ", ".join(metadata_parts) + "\n\n"

    label += f"[**Link**]({paper['link']})"

    st.checkbox(label, key=key, value=st.session_state.get(key, False),
                on_change=select, args=(paper["filename"], key))

# Navigation buttons
col2, col3 = st.columns([6, 6])
with col2:
    if st.button("Go to annotation", type="primary", key="go_button", disabled=not st.session_state.selected_option):
        # Save the selected paper's metadata in session state
        selected_paper = next(paper for paper in st.session_state.paper_choices if paper["filename"] == st.session_state.selected_option)
        st.session_state["selected_paper"] = selected_paper

        # Extract the PMID from the selected paper's JSON file
        with open(f"{JSON_FOLDER}/{selected_paper['filename']}", "r", encoding="utf-8") as f:
            raw = json.load(f)
            pmid = raw[0]["documents"][0]["passages"][0]["infons"].get("article-id_pmid", "PMID not found")

        # Update the "Paper in progress" column for the current user
        current_user_id = st.session_state.get("userID")  # Ensure userID is stored in session state
        if current_user_id:
            update_paper_in_progress(current_user_id, pmid)

        # Navigate to the detail_picker page
        st.switch_page("pages/5_detail_picker.py")
with col3:
    st.button("Refresh paper list", type="secondary", key="refresh_button", on_click=refresh_paper_list)